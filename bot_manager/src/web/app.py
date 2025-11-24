from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.config.settings import settings
from src.web.routes import auth, dashboard, conversations
import os

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates configuration
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
if not os.path.exists(templates_dir):
    os.makedirs(templates_dir)
templates = Jinja2Templates(directory=templates_dir)

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(conversations.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Telegram Bot Manager API"}
