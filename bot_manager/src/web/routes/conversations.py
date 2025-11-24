from fastapi import APIRouter, Request, Depends, Cookie, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.session import get_db
from src.models.conversations import Conversation
from src.models.bots import Bot
import os

router = APIRouter(tags=["conversations"])
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

async def get_current_user(user_id: str | None = Cookie(default=None)):
    if not user_id:
        return None
    return user_id

@router.get("/dashboard/bots/{bot_id}/conversations", response_class=HTMLResponse)
async def list_conversations(
    request: Request,
    bot_id: int,
    user_id: str | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/login")
    
    # Get Bot
    bot = await db.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    stmt = select(Conversation).where(Conversation.bot_id == bot_id)
    result = await db.execute(stmt)
    conversations = result.scalars().all()
    
    return templates.TemplateResponse("conversations.html", {
        "request": request, 
        "bot": bot, 
        "conversations": conversations,
        "active_conversation": None
    })

@router.get("/dashboard/bots/{bot_id}/conversations/{conv_id}", response_class=HTMLResponse)
async def view_conversation(
    request: Request,
    bot_id: int,
    conv_id: int,
    user_id: str | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/login")
        
    bot = await db.get(Bot, bot_id)
    conversation = await db.get(Conversation, conv_id)
    
    if not conversation or conversation.bot_id != bot_id:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    stmt = select(Conversation).where(Conversation.bot_id == bot_id)
    result = await db.execute(stmt)
    all_conversations = result.scalars().all()
    
    return templates.TemplateResponse("conversations.html", {
        "request": request, 
        "bot": bot, 
        "conversations": all_conversations,
        "active_conversation": conversation
    })
