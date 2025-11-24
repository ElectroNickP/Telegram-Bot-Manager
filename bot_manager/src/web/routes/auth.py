from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from src.database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.users import User
import os

router = APIRouter(tags=["auth"])

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    # Simple auth for prototype - in production use bcrypt
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if not user or user.password_hash != password: # TODO: Hash check
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="user_id", value=str(user.id))
    return response

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie("user_id")
    return response
