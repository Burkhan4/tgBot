import asyncio

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

from handlers.start import router as start_router

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

dp.include_router(start_router)

async def main():
    print("Bot ishlayapti ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())