import asyncio
import logging
import json
import os
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = "8784857034:AAGmWxN_eNwzysZHhqZqs04NZgOT_Rl7zC0"
KASALXONA_NOMI = "Bolalar milliy tibbiyot markazi"
KASALXONA_MANZIL = "Toshkent, Yashnobod tumani, Parkent ko'chasi 294-uy"
KASALXONA_TEL = "+998 95 341 00 03"
KASALXONA_ISH_VAQTI = "Dushanba - Juma: 08:00 - 17:00\nShanba - Yakshanba: Dam olish kuni"
KASALXONA_LAT = 41.30359
KASALXONA_LON = 69.34058
INSTAGRAM = "https://instagram.com/ncmc.uz"
TELEGRAM_KANAL = "https://t.me/ncmcnew"
FACEBOOK = "https://facebook.com/ncmc.uz"
WEBSITE = "https://bmtm.uz"
ADMIN_ID = 1353117203
USERS_FILE = "users.json"
SHIKOYATLAR_FILE = "shikoyatlar.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ============================================================
# JSON HELPERS
# ============================================================
def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_user(user: types.User):
    users = load_json(USERS_FILE, {})
    uid = str(user.id)
    if uid not in users:
        users[uid] = {
            "id": user.id,
            "ism": user.full_name,
            "username": f"@{user.username}" if user.username else "Yo'q",
            "sana": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_json(USERS_FILE, users)

def save_shikoyat(ism, telefon, matn, user_id):
    shikoyatlar = load_json(SHIKOYATLAR_FILE, [])
    shikoyatlar.append({
        "id": len(shikoyatlar) + 1,
        "ism": ism,
        "telefon": telefon,
        "matn": matn,
        "user_id": user_id,
        "sana": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "holat": "Yangi"
    })
    save_json(SHIKOYATLAR_FILE, shikoyatlar)


# ============================================================
# WEB SERVER
# ============================================================
HTML_PAGE = """<!DOCTYPE html>
<html lang="uz">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>BMTM Admin Panel</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',sans-serif; background:#f0f4f8; }
.header { background:linear-gradient(135deg,#1a73e8,#0d47a1); color:white; padding:20px 30px; display:flex; align-items:center; gap:15px; }
.header h1 { font-size:20px; }
.header p { font-size:12px; opacity:0.8; }
.stats { display:flex; gap:15px; padding:20px 30px 10px; flex-wrap:wrap; }
.stat { background:white; border-radius:10px; padding:18px 22px; flex:1; min-width:130px; box-shadow:0 2px 8px rgba(0,0,0,0.07); border-left:4px solid; }
.stat.blue{border-color:#1a73e8;} .stat.orange{border-color:#fa7b17;} .stat.green{border-color:#34a853;}
.stat .num{font-size:28px;font-weight:700;} .stat.blue .num{color:#1a73e8;} .stat.orange .num{color:#fa7b17;} .stat.green .num{color:#34a853;}
.stat .label{font-size:12px;color:#666;margin-top:3px;}
.tabs{display:flex;gap:5px;padding:15px 30px 0;}
.tab{padding:9px 20px;border-radius:8px 8px 0 0;cursor:pointer;font-size:14px;background:#dde3ea;color:#555;border:none;}
.tab.active{background:white;color:#1a73e8;}
.content{background:white;margin:0 30px 30px;border-radius:0 12px 12px 12px;padding:22px;box-shadow:0 2px 8px rgba(0,0,0,0.07);}
.search input{width:100%;padding:9px 14px;border:1px solid #ddd;border-radius:8px;font-size:14px;outline:none;margin-bottom:15px;}
.search input:focus{border-color:#1a73e8;}
table{width:100%;border-collapse:collapse;}
th{background:#f8f9fa;padding:11px 12px;text-align:left;font-size:13px;color:#555;font-weight:600;border-bottom:2px solid #e8eaed;}
td{padding:12px 12px;border-bottom:1px solid #f0f0f0;font-size:13px;vertical-align:top;}
tr:hover td{background:#f8faff;}
.badge{display:inline-block;padding:3px 9px;border-radius:20px;font-size:11px;font-weight:500;}
.badge-new{background:#fce8e6;color:#d93025;} .badge-read{background:#e6f4ea;color:#137333;}
.shikoyat-text{max-width:280px;line-height:1.5;}
.empty{text-align:center;padding:50px;color:#999;}
.empty .icon{font-size:40px;margin-bottom:10px;}
.refresh{float:right;padding:8px 16px;background:#1a73e8;color:white;border:none;border-radius:8px;cursor:pointer;font-size:13px;}
.refresh:hover{background:#1557b0;}
</style>
</head>
<body>
<div class="header">
  <div style="font-size:32px">🏥</div>
  <div><h1>Bolalar Milliy Tibbiyot Markazi</h1><p>Admin boshqaruv paneli — avtomatik yangilanadi</p></div>
  <button class="refresh" onclick="location.reload()">🔄 Yangilash</button>
</div>
<div class="stats">
  <div class="stat blue"><div class="num" id="ts">...</div><div class="label">📝 Jami shikoyatlar</div></div>
  <div class="stat orange"><div class="num" id="ns">...</div><div class="label">🔴 Yangi shikoyatlar</div></div>
  <div class="stat green"><div class="num" id="tu">...</div><div class="label">👥 Foydalanuvchilar</div></div>
</div>
<div class="tabs">
  <button class="tab active" onclick="show('s')">📝 Shikoyatlar</button>
  <button class="tab" onclick="show('u')">👥 Foydalanuvchilar</button>
</div>
<div class="content">
  <div id="tab-s">
    <div class="search"><input id="ss" placeholder="🔍 Qidirish..." oninput="filterS()"></div>
    <div id="s-table"></div>
  </div>
  <div id="tab-u" style="display:none">
    <div class="search"><input id="su" placeholder="🔍 Qidirish..." oninput="filterU()"></div>
    <div id="u-table"></div>
  </div>
</div>
<script>
let S=[], U=[];
function show(t){
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));
  document.getElementById('tab-s').style.display='none';
  document.getElementById('tab-u').style.display='none';
  if(t==='s'){document.querySelectorAll('.tab')[0].classList.add('active');document.getElementById('tab-s').style.display='block';}
  else{document.querySelectorAll('.tab')[1].classList.add('active');document.getElementById('tab-u').style.display='block';}
}
function renderS(data){
  const c=document.getElementById('s-table');
  if(!data.length){c.innerHTML='<div class="empty"><div class="icon">📋</div><p>Shikoyatlar yo\\'q</p></div>';return;}
  let h=`<table><thead><tr><th>#</th><th>Sana</th><th>Ism</th><th>Telefon</th><th>Shikoyat</th><th>Holat</th></tr></thead><tbody>`;
  [...data].reverse().forEach(s=>{
    const b=s.holat==='Yangi'?'badge-new':'badge-read';
    h+=`<tr><td><b>#${s.id}</b></td><td>${s.sana}</td><td>${s.ism}</td><td><code>${s.telefon}</code></td><td class="shikoyat-text">${s.matn}</td><td><span class="badge ${b}">${s.holat}</span></td></tr>`;
  });
  c.innerHTML=h+'</tbody></table>';
}
function renderU(data){
  const c=document.getElementById('u-table');
  if(!data.length){c.innerHTML='<div class="empty"><div class="icon">👥</div><p>Foydalanuvchilar yo\\'q</p></div>';return;}
  let h=`<table><thead><tr><th>#</th><th>Ism</th><th>Username</th><th>Telegram ID</th><th>Sana</th></tr></thead><tbody>`;
  data.forEach((u,i)=>{h+=`<tr><td>${i+1}</td><td><b>${u.ism}</b></td><td>${u.username}</td><td><code>${u.id}</code></td><td>${u.sana}</td></tr>`;});
  c.innerHTML=h+'</tbody></table>';
}
function filterS(){const q=document.getElementById('ss').value.toLowerCase();renderS(S.filter(s=>s.ism.toLowerCase().includes(q)||s.telefon.toLowerCase().includes(q)||s.matn.toLowerCase().includes(q)));}
function filterU(){const q=document.getElementById('su').value.toLowerCase();renderU(U.filter(u=>u.ism.toLowerCase().includes(q)||u.username.toLowerCase().includes(q)));}
async function load(){
  try{
    const r=await fetch('/api/data');
    const d=await r.json();
    S=d.shikoyatlar||[];
    U=d.users||[];
    document.getElementById('ts').textContent=S.length;
    document.getElementById('ns').textContent=S.filter(s=>s.holat==='Yangi').length;
    document.getElementById('tu').textContent=U.length;
    renderS(S); renderU(U);
  }catch(e){console.error(e);}
}
load();
setInterval(load, 10000);
</script>
</body>
</html>"""

class AdminHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))

        elif self.path == '/api/data':
            shikoyatlar = load_json(SHIKOYATLAR_FILE, [])
            users_raw = load_json(USERS_FILE, {})
            users = list(users_raw.values())
            data = json.dumps({"shikoyatlar": shikoyatlar, "users": users}, ensure_ascii=False)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server = HTTPServer(('localhost', 5000), AdminHandler)
    print("✅ Admin panel: http://localhost:5000")
    server.serve_forever()


