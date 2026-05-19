import asyncio
import logging
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ============================================================
# BOT TOKEN
# ============================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# ============================================================
# KASALXONA MA'LUMOTLARI
# ============================================================
KASALXONA_NOMI = "Bolalar milliy tibbiyot markazi"
KASALXONA_MANZIL = "Toshkent, Yashnobod tumani, Parkent ko'chasi 294-uy"
KASALXONA_TEL = "+998 95 341 00 03"
KASALXONA_ISH_VAQTI = (
    "Dushanba - Juma: 08:00 - 17:00\n"
    "Shanba - Yakshanba: Dam olish kuni"
)
KASALXONA_LAT = 41.30359
KASALXONA_LON = 69.34058

# Ijtimoiy tarmoqlar
INSTAGRAM = "https://instagram.com/ncmc.uz"
TELEGRAM_KANAL = "https://t.me/ncmcnew"
FACEBOOK = "https://facebook.com/ncmc.uz"
WEBSITE = "https://bmtm.uz"

# Admin ID
ADMIN_ID = 1353117203

# Foydalanuvchilar fayli
USERS_FILE = "users.json"

# ============================================================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ============================================================
# FOYDALANUVCHILARNI SAQLASH
# ============================================================
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user(user: types.User):
    users = load_users()
    user_id = str(user.id)
    if user_id not in users:
        users[user_id] = {
            "id": user.id,
            "ism": user.full_name,
            "username": f"@{user.username}" if user.username else "Yo'q",
            "sana": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)


# Shikoyat holatlari
class ShikoyatForm(StatesGroup):
    ism = State()
    telefon = State()
    shikoyat = State()


# ============================================================
# ASOSIY MENYU
# ============================================================
def asosiy_menyu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Lokatsiya"), KeyboardButton(text="📱 Ijtimoiy tarmoqlar")],
            [KeyboardButton(text="📝 Shikoyat va takliflar"), KeyboardButton(text="ℹ️ Ma'lumot")],
            [KeyboardButton(text="📞 Bog'lanish"), KeyboardButton(text="🕐 Ish vaqti")],
        ],
        resize_keyboard=True
    )
    return keyboard


# ============================================================
# START KOMANDASI
# ============================================================
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    save_user(message.from_user)
    await message.answer(
        f"👋 Assalomu alaykum!\n\n"
        f"🏥 <b>{KASALXONA_NOMI}</b> botiga xush kelibsiz!\n\n"
        f"Quyidagi bo'limlardan birini tanlang:",
        parse_mode="HTML",
        reply_markup=asosiy_menyu()
    )


# ============================================================
# ADMIN: FOYDALANUVCHILAR RO'YXATI
# ============================================================
@dp.message(Command("users"))
async def users_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    users = load_users()
    if not users:
        await message.answer("Hali hech kim botdan foydalanmagan.")
        return

    matn = f"👥 <b>Foydalanuvchilar: {len(users)} ta</b>\n\n"
    for i, (uid, u) in enumerate(users.items(), 1):
        matn += (
            f"{i}. {u['ism']}\n"
            f"   🆔 {u['id']} | {u['username']}\n"
            f"   📅 {u['sana']}\n\n"
        )

    # Telegram 4096 belgidan uzun xabar qabul qilmaydi
    if len(matn) > 4000:
        matn = matn[:4000] + "\n\n... (davomi bor)"

    await message.answer(matn, parse_mode="HTML")


# ============================================================
# LOKATSIYA
# ============================================================
@dp.message(F.text == "📍 Lokatsiya")
async def lokatsiya_handler(message: types.Message):
    await message.answer(
        f"📍 <b>Kasalxona manzili:</b>\n{KASALXONA_MANZIL}",
        parse_mode="HTML"
    )
    await bot.send_location(
        chat_id=message.chat.id,
        latitude=KASALXONA_LAT,
        longitude=KASALXONA_LON
    )


