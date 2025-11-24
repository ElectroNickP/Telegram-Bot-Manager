import asyncio
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.database.session import AsyncSessionLocal
from src.models.users import User, UserRole
from src.models.bots import Bot, BotStatus
from sqlalchemy import select

async def seed():
    async with AsyncSessionLocal() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalars().first()
        
        if not admin:
            print("Creating admin user...")
            admin = User(
                username="admin",
                password_hash="securepassword123", # In real app, hash this!
                role=UserRole.ADMIN
            )
            session.add(admin)
            await session.commit()
            print("Admin user created: admin / securepassword123")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    asyncio.run(seed())
