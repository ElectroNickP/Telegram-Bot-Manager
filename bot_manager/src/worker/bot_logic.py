import structlog
import os
import asyncio
from aiogram import Bot as AiogramBot
from aiogram.types import Message, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.bots import Bot
from src.models.conversations import Conversation
from src.services.openai_svc import OpenAIService

logger = structlog.get_logger()

class BotLogic:
    def __init__(self, bot_db: Bot, session: AsyncSession, openai_svc: OpenAIService):
        self.bot_db = bot_db
        self.session = session
        self.openai_svc = openai_svc

    async def handle_message(self, message: Message, aiogram_bot: AiogramBot):
        user_id = message.from_user.id
        chat_id = message.chat.id
        logger.info("message_received", user_id=user_id, chat_id=chat_id, content_type=message.content_type)
        
        # 1. Get or Create Conversation
        stmt = select(Conversation).where(
            Conversation.bot_id == self.bot_db.id,
            Conversation.user_telegram_id == user_id
        )
        result = await self.session.execute(stmt)
        conversation = result.scalar_one_or_none()

        if not conversation:
            logger.info("creating_new_conversation", user_id=user_id, bot_id=self.bot_db.id)
            conversation = Conversation(
                bot_id=self.bot_db.id,
                user_telegram_id=user_id,
                message_history=[]
            )
            self.session.add(conversation)
            await self.session.commit()
            await self.session.refresh(conversation)
        else:
            logger.debug("conversation_found", conversation_id=conversation.id)

        # 2. Ensure OpenAI Thread exists
        if not conversation.thread_id:
            try:
                logger.info("creating_openai_thread", conversation_id=conversation.id)
                thread_id = await self.openai_svc.create_thread()
                conversation.thread_id = thread_id
                self.session.add(conversation)
                await self.session.commit()
            except Exception as e:
                logger.error("failed_create_thread", error=str(e), conversation_id=conversation.id)
                await message.answer("Error initializing conversation.")
                return

        # 3. Process Input (Text or Voice)
        user_text = ""
        if message.voice:
            # Handle Voice
            file_id = message.voice.file_id
            logger.info("processing_voice_message", file_id=file_id)
            file = await aiogram_bot.get_file(file_id)
            file_path = file.file_path
            
            # Download
            temp_filename = f"voice_{file_id}.ogg"
            await aiogram_bot.download_file(file_path, temp_filename)
            
            try:
                with open(temp_filename, "rb") as audio_file:
                    user_text = await self.openai_svc.transcribe_audio(audio_file)
                logger.info("voice_transcribed", text_length=len(user_text))
            except Exception as e:
                logger.error("voice_transcription_failed", error=str(e))
                await message.answer("Sorry, I couldn't hear you.")
                return
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
            
            if not user_text:
                await message.answer("Sorry, I couldn't hear you.")
                return
                
            await message.answer(f"🎤 *Transcribed:* {user_text}", parse_mode="Markdown")
        else:
            user_text = message.text or ""
            logger.debug("processing_text_message", text_length=len(user_text))

        if not user_text:
            return

        # 4. Add Message to Thread
        try:
            await self.openai_svc.add_message(conversation.thread_id, user_text)
            logger.debug("message_added_to_thread", thread_id=conversation.thread_id)
        except Exception as e:
            logger.error("failed_add_message", error=str(e), thread_id=conversation.thread_id)
            await message.answer("Error processing message.")
            return

        # 5. Ensure Assistant exists
        if not self.bot_db.assistant_id:
            try:
                logger.info("creating_openai_assistant", bot_name=self.bot_db.name)
                assistant_id = await self.openai_svc.create_assistant(
                    name=self.bot_db.name,
                    instructions=self.bot_db.system_prompt or "You are a helpful assistant.",
                    model="gpt-4-turbo-preview"
                )
                self.bot_db.assistant_id = assistant_id
                self.session.add(self.bot_db)
                await self.session.commit()
                logger.info("assistant_created", assistant_id=assistant_id)
            except Exception as e:
                logger.error("failed_create_assistant", error=str(e))
                await message.answer("Error initializing assistant.")
                return

        # 6. Run Assistant
        try:
            logger.info("running_assistant", thread_id=conversation.thread_id, assistant_id=self.bot_db.assistant_id)
            response_text = await self.openai_svc.run_assistant(
                thread_id=conversation.thread_id,
                assistant_id=self.bot_db.assistant_id
            )
            logger.info("assistant_response_received", response_length=len(response_text) if response_text else 0)
        except Exception as e:
            logger.error("failed_run_assistant", error=str(e))
            await message.answer("I'm having trouble thinking right now.")
            return

        if not response_text:
            await message.answer("...")
            return

        # 7. Handle TTS (if enabled)
        voice_settings = self.bot_db.voice_settings or {}
        should_speak = False
        if message.voice: 
            should_speak = True # Reply voice to voice
        
        if should_speak:
            voice_id = voice_settings.get("voice_id", "alloy")
            speed = voice_settings.get("speed", 1.0)
            
            logger.info("generating_tts", voice_id=voice_id)
            try:
                audio_content = await self.openai_svc.text_to_speech(response_text, voice=voice_id, speed=speed)
                if audio_content:
                    temp_audio = f"reply_{message.message_id}.mp3"
                    with open(temp_audio, "wb") as f:
                        f.write(audio_content)
                    
                    try:
                        voice_file = FSInputFile(temp_audio)
                        await message.answer_voice(voice_file, caption=response_text[:1000])
                        logger.info("voice_reply_sent")
                    finally:
                        if os.path.exists(temp_audio):
                            os.remove(temp_audio)
                else:
                    await message.answer(response_text)
            except Exception as e:
                logger.error("tts_failed", error=str(e))
                await message.answer(response_text)
        else:
            await message.answer(response_text)
            logger.info("text_reply_sent")

        # 8. Update History (Local Cache)
        new_history = list(conversation.message_history)
        new_history.append({"role": "user", "content": user_text})
        new_history.append({"role": "assistant", "content": response_text})
        conversation.message_history = new_history
        self.session.add(conversation)
        await self.session.commit()
