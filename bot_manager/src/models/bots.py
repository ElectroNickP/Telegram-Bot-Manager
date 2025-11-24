from sqlalchemy import String, Integer, Boolean, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from src.database.session import Base
import enum

class BotStatus(str, enum.Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"

class Bot(Base):
    __tablename__ = "bots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String, index=True)
    
    # Encrypted tokens (stored as strings)
    telegram_token: Mapped[str] = mapped_column(String)
    openai_api_key: Mapped[str] = mapped_column(String)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=False) # Target state
    status: Mapped[BotStatus] = mapped_column(Enum(BotStatus), default=BotStatus.STOPPED) # Actual state
    
    config: Mapped[dict] = mapped_column(JSONB, default={}) # Prompts, voice settings, etc.
    
    # Logic Restoration Fields
    system_prompt: Mapped[str] = mapped_column(String, default="You are a helpful assistant.")
    voice_settings: Mapped[dict] = mapped_column(JSONB, default={"voice_id": "alloy", "speed": 1.0})
    assistant_id: Mapped[str | None] = mapped_column(String, nullable=True) # OpenAI Assistant ID

    owner: Mapped["User"] = relationship(back_populates="bots")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="bot", cascade="all, delete-orphan")
