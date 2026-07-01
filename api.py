import os
import asyncio

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from supabase import create_client
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from handlers.start import router as start_router

load_dotenv()

# ---------- Supabase ----------
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ---------- Telegram ----------
bot = Bot(token=os.getenv("BOT_TOKEN"))

dp = Dispatcher()
dp.include_router(start_router)


# ---------- FastAPI Lifespan ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Bot ishga tushdi ✅")

    polling_task = asyncio.create_task(
        dp.start_polling(bot)
    )

    yield

    polling_task.cancel()


# ---------- FastAPI ----------
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://bozor-roan.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/send-order-message")
async def send_order_message(order_id: int):

    order = (
        supabase
        .table("orders")
        .select("*")
        .eq("id", order_id)
        .single()
        .execute()
    )

    if not order.data:
        return {"success": False}

    profile = (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", order.data["user_id"])
        .single()
        .execute()
    )

    if not profile.data:
        return {"success": False}

    chat_id = profile.data.get("telegram_chat_id")

    if not chat_id:
        return {"success": False}

    await bot.send_message(
        chat_id=chat_id,
        text=f"""
✅ Buyurtmangiz qabul qilindi

Buyurtma raqami: #{order.data['id']}

Holati: Kutilmoqda

Jami summa:
{order.data['total_price']} so'm
"""
    )

    return {"success": True}


@app.post("/send-order-approved")
async def send_order_approved(order_id: int):

    order = (
        supabase
        .table("orders")
        .select("*")
        .eq("id", order_id)
        .single()
        .execute()
    )

    if not order.data:
        return {
            "success": False,
            "message": "Buyurtma topilmadi"
        }

    profile = (
        supabase
        .table("profiles")
        .select("*")
        .eq("id", order.data["user_id"])
        .single()
        .execute()
    )

    if not profile.data:
        return {
            "success": False,
            "message": "Profil topilmadi"
        }

    chat_id = profile.data.get("telegram_chat_id")

    if not chat_id:
        return {
            "success": False,
            "message": "Telegram ulanmagan"
        }

    await bot.send_message(
        chat_id=chat_id,
        text=f"""
✅ Buyurtmangiz tasdiqlandi

Buyurtma raqami: #{order.data['id']}

Tez orada operator siz bilan bog'lanadi.
"""
    )

    return {"success": True}

@app.get("/ping")
async def ping():
    return {"status": "alive"}