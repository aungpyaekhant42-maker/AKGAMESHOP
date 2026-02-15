import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import json
import os
from datetime import datetime

# ၁။ သတ်မှတ်ချက်များ
TOKEN = "8404553125:AAFxbJRUSurUVtxV6iwwy4xUoQSQkPDGsC8"
ADMIN_ID = 8532587449  # သင့် Admin ID ကို ဒီမှာထည့်ပါ

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# User Data သိမ်းမယ့် File
USER_DATA_FILE = "user_balances.json"
ORDERS_FILE = "orders.json"

# User Data တွေကို Load/Save လုပ်မယ်
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Order Data တွေကို Load/Save လုပ်မယ်
def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"pending": [], "completed": [], "cancelled": []}

def save_orders(data):
    with open(ORDERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ၂။ Keyboard
kb = [
    [KeyboardButton(text="💎 စိန်ဈေးကြည့်ရန်"), KeyboardButton(text="🎮 PUBG UC ဈေးနှုန်း")],
    [KeyboardButton(text="💰 Balance"), KeyboardButton(text="📞 Admin ကိုဆက်သွယ်ရန်")],
    [KeyboardButton(text="📥 ငွေသွင်းရန်"), KeyboardButton(text="📝 အော်ဒါတင်ရန်")],
    [KeyboardButton(text="🔙 Back Menu")]
]
keyboard = ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Admin Keyboard
admin_kb = [
    [KeyboardButton(text="📢 Broadcast ပို့ရန်"), KeyboardButton(text="👥 User စာရင်း")],
    [KeyboardButton(text="📊 စာရင်းအင်း"), KeyboardButton(text="🔙 ပင်မမီနူး")]
]
admin_keyboard = ReplyKeyboardMarkup(keyboard=admin_kb, resize_keyboard=True)

# ML Diamond Price List
ML_DIAMONDS = {
    "86": 4880,
    "172": 9700,
    "257": 14880,
    "343": 19880,
    "429": 24880,
    "514": 29880,
    "600": 34880,
    "706": 39880,
    "963": 53970,
    "1049":58950 ,
    "1135": 63950,
    "Weeklypas": 5950,
}

# PUBG UC Price List
PUBG_UC = {
    "60": 4500,
    "120": 7900,
    "180": 11850,
    "325": 19800,
    "385": 23750,
    "445": 27700,
    "660": 39500,
    "985": 59300,
    "1320": 79000,
    "1800": 98000,
}

# ၃။ FSM States
class DepositState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_amount = State()
    waiting_for_id = State()

class OrderState(StatesGroup):
    waiting_for_game = State()
    waiting_for_item = State()
    waiting_for_id = State()
    waiting_for_confirm = State()

class BroadcastState(StatesGroup):
    waiting_for_message = State()
    waiting_for_confirm = State()

# ၄။ Start Command
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    # User အသစ်ဆိုရင် Data အသစ်ထည့်မယ်
    if user_id not in user_data:
        user_data[user_id] = {
            "username": message.from_user.username or message.from_user.full_name,
            "full_name": message.from_user.full_name,
            "balance": 0,
            "deposit_history": [],
            "order_history": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_user_data(user_data)
    else:
        # Update last active
        user_data[user_id]["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_user_data(user_data)
        
        # Old user data ကို update လုပ်မယ်
        if user_data[user_id].get("deposit_history") and len(user_data[user_id]["deposit_history"]) > 0:
            first_item = user_data[user_id]["deposit_history"][0]
            if isinstance(first_item, int):
                new_history = []
                for amount in user_data[user_id]["deposit_history"]:
                    new_history.append({
                        "amount": amount,
                        "date": "2024-01-01 00:00:00",
                        "admin": "System Update"
                    })
                user_data[user_id]["deposit_history"] = new_history
                save_user_data(user_data)
    
    # Admin ဆိုရင် Admin Menu ပြမယ်
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "👑 **Admin Menu မှ ကြိုဆိုပါတယ်**\n\n"
            "သင်သည် Admin ဖြစ်ပါသည်။ အောက်ပါမီနူးမှ ရွေးချယ်နိုင်ပါသည်။",
            parse_mode="Markdown",
            reply_markup=admin_keyboard
        )
    else:
        await message.answer(
            "𝘼𝙆 𝙂𝘼𝙈𝙀 𝙎𝙃𝙊𝙋မှ ကြိုဆိုပါတယ်။\n"
            "ငွေလွှဲပြီးပါက 'ငွေသွင်းရန်' ခလုတ်ကိုနှိပ်ပြီး ပြေစာပုံနှင့် ငွေပမာဏကို ပို့ပေးပါ။",
            reply_markup=keyboard
        )

# ၅။ Back Menu
@dp.message(F.text == "🔙 Back Menu")
async def back_menu(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin မီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=admin_keyboard)
    else:
        await message.answer("ပင်မမီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=keyboard)

# ၆။ Admin Menu မှ ပင်မမီနူးသို့
@dp.message(F.text == "🔙 ပင်မမီနူး")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin မီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=admin_keyboard)
    else:
        await message.answer("ပင်မမီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=keyboard)

# ၇။ Broadcast ပို့ရန်
@dp.message(F.text == "📢 Broadcast ပို့ရန်")
async def broadcast_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await message.answer("ဤလုပ်ဆောင်ချက်သည် Admin များအတွက်သာ ဖြစ်ပါသည်။")
        return
    
    await message.answer(
        "📢 **Broadcast Message**\n\n"
        "ကျေးဇူးပြု၍ User အားလုံးကို ပို့လိုသော စာသားကို ရိုက်ထည့်ပါ။\n"
        "သင်သည် စာသား၊ ဓာတ်ပုံ၊ ဗီဒီယို စသည်ဖြင့် မည်သည့်အရာမဆို ပို့နိုင်ပါသည်။\n\n"
        "ပယ်ဖျက်လိုပါက /cancel ကိုနှိပ်ပါ။",
        parse_mode="Markdown"
    )
    await state.set_state(BroadcastState.waiting_for_message)

# ၈။ Cancel Command
@dp.message(Command("cancel"))
async def cancel_broadcast(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    
    await state.clear()
    await message.answer("လုပ်ဆောင်ချက်ကို ဖျက်သိမ်းလိုက်သည်။", reply_markup=admin_keyboard)

# ၉။ Broadcast Message လက်ခံခြင်း
@dp.message(BroadcastState.waiting_for_message)
async def broadcast_receive(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        await state.clear()
        return
    
    # Message data ကို သိမ်းမယ်
    message_data = {
        "type": "text",
        "content": message.text,
        "has_media": False
    }
    
    # Photo ပါလာရင်
    if message.photo:
        message_data["type"] = "photo"
        message_data["photo_id"] = message.photo[-1].file_id
        message_data["caption"] = message.caption or ""
        message_data["has_media"] = True
    
    # Video ပါလာရင်
    elif message.video:
        message_data["type"] = "video"
        message_data["video_id"] = message.video.file_id
        message_data["caption"] = message.caption or ""
        message_data["has_media"] = True
    
    # Document ပါလာရင်
    elif message.document:
        message_data["type"] = "document"
        message_data["document_id"] = message.document.file_id
        message_data["caption"] = message.caption or ""
        message_data["has_media"] = True
    
    # Animation (GIF) ပါလာရင်
    elif message.animation:
        message_data["type"] = "animation"
        message_data["animation_id"] = message.animation.file_id
        message_data["caption"] = message.caption or ""
        message_data["has_media"] = True
    
    await state.update_data(message_data=message_data)
    
    # အတည်ပြုရန် ပြမယ်
    user_data = load_user_data()
    total_users = len(user_data)
    
    confirm_text = (
        f"📢 **Broadcast အတည်ပြုရန်**\n\n"
        f"စုစုပေါင်း User အရေအတွက်: **{total_users}** ယောက်\n\n"
        f"ဤအကြောင်းအရာကို User အားလုံးဆီ ပို့ရန် အတည်ပြုပါသလား?"
    )
    
    confirm_buttons = [
        [
            InlineKeyboardButton(text="✅ ပို့မယ်", callback_data="broadcast_confirm"),
            InlineKeyboardButton(text="❌ မပို့တော့ပါ", callback_data="broadcast_cancel")
        ]
    ]
    
    # Message အကြိုကြည့်ရန် ပြမယ်
    if message_data["has_media"]:
        if message_data["type"] == "photo":
            await message.answer_photo(
                photo=message_data["photo_id"],
                caption=f"**အကြိုကြည့်ရန် (Preview)**\n\n{message_data['caption']}\n\n{confirm_text}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=confirm_buttons)
            )
        elif message_data["type"] == "video":
            await message.answer_video(
                video=message_data["video_id"],
                caption=f"**အကြိုကြည့်ရန် (Preview)**\n\n{message_data['caption']}\n\n{confirm_text}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=confirm_buttons)
            )
    else:
        await message.answer(
            f"**အကြိုကြည့်ရန် (Preview)**\n\n{message_data['content']}\n\n{confirm_text}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=confirm_buttons)
        )
    
    await state.set_state(BroadcastState.waiting_for_confirm)

# ၁၀။ Broadcast အတည်ပြုခြင်း
@dp.callback_query(lambda c: c.data in ["broadcast_confirm", "broadcast_cancel"])
async def broadcast_confirm(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("သင်သည် Admin မဟုတ်ပါ။")
        return
    
    if callback.data == "broadcast_cancel":
        await state.clear()
        await callback.message.edit_text("❌ Broadcast ကို ဖျက်သိမ်းလိုက်သည်။")
        await callback.answer()
        return
    
    # Broadcast စတင်မည်
    data = await state.get_data()
    message_data = data.get('message_data')
    user_data = load_user_data()
    
    await callback.message.edit_text("📢 Broadcast စတင်နေပါပြီ... ခဏစောင့်ပါ။")
    
    success_count = 0
    fail_count = 0
    
    for user_id in user_data.keys():
        try:
            if message_data["has_media"]:
                if message_data["type"] == "photo":
                    await bot.send_photo(
                        chat_id=int(user_id),
                        photo=message_data["photo_id"],
                        caption=message_data["caption"]
                    )
                elif message_data["type"] == "video":
                    await bot.send_video(
                        chat_id=int(user_id),
                        video=message_data["video_id"],
                        caption=message_data["caption"]
                    )
                elif message_data["type"] == "document":
                    await bot.send_document(
                        chat_id=int(user_id),
                        document=message_data["document_id"],
                        caption=message_data["caption"]
                    )
                elif message_data["type"] == "animation":
                    await bot.send_animation(
                        chat_id=int(user_id),
                        animation=message_data["animation_id"],
                        caption=message_data["caption"]
                    )
            else:
                await bot.send_message(
                    chat_id=int(user_id),
                    text=message_data["content"]
                )
            
            success_count += 1
            await asyncio.sleep(0.05)  # Rate limit ကိုရှောင်ရန်
            
        except Exception as e:
            fail_count += 1
            print(f"Failed to send to {user_id}: {e}")
    
    # ရလဒ်ပြမယ်
    result_text = (
        f"📢 **Broadcast ပြီးဆုံးပါပြီ**\n\n"
        f"✅ ပို့ပြီးသူ: **{success_count}** ယောက်\n"
        f"❌ မပို့ရသေးသူ: **{fail_count}** ယောက်\n"
        f"📊 စုစုပေါင်း: **{success_count + fail_count}** ယောက်"
    )
    
    await callback.message.answer(result_text, parse_mode="Markdown", reply_markup=admin_keyboard)
    await state.clear()
    await callback.answer()

# ၁၁။ User စာရင်းကြည့်ရန်
@dp.message(F.text == "👥 User စာရင်း")
async def user_list(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("ဤလုပ်ဆောင်ချက်သည် Admin များအတွက်သာ ဖြစ်ပါသည်။")
        return
    
    user_data = load_user_data()
    
    # User အရေအတွက်
    total_users = len(user_data)
    
    # စုစုပေါင်းငွေပမာဏ
    total_balance = sum([u['balance'] for u in user_data.values()])
    
    # ယနေ့ဝင်လာသူ
    today = datetime.now().strftime("%Y-%m-%d")
    today_active = 0
    for u in user_data.values():
        if u.get('last_active', '').startswith(today):
            today_active += 1
    
    # စာရင်းပေါင်းချုပ်
    summary = (
        f"👥 **User စာရင်းအချက်အလက်**\n\n"
        f"📊 စုစုပေါင်း User: **{total_users}** ယောက်\n"
        f"💰 စုစုပေါင်းလက်ကျန်: **{total_balance:,} Ks**\n"
        f"📅 ယနေ့ဝင်လာသူ: **{today_active}** ယောက်\n\n"
        f"**အသေးစိတ်စာရင်း:**\n"
        f"─────────────────"
    )
    
    # User ၁၀ ယောက်စာ ပြမယ်
    count = 0
    for uid, uinfo in user_data.items():
        if count < 10:
            summary += (
                f"\n🆔 ID: `{uid}`\n"
                f"📝 Username: @{uinfo.get('username', 'N/A')}\n"
                f"💰 Balance: {uinfo['balance']:,} Ks\n"
                f"📦 Orders: {len(uinfo.get('order_history', []))}\n"
                f"─────────────────"
            )
            count += 1
    
    if total_users > 10:
        summary += f"\n... နှင့် အခြား {total_users - 10} ယောက်"
    
    await message.answer(summary, parse_mode="Markdown")

# ၁၂။ စာရင်းအင်းကြည့်ရန်
@dp.message(F.text == "📊 စာရင်းအင်း")
async def statistics(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("ဤလုပ်ဆောင်ချက်သည် Admin များအတွက်သာ ဖြစ်ပါသည်။")
        return
    
    user_data = load_user_data()
    orders = load_orders()
    
    # User စာရင်း
    total_users = len(user_data)
    
    # စုစုပေါင်းငွေပမာဏ
    total_balance = sum([u['balance'] for u in user_data.values()])
    total_deposit = 0
    for u in user_data.values():
        for d in u.get('deposit_history', []):
            if isinstance(d, dict):
                total_deposit += d.get('amount', 0)
            else:
                total_deposit += d
    
    # အော်ဒါစာရင်း
    pending_orders = len(orders.get('pending', []))
    completed_orders = len(orders.get('completed', []))
    cancelled_orders = len(orders.get('cancelled', []))
    total_orders = pending_orders + completed_orders + cancelled_orders
    
    # စုစုပေါင်းရောင်းရငွေ
    total_sales = sum([o.get('price', 0) for o in orders.get('completed', [])])
    
    stats = (
        f"📊 **စာရင်းအင်းအချက်အလက်များ**\n\n"
        f"👥 **User ဆိုင်ရာ**\n"
        f"├ စုစုပေါင်း User: {total_users} ယောက်\n"
        f"├ စုစုပေါင်းလက်ကျန်: {total_balance:,} Ks\n"
        f"└ စုစုပေါင်းငွေသွင်း: {total_deposit:,} Ks\n\n"
        f"📦 **အော်ဒါဆိုင်ရာ**\n"
        f"├ စုစုပေါင်းအော်ဒါ: {total_orders} ခု\n"
        f"├ ဆိုင်းငံ့: {pending_orders} ခု\n"
        f"├ ပြီးဆုံး: {completed_orders} ခု\n"
        f"├ ပျက်ကွက်: {cancelled_orders} ခု\n"
        f"└ စုစုပေါင်းရောင်းရငွေ: {total_sales:,} Ks"
    )
    
    await message.answer(stats, parse_mode="Markdown")

# ၁၃။ MLBB စျေးနှုန်းများ
@dp.message(F.text == "💎 စိန်ဈေးကြည့်ရန်")
async def ml_prices(message: types.Message):
    price_text = "💎 Mobile Legends စျေးနှုန်းများ\n"
    price_text += "─────────────────\n"
    for diamond, price in ML_DIAMONDS.items():
        if diamond == "Weeklypas":
            price_text += f"💎 Weekly Pass - {price} Ks\n"
        else:
            price_text += f"💎 {diamond} Diamonds - {price} Ks\n"
    price_text += "─────────────────"
    await message.answer(price_text)

# ၁၄။ PUBG စျေးနှုန်းများ
@dp.message(F.text == "🎮 PUBG UC ဈေးနှုန်း")
async def pubg_prices(message: types.Message):
    price_text = "🎮 PUBG UC စျေးနှုန်းများ\n"
    price_text += "─────────────────\n"
    for uc, price in PUBG_UC.items():
        price_text += f"🎮 UC {uc} - {price} Ks\n"
    price_text += "─────────────────"
    await message.answer(price_text)

# ၁၅။ Balance ကြည့်ရန်
@dp.message(F.text == "💰 Balance")
async def check_balance(message: types.Message):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    if user_id in user_data:
        user_info = user_data[user_id]
        
        # စုစုပေါင်းငွေသွင်းပမာဏ တွက်ချက်ခြင်း
        total_deposit = 0
        if user_info['deposit_history']:
            if isinstance(user_info['deposit_history'][0], dict):
                total_deposit = sum([d.get('amount', 0) for d in user_info['deposit_history']])
            else:
                total_deposit = sum(user_info['deposit_history'])
        
        balance_text = (
            f"👤 <b>အသုံးပြုသူအချက်အလက်</b>\n"
            f"─────────────────\n"
            f"🆔 User ID: <code>{message.from_user.id}</code>\n"
            f"📝 Username: @{message.from_user.username if message.from_user.username else 'မရှိပါ'}\n"
            f"💰 လက်ကျန်ငွေ: <b>{user_info['balance']:,} Ks</b>\n"
            f"📊 စုစုပေါင်းငွေသွင်း: <b>{total_deposit:,} Ks</b>\n"
            f"📦 စုစုပေါင်းမှာယူမှု: <b>{len(user_info['order_history'])}</b>\n"
            f"─────────────────"
        )
        await message.answer(balance_text, parse_mode="HTML")
    else:
        await message.answer("သင့်အကောင့်ကို ရှာမတွေ့ပါ။ /start ကိုနှိပ်ပါ။")

# ၁၆။ အော်ဒါတင်ရန်
@dp.message(F.text == "📝 အော်ဒါတင်ရန်")
async def order_start(message: types.Message, state: FSMContext):
    user_id = str(message.from_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        await message.answer("ကျေးဇူးပြု၍ /start ကိုအရင်နှိပ်ပါ။")
        return
    
    # Game selection keyboard
    game_kb = [
        [KeyboardButton(text="🎮 Mobile Legends")],
        [KeyboardButton(text="🎯 PUBG Mobile")],
        [KeyboardButton(text="🔙 Back Menu")]
    ]
    
    await message.answer(
        f"သင့်လက်ကျန်ငွေ: <b>{user_data[user_id]['balance']:,} Ks</b>\n\n"
        f"📝 <b>အော်ဒါတင်ရန်</b>\n"
        f"ကျေးဇူးပြု၍ ဂိမ်းအမျိုးအစားကို ရွေးချယ်ပါ။",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(keyboard=game_kb, resize_keyboard=True)
    )
    await state.set_state(OrderState.waiting_for_game)

# ၁၇။ ဂိမ်းရွေးချယ်ခြင်း
@dp.message(OrderState.waiting_for_game, F.text)
async def select_game(message: types.Message, state: FSMContext):
    if message.text == "🔙 Back Menu":
        await state.clear()
        await message.answer("ပင်မမီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=keyboard)
        return
    
    if message.text == "🎮 Mobile Legends":
        await state.update_data(game="ML")
        
        # Diamond selection keyboard
        diamond_kb = []
        for d in ML_DIAMONDS.keys():
            diamond_kb.append([KeyboardButton(text=str(d))])
        diamond_kb.append([KeyboardButton(text="🔙 Back Menu")])
        
        await message.answer(
            f"🎮 <b>Mobile Legends အော်ဒါတင်ရန်</b>\n\n"
            f"ကျေးဇူးပြု၍ သင်ဝယ်ယူလိုသော စိန်အရေအတွက်ကို ရွေးချယ်ပါ။\n\n"
            f"{chr(10).join([f'💎 {k} Diamonds - {v} Ks' for k, v in ML_DIAMONDS.items()])}",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(keyboard=diamond_kb, resize_keyboard=True)
        )
        await state.set_state(OrderState.waiting_for_item)
        
    elif message.text == "🎯 PUBG Mobile":
        await state.update_data(game="PUBG")
        
        # UC selection keyboard
        uc_kb = []
        for u in PUBG_UC.keys():
            uc_kb.append([KeyboardButton(text=u)])
        uc_kb.append([KeyboardButton(text="🔙 Back Menu")])
        
        await message.answer(
            f"🎯 <b>PUBG Mobile အော်ဒါတင်ရန်</b>\n\n"
            f"ကျေးဇူးပြု၍ သင်ဝယ်ယူလိုသော UC အရေအတွက်ကို ရွေးချယ်ပါ။\n\n"
            f"{chr(10).join([f'🎮 UC {u} - {p} Ks' for u, p in PUBG_UC.items()])}",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(keyboard=uc_kb, resize_keyboard=True)
        )
        await state.set_state(OrderState.waiting_for_item)
    else:
        await message.answer("မှားယွင်းသော ရွေးချယ်မှုပါ။ ကျေးဇူးပြု၍ အထက်ပါ စာရင်းထဲမှ ရွေးချယ်ပါ။")

# ၁၈။ ပစ္စည်းရွေးချယ်ခြင်း
@dp.message(OrderState.waiting_for_item, F.text)
async def select_item(message: types.Message, state: FSMContext):
    if message.text == "🔙 Back Menu":
        await state.clear()
        await message.answer("ပင်မမီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=keyboard)
        return
    
    data = await state.get_data()
    game = data.get('game')
    
    if game == "ML":
        item = message.text
        if item not in ML_DIAMONDS:
            await message.answer("မှားယွင်းသော ရွေးချယ်မှုပါ။ ကျေးဇူးပြု၍ စာရင်းထဲမှ ရွေးချယ်ပါ။")
            return
        price = ML_DIAMONDS[item]
        await state.update_data(item=item, price=price)
        
        await message.answer(
            f"သင်ရွေးချယ်ထားသော ပစ္စည်း: {'Weekly Pass' if item == 'Weeklypas' else f'💎 {item} Diamonds'}\n"
            f"ကျသင့်ငွေ: <b>{price:,} Ks</b>\n\n"
            f"ကျေးဇူးပြု၍ သင်၏ Game ID ကို ထည့်သွင်းပါ။",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Back Menu")]], resize_keyboard=True)
        )
        await state.set_state(OrderState.waiting_for_id)
        
    elif game == "PUBG":
        item = message.text
        if item not in PUBG_UC:
            await message.answer("မှားယွင်းသော ရွေးချယ်မှုပါ။ ကျေးဇူးပြု၍ စာရင်းထဲမှ ရွေးချယ်ပါ။")
            return
        price = PUBG_UC[item]
        await state.update_data(item=item, price=price)
        
        await message.answer(
            f"သင်ရွေးချယ်ထားသော ပစ္စည်း: 🎮 UC {item}\n"
            f"ကျသင့်ငွေ: <b>{price:,} Ks</b>\n\n"
            f"ကျေးဇူးပြု၍ သင်၏ Game ID ကို ထည့်သွင်းပါ။",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🔙 Back Menu")]], resize_keyboard=True)
        )
        await state.set_state(OrderState.waiting_for_id)

# ၁၉။ Game ID ထည့်ခြင်း
@dp.message(OrderState.waiting_for_id, F.text)
async def enter_game_id(message: types.Message, state: FSMContext):
    if message.text == "🔙 Back Menu":
        await state.clear()
        await message.answer("ပင်မမီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=keyboard)
        return
    
    game_id = message.text.strip()
    if len(game_id) < 4:
        await message.answer("မှန်ကန်သော Game ID (အနည်းဆုံး 4 လုံး) ကို ထည့်သွင်းပါ။")
        return
    
    data = await state.get_data()
    game = data.get('game')
    item = data.get('item')
    price = data.get('price')
    
    # အတည်ပြုရန် ပြမယ်
    item_name = ""
    if game == "ML":
        item_name = "Weekly Pass" if item == "Weeklypas" else f"💎 {item} Diamonds"
    else:
        item_name = f"🎮 UC {item}"
    
    confirm_text = (
        f"📝 <b>သင်၏မှာယူမှု အချက်အလက်များ</b>\n\n"
        f"🎮 ဂိမ်း: {'Mobile Legends' if game == 'ML' else 'PUBG Mobile'}\n"
        f"🆔 Game ID: <code>{game_id}</code>\n"
        f"📦 ပစ္စည်း: {item_name}\n"
        f"💰 ကျသင့်ငွေ: <b>{price:,} Ks</b>\n\n"
        f"အတည်ပြုရန် အောက်ပါခလုတ်ကိုနှိပ်ပါ။"
    )
    
    confirm_buttons = [
        [
            InlineKeyboardButton(text="✅ အတည်ပြုမယ်", callback_data=f"confirm_order_{game_id}"),
            InlineKeyboardButton(text="❌ မလုပ်တော့ပါ", callback_data="cancel_order")
        ]
    ]
    
    await state.update_data(game_id=game_id)
    await message.answer(
        confirm_text,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=confirm_buttons)
    )
    await state.set_state(OrderState.waiting_for_confirm)

# ၂၀။ Order အတည်ပြုခြင်း
@dp.callback_query(lambda c: c.data.startswith('confirm_order_') or c.data == 'cancel_order')
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'cancel_order':
        await state.clear()
        await callback.message.edit_text("မှာယူမှု ဖျက်သိမ်းလိုက်သည်။")
        await callback.answer()
        await callback.message.answer("ပင်မမီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=keyboard)
        return
    
    game_id = callback.data.replace('confirm_order_', '')
    data = await state.get_data()
    user_id = str(callback.from_user.id)
    user_data = load_user_data()
    
    if user_id not in user_data:
        await callback.message.edit_text("အသုံးပြုသူ အချက်အလက် မတွေ့ပါ။ /start ကိုနှိပ်ပါ။")
        await state.clear()
        await callback.answer()
        return
    
    game = data.get('game')
    item = data.get('item')
    price = data.get('price')
    
    # Balance စစ်ဆေးမယ်
    if user_data[user_id]['balance'] < price:
        await callback.message.edit_text(
            f"❌ လက်ကျန်ငွေ မလုံလောက်ပါ။\n"
            f"လက်ကျန်ငွေ: <b>{user_data[user_id]['balance']:,} Ks</b>\n"
            f"လိုအပ်သောငွေ: <b>{price:,} Ks</b>\n\n"
            f"ကျေးဇူးပြု၍ ငွေအရင်သွင်းပါ။",
            parse_mode="HTML"
        )
        await state.clear()
        await callback.answer()
        await callback.message.answer("ပင်မမီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=keyboard)
        return
    
    # Balance ထဲက နုတ်မယ်
    old_balance = user_data[user_id]['balance']
    user_data[user_id]['balance'] -= price
    
    # Item name ပြင်ဆင်
    item_name = ""
    if game == "ML":
        item_name = "Weekly Pass" if item == "Weeklypas" else f"{item} Diamonds"
    else:
        item_name = f"UC {item}"
    
    # Order History ထဲထည့်မယ်
    order_info = {
        "order_id": f"{game}{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "game": "Mobile Legends" if game == "ML" else "PUBG Mobile",
        "item": item_name,
        "game_id": game_id,
        "price": price,
        "old_balance": old_balance,
        "new_balance": user_data[user_id]['balance'],
        "status": "pending",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    user_data[user_id]['order_history'].append(order_info)
    user_data[user_id]['last_active'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_user_data(user_data)
    
    # Order ကို Orders File မှာသိမ်းမယ်
    orders = load_orders()
    orders["pending"].append({
        **order_info,
        "user_id": user_id,
        "username": callback.from_user.username or callback.from_user.full_name,
        "full_name": callback.from_user.full_name
    })
    save_orders(orders)
    
    # Admin ဆီပို့မယ်
    admin_buttons = [
        [
            InlineKeyboardButton(text="✅ ပြီးပါပြီ", callback_data=f"complete_{order_info['order_id']}"),
            InlineKeyboardButton(text="❌ ပြဿနာရှိ", callback_data=f"problem_{order_info['order_id']}")
        ]
    ]
    
    admin_message = (
        f"🛒 <b>အော်ဒါအသစ် ရောက်ရှိ</b>\n\n"
        f"🆔 အော်ဒါနံပါတ်: <code>{order_info['order_id']}</code>\n"
        f"👤 အမည်: {callback.from_user.full_name}\n"
        f"🆔 User ID: <code>{user_id}</code>\n"
        f"📝 Username: @{callback.from_user.username if callback.from_user.username else 'မရှိပါ'}\n"
        f"🎮 ဂိမ်း: {order_info['game']}\n"
        f"📦 ပစ္စည်း: {item_name}\n"
        f"🎮 Game ID: <code>{game_id}</code>\n"
        f"💰 ကျသင့်ငွေ: <b>{price:,} Ks</b>\n"
        f"💵 လက်ကျန်အဟောင်း: <b>{old_balance:,} Ks</b>\n"
        f"💵 လက်ကျန်အသစ်: <b>{user_data[user_id]['balance']:,} Ks</b>\n"
        f"⏰ အချိန်: {order_info['timestamp']}"
    )
    
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=admin_buttons)
    )
    
    # User ကို အကြောင်းကြားမယ်
    await callback.message.edit_text(
        f"✅ <b>အော်ဒါတင်ပြီးပါပြီ။</b>\n\n"
        f"🆔 အော်ဒါနံပါတ်: <code>{order_info['order_id']}</code>\n"
        f"🎮 ဂိမ်း: {order_info['game']}\n"
        f"📦 ပစ္စည်း: {item_name}\n"
        f"💰 ကျသင့်ငွေ: <b>{price:,} Ks</b>\n"
        f"💵 လက်ကျန်အဟောင်း: <b>{old_balance:,} Ks</b>\n"
        f"💵 လက်ကျန်အသစ်: <b>{user_data[user_id]['balance']:,} Ks</b>\n\n"
        f"Admin မှ စစ်ဆေးပြီး မကြာမီ ထည့်ပေးပါမည်။",
        parse_mode="HTML"
    )
    
    await state.clear()
    await callback.answer()
    await callback.message.answer("ပင်မမီနူးသို့ ပြန်လည်ရောက်ရှိပါပြီ။", reply_markup=keyboard)

# ၂၁။ Admin မှ Order ပြီးဆုံးကြောင်း အတည်ပြုခြင်း
@dp.callback_query(lambda c: c.data.startswith('complete_') or c.data.startswith('problem_'))
async def process_order_status(callback: types.CallbackQuery):
    data = callback.data.split('_')
    action = data[0]
    order_id = data[1]
    
    orders = load_orders()
    
    if action == "complete":
        for i, order in enumerate(orders["pending"]):
            if order["order_id"] == order_id:
                completed_order = orders["pending"].pop(i)
                completed_order["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                completed_order["completed_by"] = callback.from_user.full_name
                orders["completed"].append(completed_order)
                save_orders(orders)
                
                await bot.send_message(
                    chat_id=int(completed_order["user_id"]),
                    text=f"✅ <b>အော်ဒါ ပြီးဆုံးပါပြီ။</b>\n\n"
                         f"🆔 အော်ဒါနံပါတ်: <code>{order_id}</code>\n"
                         f"🎮 ဂိမ်း: {completed_order['game']}\n"
                         f"📦 ပစ္စည်း: {completed_order['item']}\n"
                         f"🎮 Game ID: <code>{completed_order['game_id']}</code>\n\n"
                         f"အသုံးပြုပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။",
                    parse_mode="HTML"
                )
                
                await callback.message.edit_text(
                    callback.message.text + "\n\n✅ <b>အော်ဒါပြီးဆုံးကြောင်း အတည်ပြုပြီး</b>",
                    parse_mode="HTML"
                )
                break
    
    elif action == "problem":
        for i, order in enumerate(orders["pending"]):
            if order["order_id"] == order_id:
                problem_order = orders["pending"].pop(i)
                problem_order["cancelled_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                problem_order["cancelled_by"] = callback.from_user.full_name
                orders["cancelled"].append(problem_order)
                save_orders(orders)
                
                await bot.send_message(
                    chat_id=int(problem_order["user_id"]),
                    text=f"⚠️ <b>အော်ဒါတွင် ပြဿနာရှိနေပါသည်။</b>\n\n"
                         f"🆔 အော်ဒါနံပါတ်: <code>{order_id}</code>\n"
                         f"ကျေးဇူးပြု၍ Admin ကို ဆက်သွယ်ပါ။",
                    parse_mode="HTML"
                )
                
                await callback.message.edit_text(
                    callback.message.text + "\n\n⚠️ <b>ပြဿနာရှိကြောင်း အကြောင်းကြားပြီး</b>",
                    parse_mode="HTML"
                )
                break
    
    await callback.answer()

# ၂၂။ ငွေသွင်းရန်
@dp.message(F.text == "📥 ငွေသွင်းရန်")
async def deposit_start(message: types.Message, state: FSMContext):
    await message.answer(
        "📥 <b>ငွေသွင်းရန် လုပ်ငန်းစဉ်</b>\n\n"
        "ကျေးဇူးပြု၍ အောက်ပါအတိုင်း ပို့ပေးပါ။\n\n"
        "1. ငွေလွှဲပြေစာ Screenshot ပို့ပါ\n"
        "2. ငွေပမာဏ ထည့်သွင်းပါ\n"
        "3. ငွေလွှဲအမှတ်စဉ် (5 လုံး) ထည့်သွင်းပါ",
        parse_mode="HTML"
    )
    await state.set_state(DepositState.waiting_for_photo)

# ၂၃။ ငွေသွင်းပြေစာပုံ လက်ခံခြင်း
@dp.message(DepositState.waiting_for_photo, F.photo)
async def deposit_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo_id=message.photo[-1].file_id)
    await message.answer("ကျေးဇူးပြု၍ ငွေပမာဏကို ထည့်သွင်းပါ။ (ဥပမာ - 5000)")
    await state.set_state(DepositState.waiting_for_amount)

# ၂၄။ ငွေပမာဏ လက်ခံခြင်း
@dp.message(DepositState.waiting_for_amount, F.text)
async def deposit_amount(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.replace(',', '').strip())
        if amount < 1000:
            await message.answer("အနည်းဆုံး 1000 Ks မှ စတင်ငွေသွင်းနိုင်ပါသည်။")
            return
        
        await state.update_data(amount=amount)
        await message.answer("ကျေးဇူးပြု၍ ငွေလွှဲအမှတ်စဉ် (5 လုံး) ကို ထည့်သွင်းပါ။")
        await state.set_state(DepositState.waiting_for_id)
    except ValueError:
        await message.answer("မှန်ကန်သော ငွေပမာဏကို ထည့်သွင်းပါ။ (ဥပမာ - 5000)")

# ၂၅။ ငွေလွှဲအမှတ်စဉ် လက်ခံခြင်းနှင့် Admin သို့ပို့ခြင်း
@dp.message(DepositState.waiting_for_id, F.text)
async def deposit_id(message: types.Message, state: FSMContext):
    payment_id = message.text.strip()
    
    if not re.match(r'^\d{5}$', payment_id):
        await message.answer("ငွေလွှဲအမှတ်စဉ်သည် ဂဏန်း ၅ လုံး ဖြစ်ရပါမည်။ ထပ်မံထည့်သွင်းပါ။")
        return
    
    data = await state.get_data()
    photo_id = data.get('photo_id')
    amount = data.get('amount')
    
    approve_buttons = [
        [
            InlineKeyboardButton(text="✅ အတည်ပြုမယ်", callback_data=f"approve_{message.from_user.id}_{amount}"),
            InlineKeyboardButton(text="❌ ငြင်းပယ်မယ်", callback_data=f"reject_{message.from_user.id}")
        ]
    ]
    approve_keyboard = InlineKeyboardMarkup(inline_keyboard=approve_buttons)
    
    admin_message = (
        f"🔔 <b>ငွေသွင်းရန် တောင်းဆိုချက်</b>\n\n"
        f"👤 အမည်: {message.from_user.full_name}\n"
        f"🆔 User ID: <code>{message.from_user.id}</code>\n"
        f"📝 Username: @{message.from_user.username if message.from_user.username else 'မရှိပါ'}\n"
        f"💰 ငွေပမာဏ: <b>{amount:,} Ks</b>\n"
        f"🔢 ငွေလွှဲအမှတ်စဉ်: <code>{payment_id}</code>"
    )
    
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo_id,
        caption=admin_message,
        reply_markup=approve_keyboard,
        parse_mode="HTML"
    )
    
    await message.answer("သင်၏ငွေသွင်းတောင်းဆိုမှုကို Admin ထံပေးပို့ပြီးပါပြီ။ ခဏအတွင်း အတည်ပြုပေးပါမည်။")
    await state.clear()

# ၂၆။ Admin မှ ငွေသွင်းအတည်ပြု/ငြင်းပယ်ခြင်း
@dp.callback_query(lambda c: c.data.startswith('approve_') or c.data.startswith('reject_'))
async def process_deposit_approval(callback: types.CallbackQuery):
    data = callback.data.split('_')
    action = data[0]
    user_id = data[1]
    
    if action == "approve":
        amount = int(data[2])
        
        user_data = load_user_data()
        if user_id in user_data:
            old_balance = user_data[user_id]['balance']
            user_data[user_id]['balance'] += amount
            
            if 'deposit_history' not in user_data[user_id]:
                user_data[user_id]['deposit_history'] = []
            
            user_data[user_id]['deposit_history'].append({
                "amount": amount,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "admin": callback.from_user.full_name
            })
            save_user_data(user_data)
            
            await bot.send_message(
                chat_id=int(user_id),
                text=f"✅ <b>ငွေသွင်းတောင်းဆိုမှု အတည်ပြုပြီးပါပြီ။</b>\n\n"
                     f"💰 လက်ကျန်အဟောင်း: <b>{old_balance:,} Ks</b>\n"
                     f"💰 လက်ကျန်အသစ်: <b>{user_data[user_id]['balance']:,} Ks</b>",
                parse_mode="HTML"
            )
            
            await callback.message.edit_caption(
                caption=callback.message.caption + f"\n\n✅ <b>အတည်ပြုပြီး - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</b>",
                parse_mode="HTML"
            )
        else:
            await callback.answer("User ကို ရှာမတွေ့ပါ")
    
    elif action == "reject":
        await bot.send_message(
            chat_id=int(user_id),
            text="❌ သင်၏ငွေသွင်းတောင်းဆိုမှုကို ငြင်းပယ်လိုက်ပါသည်။\n"
                 "အကြောင်းအရာကို ပြန်လည်စစ်ဆေးပြီး ထပ်မံကြိုးစားကြည့်ပါ။"
        )
        
        await callback.message.edit_caption(
            caption=callback.message.caption + f"\n\n❌ <b>ငြင်းပယ်လိုက်သည် - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</b>",
            parse_mode="HTML"
        )
    
    await callback.answer()

# ၂၇။ Admin ကိုဆက်သွယ်ရန်
@dp.message(F.text == "📞 Admin ကိုဆက်သွယ်ရန်")
async def contact_admin(message: types.Message):
    contact_text = (
        "📞 <b>Admin ကိုဆက်သွယ်ရန်</b>\n\n"
        "💬 Telegram: @VIPBEE_32\n"
        "⏰ အချိန်: နံနက်၇နာရီ မှ ည ၉ နာရီအထိ"
    )
    await message.answer(contact_text, parse_mode="HTML")

async def main():
    print("Bot is running with Order System and Broadcast Service...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
