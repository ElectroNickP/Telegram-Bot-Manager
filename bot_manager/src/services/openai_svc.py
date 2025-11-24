import openai
from src.config.settings import settings
import structlog

logger = structlog.get_logger()

class OpenAIService:
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def generate_response(self, messages: list[dict], model: str = "gpt-4-turbo-preview") -> str:
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI API Error", error=str(e))
            return "Sorry, I encountered an error processing your request."

    async def create_assistant(self, name: str, instructions: str, model: str = "gpt-4-turbo-preview") -> str:
        try:
            assistant = await self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model=model
            )
            return assistant.id
        except Exception as e:
            logger.error("OpenAI Create Assistant Error", error=str(e))
            raise

    async def create_thread(self) -> str:
        try:
            thread = await self.client.beta.threads.create()
            return thread.id
        except Exception as e:
            logger.error("OpenAI Create Thread Error", error=str(e))
            raise

    async def add_message(self, thread_id: str, content: str) -> None:
        try:
            await self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=content
            )
        except Exception as e:
            logger.error("OpenAI Add Message Error", error=str(e))
            raise

    async def run_assistant(self, thread_id: str, assistant_id: str) -> str:
        try:
            run = await self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )

            # Poll for completion
            while True:
                run_status = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'cancelled', 'expired']:
                    raise Exception(f"Run failed with status: {run_status.status}")
                
                # Wait a bit before polling again
                import asyncio
                await asyncio.sleep(1)

            # Get messages
            messages = await self.client.beta.threads.messages.list(
                thread_id=thread_id
            )
            
            # Return the latest assistant message
            for msg in messages.data:
                if msg.role == "assistant":
                    return msg.content[0].text.value
            
            return ""
        except Exception as e:
            logger.error("OpenAI Run Assistant Error", error=str(e))
            raise

    async def transcribe_audio(self, audio_file, model: str = "whisper-1") -> str:
        try:
            transcript = await self.client.audio.transcriptions.create(
                model=model,
                file=audio_file
            )
            return transcript.text
        except Exception as e:
            logger.error("OpenAI Whisper Error", error=str(e))
            return ""

    async def text_to_speech(self, text: str, voice: str = "alloy", speed: float = 1.0) -> bytes:
        try:
            response = await self.client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                speed=speed
            )
            return response.content
        except Exception as e:
            logger.error("OpenAI TTS Error", error=str(e))
            return b""
