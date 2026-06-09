# 🏥 Bolalar Milliy Tibbiyot Markazi — Telegram Bot

Bolalar milliy tibbiyot markazi uchun Telegram bot. Foydalanuvchilar kasalxona haqida ma'lumot olishi, shikoyat va takliflar yuborishi mumkin. Admin uchun veb-panel mavjud.

## ✨ Imkoniyatlar

- 📍 **Lokatsiya** — kasalxona manzili va xarita
- 📱 **Ijtimoiy tarmoqlar** — Instagram, Telegram, Facebook, veb-sayt
- 📝 **Shikoyat va takliflar** — foydalanuvchilardan shikoyat qabul qilish
- ℹ️ **Ma'lumot** — kasalxona haqida to'liq axborot
- 📞 **Bog'lanish** — telefon raqami
- 🕐 **Ish vaqti** — ish jadvalini ko'rsatish
- 🖥️ **Admin panel** — `http://localhost:5000` da shikoyatlar va foydalanuvchilarni boshqarish

## 🚀 O'rnatish

### 1. Repozitoriyni klonlash

```bash
git clone https://github.com/username/bmtm-bot.git
cd bmtm-bot
```

### 2. Virtual muhit yaratish

```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. `.env` faylini sozlash

```bash
cp .env.example .env
```

`.env` faylini oching va quyidagilarni to'ldiring:

```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id_here
```

> 💡 **BOT_TOKEN** — [@BotFather](https://t.me/BotFather) dan olinadi  
> 💡 **ADMIN_ID** — [@userinfobot](https://t.me/userinfobot) dan bilib olasiz

### 5. Botni ishga tushirish

```bash
python bot.py
```

Bot ishga tushgach:
- Telegram botingiz ishlaydi
- Admin panel: `http://localhost:5000`

## 📁 Fayl tuzilmasi

```
bmtm-bot/
├── bot.py              # Asosiy bot kodi
├── requirements.txt    # Python kutubxonalari
├── .env.example        # Sozlamalar namunasi
├── .env                # Sozlamalar (githubga yuklanmaydi!)
├── .gitignore          # Git chiqarib tashlash ro'yxati
└── README.md           # Ushbu fayl
```

> ⚠️ `users.json` va `shikoyatlar.json` fayllari bot ishlaganda avtomatik yaratiladi.

## 🛡️ Xavfsizlik

- `.env` fayli `.gitignore` ga qo'shilgan — token hech qachon githubga yuklanmaydi
- Bot tokeni va Admin ID faqat `.env` faylida saqlanadi

## 🛠️ Texnologiyalar

- [Python 3.10+](https://python.org)
- [aiogram 3.x](https://docs.aiogram.dev) — Telegram Bot Framework
- [python-dotenv](https://pypi.org/project/python-dotenv/) — muhit o'zgaruvchilari
