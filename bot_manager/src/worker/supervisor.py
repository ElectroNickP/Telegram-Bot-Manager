import asyncio
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.session import AsyncSessionLocal
from src.services.bot_service import BotService
from src.services.crypto import crypto_service
from src.models.bots import BotStatus
from aiogram import Bot as AiogramBot, Dispatcher
from aiogram.types import Message
from sqlalchemy import select
from src.models.bots import Bot
from src.worker.bot_logic import BotLogic
from src.services.openai_svc import OpenAIService

logger = structlog.get_logger()

class Supervisor:
    def __init__(self):
        self.running_bots: dict[int, asyncio.Task] = {}
        self.bot_instances: dict[int, AiogramBot] = {}

    async def start(self):
        logger.info("Supervisor started")
        while True:
            try:
                async with AsyncSessionLocal() as session:
                    await self.sync_bots(session)
            except Exception as e:
                logger.error("Error in supervisor loop", error=str(e))
            
            await asyncio.sleep(5)

    async def sync_bots(self, session: AsyncSession):
        bot_service = BotService(session)
        active_bots = await bot_service.get_active_bots()
        active_bot_ids = {b.id for b in active_bots}

        # Stop bots that should not be running
        for bot_id in list(self.running_bots.keys()):
            if bot_id not in active_bot_ids:
                await self.stop_bot(bot_id, bot_service)

        # Start bots that should be running
        for bot in active_bots:
            if bot.id not in self.running_bots:
                await self.start_bot(bot, bot_service)

    async def start_bot(self, bot_db, bot_service: BotService):
        logger.info("Starting bot", bot_id=bot_db.id, name=bot_db.name)
        
        try:
            token = crypto_service.decrypt(bot_db.telegram_token)
            if not token:
                logger.error("Failed to decrypt token", bot_id=bot_db.id)
                await bot_service.update_bot_status(bot_db.id, BotStatus.ERROR)
                return

            # Initialize Aiogram Bot and Dispatcher
            bot = AiogramBot(token=token)
            dp = Dispatcher()

            # Initialize OpenAIService
            openai_svc = OpenAIService(api_key=crypto_service.decrypt(bot_db.openai_api_key))
            
            # Initialize BotLogic
            # Note: We need to pass a session factory or handle session lifecycle carefully.
            # The supervisor loop creates a session for sync_bots, but the bot runs in a separate task.
            # We should create a NEW session for the bot logic interactions to avoid concurrency issues with the supervisor loop.
            # However, BotLogic expects a session.
            # Let's instantiate BotLogic inside the handler or pass a session factory?
            # Better: Create a wrapper that creates a session for each message.
            
            @dp.message()
            async def main_handler(message: Message):
                async with AsyncSessionLocal() as session:
                    # Re-fetch bot to ensure it's attached to this session
                    stmt = select(Bot).where(Bot.id == bot_db.id)
                    result = await session.execute(stmt)
                    current_bot = result.scalar_one()
                    
                    logic = BotLogic(current_bot, session, openai_svc)
                    await logic.handle_message(message, bot)

            # Create async task
            async def run_polling():
                try:
                    await dp.start_polling(bot)
                except asyncio.CancelledError:
                    logger.info("Bot polling cancelled", bot_id=bot_db.id)
                except Exception as e:
                    logger.error("Bot polling error", bot_id=bot_db.id, error=str(e))
                    await bot_service.update_bot_status(bot_db.id, BotStatus.ERROR)
                finally:
                    await bot.session.close()

            task = asyncio.create_task(run_polling())
            self.running_bots[bot_db.id] = task
            self.bot_instances[bot_db.id] = bot
            
            await bot_service.update_bot_status(bot_db.id, BotStatus.RUNNING)

        except Exception as e:
            logger.error("Failed to start bot", bot_id=bot_db.id, error=str(e))
            await bot_service.update_bot_status(bot_db.id, BotStatus.ERROR)

    async def stop_bot(self, bot_id: int, bot_service: BotService):
        logger.info("Stopping bot", bot_id=bot_id)
        if bot_id in self.running_bots:
            task = self.running_bots[bot_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            del self.running_bots[bot_id]
            del self.bot_instances[bot_id]
            
            await bot_service.update_bot_status(bot_id, BotStatus.STOPPED)

if __name__ == "__main__":
    supervisor = Supervisor()
    asyncio.run(supervisor.start())
