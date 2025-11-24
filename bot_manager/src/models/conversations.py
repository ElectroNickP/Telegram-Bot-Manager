from sqlalchemy import String, Integer, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from src.database.session import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    bot_id: Mapped[int] = mapped_column(ForeignKey("bots.id"))
    user_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)
    thread_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True) # OpenAI Thread ID
    
    message_history: Mapped[list] = mapped_column(JSONB, default=[])

    bot: Mapped["Bot"] = relationship(back_populates="conversations")