# ============================================================
# IJTIMOIY TARMOQLAR
# ============================================================
@dp.message(F.text == "📱 Ijtimoiy tarmoqlar")
async def ijtimoiy_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Instagram", url=INSTAGRAM)],
        [InlineKeyboardButton(text="✈️ Telegram kanal", url=TELEGRAM_KANAL)],
        [InlineKeyboardButton(text="👥 Facebook", url=FACEBOOK)],
        [InlineKeyboardButton(text="🌐 Veb-sayt", url=WEBSITE)],
    ])
    await message.answer(
        "📱 <b>Bizning ijtimoiy tarmoqlarimiz:</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )


# ============================================================
# SHIKOYAT — BOSHLASH
# ============================================================
@dp.message(F.text == "📝 Shikoyat va takliflar")
async def shikoyat_boshlash(message: types.Message, state: FSMContext):
    await state.set_state(ShikoyatForm.ism)
    await message.answer(
        "📝 <b>Shikoyat yuborish</b>\n\n"
        "Ismingizni kiriting:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
            resize_keyboard=True
        )
    )


@dp.message(ShikoyatForm.ism)
async def shikoyat_ism(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=asosiy_menyu())
        return
    await state.update_data(ism=message.text)
    await state.set_state(ShikoyatForm.telefon)
    await message.answer("📞 Telefon raqamingizni kiriting (masalan: +998901234567):")


@dp.message(ShikoyatForm.telefon)
async def shikoyat_telefon(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=asosiy_menyu())
        return
    await state.update_data(telefon=message.text)
    await state.set_state(ShikoyatForm.shikoyat)
    await message.answer("✍️ Shikoyatingizni yozing:")


@dp.message(ShikoyatForm.shikoyat)
async def shikoyat_yuborish(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=asosiy_menyu())
        return

    data = await state.get_data()
    shikoyat_matni = (
        f"🚨 <b>YANGI SHIKOYAT</b>\n\n"
        f"👤 Ism: {data['ism']}\n"
        f"📞 Telefon: {data['telefon']}\n"
        f"📝 Shikoyat:\n{message.text}\n\n"
        f"🆔 Foydalanuvchi ID: {message.from_user.id}"
    )

    try:
        await bot.send_message(ADMIN_ID, shikoyat_matni, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"⚠️ Xato: {e}")

    await state.clear()
    await message.answer(
        "✅ <b>Shikoyatingiz qabul qilindi!</b>\n\n"
        "Tez orada siz bilan bog'lanamiz. Rahmat!",
        parse_mode="HTML",
        reply_markup=asosiy_menyu()
    )


# ============================================================
# MA'LUMOT
# ============================================================
@dp.message(F.text == "ℹ️ Ma'lumot")
async def malumot_handler(message: types.Message):
    await message.answer(
        f"🏥 <b>{KASALXONA_NOMI}</b>\n\n"
        f"📍 Manzil: {KASALXONA_MANZIL}\n"
        f"📞 Telefon: {KASALXONA_TEL}\n"
        f"🕐 Ish vaqti:\n{KASALXONA_ISH_VAQTI}",
        parse_mode="HTML"
    )


# ============================================================
# BOG'LANISH
# ============================================================
@dp.message(F.text == "📞 Bog'lanish")
async def boglanish_handler(message: types.Message):
    await message.answer(
        f"📞 <b>Bog'lanish:</b>\n\n"
        f"☎️ Telefon: <code>{KASALXONA_TEL}</code>\n\n"
        f"📍 Manzil: {KASALXONA_MANZIL}\n\n"
        f"Raqamni bosib nusxa olishingiz mumkin!",
        parse_mode="HTML"
    )


# ============================================================
# ISH VAQTI
# ============================================================
@dp.message(F.text == "🕐 Ish vaqti")
async def ish_vaqti_handler(message: types.Message):
    await message.answer(
        f"🕐 <b>Ish vaqtimiz:</b>\n\n{KASALXONA_ISH_VAQTI}",
        parse_mode="HTML"
    )


# ============================================================
# BOTNI ISHGA TUSHIRISH
# ============================================================
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