# ============================================================
# BOT HANDLERS
# ============================================================
class ShikoyatForm(StatesGroup):
    ism = State()
    telefon = State()
    shikoyat = State()

def asosiy_menyu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Lokatsiya"), KeyboardButton(text="📱 Ijtimoiy tarmoqlar")],
            [KeyboardButton(text="📝 Shikoyat va takliflar"), KeyboardButton(text="ℹ️ Ma'lumot")],
            [KeyboardButton(text="📞 Bog'lanish"), KeyboardButton(text="🕐 Ish vaqti")],
        ],
        resize_keyboard=True
    )

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    save_user(message.from_user)
    await message.answer(
        f"👋 Assalomu alaykum!\n\n🏥 <b>{KASALXONA_NOMI}</b> botiga xush kelibsiz!\n\nQuyidagi bo'limlardan birini tanlang:",
        parse_mode="HTML", reply_markup=asosiy_menyu()
    )

@dp.message(Command("users"))
async def users_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    users = load_json(USERS_FILE, {})
    await message.answer(f"👥 Jami foydalanuvchilar: <b>{len(users)} ta</b>\n\nAdmin panel: http://localhost:5000", parse_mode="HTML")

@dp.message(F.text == "📍 Lokatsiya")
async def lokatsiya_handler(message: types.Message):
    await message.answer(f"📍 <b>Kasalxona manzili:</b>\n{KASALXONA_MANZIL}", parse_mode="HTML")
    await bot.send_location(chat_id=message.chat.id, latitude=KASALXONA_LAT, longitude=KASALXONA_LON)

