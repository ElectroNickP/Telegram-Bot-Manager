from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.bots import Bot, BotStatus

class BotService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_bots(self) -> list[Bot]:
        result = await self.session.execute(select(Bot))
        return list(result.scalars().all())

    async def get_active_bots(self) -> list[Bot]:
        result = await self.session.execute(select(Bot).where(Bot.is_active == True))
        return list(result.scalars().all())

    async def get_bot(self, bot_id: int) -> Bot | None:
        return await self.session.get(Bot, bot_id)

    async def create_bot(self, user_id: int, name: str, telegram_token: str, openai_api_key: str, 
                         system_prompt: str = "You are a helpful assistant.", 
                         voice_settings: dict = None,
                         config: dict = None) -> Bot:
        bot = Bot(
            user_id=user_id,
            name=name,
            telegram_token=telegram_token,
            openai_api_key=openai_api_key,
            system_prompt=system_prompt,
            voice_settings=voice_settings or {"voice_id": "alloy", "speed": 1.0},
            config=config or {},
            is_active=True,
            status=BotStatus.RUNNING
        )
        self.session.add(bot)
        await self.session.commit()
        await self.session.refresh(bot)
        return bot

    async def update_bot(self, bot_id: int, name: str = None, telegram_token: str = None, 
                         openai_api_key: str = None, system_prompt: str = None, 
                         voice_settings: dict = None) -> Bot | None:
        bot = await self.get_bot(bot_id)
        if not bot:
            return None
        
        if name: bot.name = name
        if telegram_token: bot.telegram_token = telegram_token
        if openai_api_key: bot.openai_api_key = openai_api_key
        if system_prompt: 
            bot.system_prompt = system_prompt
            bot.assistant_id = None # Force re-creation of assistant
        if voice_settings: bot.voice_settings = voice_settings
        
        await self.session.commit()
        await self.session.refresh(bot)
        return bot

    async def update_bot_status(self, bot_id: int, status: BotStatus):
        bot = await self.get_bot(bot_id)
        if bot:
            bot.status = status
            await self.session.commit()

    async def set_bot_active_state(self, bot_id: int, is_active: bool):
        bot = await self.get_bot(bot_id)
        if bot:
            bot.is_active = is_active
            await self.session.commit()
