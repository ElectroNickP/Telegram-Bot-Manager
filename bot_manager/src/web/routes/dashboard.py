from fastapi import APIRouter, Request, Depends, Cookie, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database.session import get_db
from src.services.bot_service import BotService
from src.models.bots import Bot
import os

router = APIRouter(tags=["dashboard"])

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

async def get_current_user(user_id: str | None = Cookie(default=None)):
    if not user_id:
        return None
    return user_id

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user_id: str | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/login")
    
    bot_service = BotService(db)
    bots = await bot_service.get_all_bots()
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "bots": bots})

@router.get("/dashboard/bots", response_class=HTMLResponse)
async def get_bots_list(
    request: Request,
    user_id: str | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """HTMX endpoint to refresh bot list"""
    if not user_id:
        return ""
        
    bot_service = BotService(db)
    bots = await bot_service.get_all_bots()
    
    return templates.TemplateResponse("partials/bot_list.html", {"request": request, "bots": bots})

@router.post("/dashboard/bots/create", response_class=HTMLResponse)
async def create_bot(
    request: Request,
    name: str = Form(...),
    telegram_token: str = Form(...),
    openai_api_key: str = Form(...),
    system_prompt: str = Form(None),
    voice_id: str = Form("alloy"),
    voice_speed: float = Form(1.0),
    user_id: str | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
        
    # Create bot
    bot_service = BotService(db)
    voice_settings = {"voice_id": voice_id, "speed": voice_speed}
    await bot_service.create_bot(
        user_id=int(user_id),
        name=name,
        telegram_token=telegram_token,
        openai_api_key=openai_api_key,
        system_prompt=system_prompt,
        voice_settings=voice_settings
    )
    
    # Return the updated bot list
    stmt = select(Bot).order_by(Bot.id)
    result = await db.execute(stmt)
    bots = result.scalars().all()
    
    return templates.TemplateResponse("partials/bot_list.html", {
        "request": request, 
        "bots": bots
    }, headers={"HX-Trigger": "closeModal"})

@router.get("/dashboard/bots/new", response_class=HTMLResponse)
async def new_bot_form(request: Request):
    return templates.TemplateResponse("partials/bot_form.html", {"request": request, "bot": None})

@router.get("/dashboard/bots/{bot_id}/edit", response_class=HTMLResponse)
async def edit_bot_form(
    request: Request,
    bot_id: int,
    user_id: str | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not user_id:
        return ""
        
    bot_service = BotService(db)
    bot = await bot_service.get_bot(bot_id)
    return templates.TemplateResponse("partials/bot_form.html", {"request": request, "bot": bot})

@router.post("/dashboard/bots/{bot_id}/edit", response_class=HTMLResponse)
async def edit_bot(
    request: Request,
    bot_id: int,
    name: str = Form(...),
    telegram_token: str = Form(...),
    openai_api_key: str = Form(...),
    system_prompt: str = Form(...),
    voice_id: str = Form(...),
    voice_speed: float = Form(...),
    user_id: str | None = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
        
    bot_service = BotService(db)
    voice_settings = {"voice_id": voice_id, "speed": voice_speed}
    
    await bot_service.update_bot(
        bot_id=bot_id,
        name=name,
        telegram_token=telegram_token,
        openai_api_key=openai_api_key,
        system_prompt=system_prompt,
        voice_settings=voice_settings
    )
    
    # Return updated list
    bots = await bot_service.get_all_bots()
    return templates.TemplateResponse("partials/bot_list.html", {"request": request, "bots": bots}, headers={"HX-Trigger": "closeModal"})

@router.post("/dashboard/validate/telegram-token")
async def validate_telegram_token(token: str = Form(...)):
    """Validate Telegram token and return bot info as JSON"""
    try:
        from aiogram import Bot as AiogramBot
        from aiogram.client.session.aiohttp import AiohttpSession
        from fastapi.responses import JSONResponse
        
        # Create a temporary bot instance to check token
        async with AiohttpSession() as session:
            bot = AiogramBot(token=token, session=session)
            try:
                bot_info = await bot.get_me()
                # Return JSON response
                return JSONResponse({
                    "success": True,
                    "data": {
                        "username": bot_info.username,
                        "first_name": bot_info.first_name,
                        "display_name": bot_info.first_name
                    }
                })
            finally:
                await session.close()
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=400)
@router.post("/dashboard/validate/openai-assistant")
async def validate_openai_assistant(
    assistant_id: str = Form(...),
    openai_api_key: str = Form(...)
):
    """Validate OpenAI Assistant ID and API Key"""
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=openai_api_key)
        assistant = await client.beta.assistants.retrieve(assistant_id)
        
        return HTMLResponse(
            f"""
            <div class="validation-success" style="color: var(--success); margin-top: 0.5rem; font-size: 0.9rem;">
                <i class="fas fa-check-circle"></i> Valid: <strong>{assistant.name or 'Unnamed Assistant'}</strong>
                <br><small>Model: {assistant.model}</small>
            </div>
            """
        )
    except Exception as e:
        return HTMLResponse(
            f"""
            <div class="validation-error" style="color: var(--danger); margin-top: 0.5rem; font-size: 0.9rem;">
                <i class="fas fa-times-circle"></i> Invalid: {str(e)}
            </div>
            """
        )