@dp.message(F.text == "📱 Ijtimoiy tarmoqlar")
async def ijtimoiy_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📸 Instagram", url=INSTAGRAM)],
        [InlineKeyboardButton(text="✈️ Telegram kanal", url=TELEGRAM_KANAL)],
        [InlineKeyboardButton(text="👥 Facebook", url=FACEBOOK)],
        [InlineKeyboardButton(text="🌐 Veb-sayt", url=WEBSITE)],
    ])
    await message.answer("📱 <b>Bizning ijtimoiy tarmoqlarimiz:</b>", parse_mode="HTML", reply_markup=keyboard)

@dp.message(F.text == "📝 Shikoyat va takliflar")
async def shikoyat_boshlash(message: types.Message, state: FSMContext):
    await state.set_state(ShikoyatForm.ism)
    await message.answer(
        "📝 <b>Shikoyat va takliflar</b>\n\nIsmingizni kiriting:",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True)
    )

@dp.message(ShikoyatForm.ism)
async def shikoyat_ism(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=asosiy_menyu())
        return
    await state.update_data(ism=message.text)
    await state.set_state(ShikoyatForm.telefon)
    await message.answer("📞 Telefon raqamingizni kiriting:")

@dp.message(ShikoyatForm.telefon)
async def shikoyat_telefon(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=asosiy_menyu())
        return
    await state.update_data(telefon=message.text)
    await state.set_state(ShikoyatForm.shikoyat)
    await message.answer("✍️ Shikoyat yoki taklifingizni yozing:")

@dp.message(ShikoyatForm.shikoyat)
async def shikoyat_yuborish(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Bekor qilindi.", reply_markup=asosiy_menyu())
        return
    data = await state.get_data()
    save_shikoyat(data['ism'], data['telefon'], message.text, message.from_user.id)
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
        "✅ <b>Shikoyatingiz qabul qilindi!</b>\n\nTez orada siz bilan bog'lanamiz. Rahmat!",
        parse_mode="HTML", reply_markup=asosiy_menyu()
    )

@dp.message(F.text == "ℹ️ Ma'lumot")
async def malumot_handler(message: types.Message):
    await message.answer(
        f"🏥 <b>{KASALXONA_NOMI}</b>\n\n📍 Manzil: {KASALXONA_MANZIL}\n📞 Telefon: {KASALXONA_TEL}\n🕐 Ish vaqti:\n{KASALXONA_ISH_VAQTI}",
        parse_mode="HTML"
    )

@dp.message(F.text == "📞 Bog'lanish")
async def boglanish_handler(message: types.Message):
    await message.answer(
        f"📞 <b>Bog'lanish:</b>\n\n☎️ Telefon: <code>{KASALXONA_TEL}</code>\n\n📍 Manzil: {KASALXONA_MANZIL}\n\nRaqamni bosib nusxa olishingiz mumkin!",
        parse_mode="HTML"
    )

@dp.message(F.text == "🕐 Ish vaqti")
async def ish_vaqti_handler(message: types.Message):
    await message.answer(f"🕐 <b>Ish vaqtimiz:</b>\n\n{KASALXONA_ISH_VAQTI}", parse_mode="HTML")


# ============================================================
# ISHGA TUSHIRISH
# ============================================================
async def main():
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
