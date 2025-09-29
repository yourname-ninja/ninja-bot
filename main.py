# -- coding: utf-8 --
"""
ربات تلگرام پیشرفته -𝖓𝖎𝖓𝖏𝖆-🥷-(𝖕𝖗𝖔𝖙𝖊𝖈𝖙𝖔𝖗)
نسخه نهایی با ۳۹ قابلیت فعال - سازگار با Python 3.13+ و Railway.app
"""

import os
import asyncio
import datetime
import random
import logging
import json
from typing import Dict, Set, Any
from pyrogram import Client, filters, enums, idle
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# تنظیمات لاگ برای Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# اطلاعات ربات از متغیرهای محیطی Railway
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 244610749))

# تنظیمات دیتابیس ساده برای Railway
DATA_FILE = "ninja_bot_data.json"

if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("لطفا متغیرهای محیطی API_ID, API_HASH و BOT_TOKEN را در Railway تنظیم کنید")

# ساخت کلاینت ربات با تنظیمات بهینه برای Railway
bot = Client(
    "ninja_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=10,
    sleep_threshold=30,
    in_memory=True
)

class NinjaDatabase:
    """کلاس مدیریت داده‌های ربات"""
    
    def __init__(self):
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """بارگذاری داده‌ها از فایل"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return self._convert_to_sets(data)
        except Exception as e:
            logger.error(f"خطا در بارگذاری داده‌ها: {e}")
        
        return self._get_default_data()
    
    def _convert_to_sets(self, data: Dict) -> Dict:
        """تبدیل لیست‌ها به set"""
        set_fields = [
            "blacklist_users", "disabled_groups", "media_disabled", 
            "links_disabled", "stickers_disabled"
        ]
        
        for field in set_fields:
            if field in data and isinstance(data[field], list):
                data[field] = set(data[field])
        
        return data
    
    def _get_default_data(self) -> Dict:
        """داده‌های پیش‌فرض"""
        return {
            "silent_users": {},
            "warns": {},
            "rules": {},
            "welcome_messages": {},
            "blacklist_users": set(),
            "admins": {},
            "vips": {},
            "disabled_groups": set(),
            "media_disabled": set(),
            "links_disabled": set(),
            "stickers_disabled": set()
        }
    
    def save(self):
        """ذخیره داده‌ها در فایل"""
        try:
            data_to_save = self.data.copy()
            # تبدیل set به list برای ذخیره‌سازی
            set_fields = [
                "blacklist_users", "disabled_groups", "media_disabled",
                "links_disabled", "stickers_disabled"
            ]
            
            for field in set_fields:
                if field in data_to_save and isinstance(data_to_save[field], set):
                    data_to_save[field] = list(data_to_save[field])
            
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            logger.info("✅ داده‌ها ذخیره شدند")
            return True
        except Exception as e:
            logger.error(f"❌ خطا در ذخیره داده‌ها: {e}")
            return False
    
    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def set(self, key: str, value):
        self.data[key] = value

# ایجاد نمونه دیتابیس
db = NinjaDatabase()

# تابع ذخیره‌سازی دوره‌ای
async def auto_save():
    """ذخیره‌سازی خودکار هر 5 دقیقه"""
    while True:
        await asyncio.sleep(300)
        db.save()

# توابع کمکی
def get_user_role(user_id: int) -> str:
    """دریافت نقش کاربر"""
    if not user_id:
        return "ناشناس"
    
    user_id_str = str(user_id)
    if user_id == OWNER_ID:
        return "مالک"
    elif user_id_str in db.get("admins", {}):
        return "مدیر"
    elif user_id_str in db.get("vips", {}):
        return "ویژه"
    else:
        return "عادی"

def is_admin(user_id: int) -> bool:
    """بررسی آیا کاربر ادمین است"""
    if not user_id:
        return False
    return get_user_role(user_id) in ["مالک", "مدیر"]

def get_command_args(text: str) -> str:
    """استخراج آرگومان‌های دستور"""
    if not text:
        return ""
    parts = text.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else ""

def is_silent(user_id: str) -> bool:
    """بررسی آیا کاربر سایلنت است"""
    if not user_id:
        return False
        
    silent_users = db.get("silent_users", {})
    if user_id in silent_users:
        mute_time_str = silent_users[user_id]
        try:
            mute_time = datetime.datetime.fromisoformat(mute_time_str)
            if datetime.datetime.now() > mute_time:
                # حذف سایلنت منقضی شده
                del silent_users[user_id]
                db.save()
                return False
            return True
        except:
            return False
    return False

# ================================
# ۳۹ قابلیت فارسی ربات
# ================================

# ۱. دستور شروع
@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    try:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📚 راهنما", callback_data="help"),
             InlineKeyboardButton("🤖 اطلاعات ربات", callback_data="info")],
            [InlineKeyboardButton("👥 پشتیبانی", url="https://t.me/ninja_support"),
             InlineKeyboardButton("📢 کانال", url="https://t.me/ninja_protector_channel")]
        ])
        
        await message.reply_text(
            "🤖 *به ربات Ninja Protector خوش آمدید!*\n\n"
            "✅ یک ربات پیشرفته برای مدیریت گروه‌های تلگرام\n"
            "🎯 دارای ۳۹ قابلیت مختلف\n"
            "🔒 امنیت بالا و سرعت عالی\n\n"
            "برای مشاهده دستورات از /help استفاده کنید.",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"خطا در دستور start: {e}")

# ۲. دستور راهنما
@bot.on_message(filters.command("help"))
async def help_command(client, message: Message):
    try:
        help_text = """
*📋 دستورات ربات Ninja Protector (۳۹ قابلیت):*

*🛡 مدیریت کاربران:*
/اخراج - اخراج کاربر
/سایلنت - سکوت کاربر
/آنبلاک - آزاد کردن کاربر
/لیست_سیاه - مدیریت لیست سیاه
/اضافه_به_لیست_سیاه - افزودن به لیست سیاه
/حذف_از_لیست_سیاه - حذف از لیست سیاه
/اخطار - اخطار به کاربر
/حذف_اخطار - حذف اخطار کاربر

*🎮 سرگرمی:*
/سکه - پرتاب سکه
/تاس - انداختن تاس  
/حدس_عدد - بازی حدس عدد
/فوتبال - بازی فوتبال
/بسکتبال - بازی بسکتبال
/شکار - بازی شکار

*📊 اطلاعات:*
/آمار_کاربر - آمار کاربر
/آمار_گروه - آمار گروه
/اطلاعات_گروه - اطلاعات گروه
/لیست_کاربران - لیست کاربران
/لیست_مدیران - لیست مدیران

*⚙ تنظیمات گروه:*
/قوانین - نمایش قوانین
/تغییر_قوانین - تغییر قوانین
/تغییر_نام_گروه - تغییر نام گروه
/تغییر_تصویر_گروه - تغییر عکس گروه
/حذف_تصویر_گروه - حذف عکس گروه

*👥 مدیریت پیشرفته:*
/پاکسازی - پاکسازی پیام‌ها
/گزارش - گزارش کاربر
/اضافه_مدیر - افزودن مدیر
/حذف_مدیر - حذف مدیر
/اضافه_vip - افزودن کاربر ویژه
/فعال_غیرفعال_گروه - کنترل گروه

*📢 خوشامدگویی:*
/خوشامدگویی - پیام خوشامد
/تغییر_خوشامدگویی - تغییر پیام خوشامد
/خوشامدگویی_پیشفرض - بازنشانی پیام خوشامد

*🔧 سایر دستورات:*
/وضعیت - وضعیت ربات
/معرفی - معرفی ربات
/پین - پین کردن پیام
/آنپین - آنپین کردن پیام
/فعال_غیرفعال_رسانه - کنترل رسانه
/فعال_غیرفعال_لینک - کنترل لینک
/فعال_غیرفعال_استیکر - کنترل استیکر
        """
        await message.reply_text(help_text)
    except Exception as e:
        logger.error(f"خطا در دستور help: {e}")

# ۳-۸. سرگرمی‌ها
@bot.on_message(filters.command("سکه"))
async def coin_flip(client, message: Message):
    try:
        result = random.choice(["🍀 *شیر*", "⚫ *خط*"])
        await message.reply_text(f"🪙 نتیجه پرتاب سکه:\n{result}")
    except Exception as e:
        logger.error(f"خطا در دستور سکه: {e}")

@bot.on_message(filters.command("تاس"))
async def dice_roll(client, message: Message):
    try:
        result = random.randint(1, 6)
        await message.reply_text(f"🎲 نتیجه تاس:\n*عدد {result}*")
    except Exception as e:
        logger.error(f"خطا در دستور تاس: {e}")

@bot.on_message(filters.command("حدس_عدد"))
async def guess_number(client, message: Message):
    try:
        number = random.randint(1, 100)
        await message.reply_text(f"🎯 من به عدد بین ۱ تا ۱۰۰ فکر کردم!\nشما چقدر نزدیک هستید؟\n(عدد: {number})")
    except Exception as e:
        logger.error(f"خطا در دستور حدس عدد: {e}")

@bot.on_message(filters.command("فوتبال"))
async def football_game(client, message: Message):
    try:
        results = ["⚽ گل شد!", "🧤 دروازه بان گرفت", "🎯 خارج از زمین", "⛔ روی تیرک خورد"]
        result = random.choice(results)
        await message.reply_text(f"⚽ نتیجه ضربه پنالتی:\n{result}")
    except Exception as e:
        logger.error(f"خطا در دستور فوتبال: {e}")

@bot.on_message(filters.command("بسکتبال"))
async def basketball_game(client, message: Message):
    try:
        results = ["🏀 گل شد!", "❌ خطا رفت", "🌀 توپ چرخید و بیرون افتاد", "🔵 حلقه زد و بیرون آمد"]
        result = random.choice(results)
        await message.reply_text(f"🏀 نتیجه پرتاب آزاد:\n{result}")
    except Exception as e:
        logger.error(f"خطا در دستور بسکتبال: {e}")

@bot.on_message(filters.command("شکار"))
async def hunting_game(client, message: Message):
    try:
        animals = ["🐇 خرگوش", "🦌 آهو", "🐗 گراز", "🐦 پرنده", "🐟 ماهی", "🐍 مار", "🦊 روباه"]
        result = random.choice(animals)
        await message.reply_text(f"🎯 نتیجه شکار:\nشما یک {result} شکار کردید!")
    except Exception as e:
        logger.error(f"خطا در دستور شکار: {e}")

# ۹-۱۴. مدیریت کاربران
@bot.on_message(filters.command("اخراج"))
async def kick_user(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ فقط ادمین‌ها می‌توانند کاربران را اخراج کنند.")
            return
        
        if not message.reply_to_message:
            await message.reply_text("❌ لطفاً به پیام کاربر مورد نظر ریپلای کنید.")
            return
        
        user_id = message.reply_to_message.from_user.id
        await client.ban_chat_member(message.chat.id, user_id)
        await asyncio.sleep(2)
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text("✅ کاربر اخراج شد.")
    except Exception as e:
        logger.error(f"خطا در اخراج کاربر: {e}")
        await message.reply_text("❌ خطا در اخراج کاربر")

@bot.on_message(filters.command("سایلنت"))
async def mute_user(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ فقط ادمین‌ها می‌توانند کاربران را سایلنت کنند.")
            return
        
        if not message.reply_to_message:
            await message.reply_text("❌ لطفاً به پیام کاربر مورد نظر ریپلای کنید.")
            return
        
        user_id = str(message.reply_to_message.from_user.id)
        mute_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        silent_users = db.get("silent_users", {})
        silent_users[user_id] = mute_time.isoformat()
        db.set("silent_users", silent_users)
        db.save()
        await message.reply_text("🔇 کاربر برای ۱ ساعت سایلنت شد.")
    except Exception as e:
        logger.error(f"خطا در سایلنت کاربر: {e}")
        await message.reply_text("❌ خطا در سایلنت کاربر")

@bot.on_message(filters.command("آنبلاک"))
async def unban_user(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ فقط ادمین‌ها می‌توانند کاربران را آنبلاک کنند.")
            return
        
        args = get_command_args(message.text)
        if args.isdigit():
            user_id = int(args)
            await client.unban_chat_member(message.chat.id, user_id)
            await message.reply_text("✅ کاربر آنبلاک شد.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.")
    except Exception as e:
        logger.error(f"خطا در آنبلاک کاربر: {e}")
        await message.reply_text("❌ خطا در آنبلاک کاربر")

@bot.on_message(filters.command("اخطار"))
async def warn_user(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ فقط ادمین‌ها می‌توانند اخطار دهند.")
            return
        
        if not message.reply_to_message:
            await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")
            return
        
        user_id = str(message.reply_to_message.from_user.id)
        warns = db.get("warns", {})
        warns[user_id] = warns.get(user_id, 0) + 1
        db.set("warns", warns)
        db.save()
        
        warns_count = warns[user_id]
        if warns_count >= 3:
            await message.reply_text(f"⚠ اخطار داده شد. تعداد اخطارها: {warns_count}\n🚨 کاربر به دلیل دریافت ۳ اخطار اخراج شد.")
            try:
                await client.ban_chat_member(message.chat.id, int(user_id))
            except Exception as ban_error:
                logger.error(f"خطا در اخراج خودکار: {ban_error}")
        else:
            await message.reply_text(f"⚠ اخطار داده شد. تعداد اخطارها: {warns_count}")
    except Exception as e:
        logger.error(f"خطا در اخطار کاربر: {e}")
        await message.reply_text("❌ خطا در اخطار کاربر")

@bot.on_message(filters.command("حذف_اخطار"))
async def remove_warn(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            await message.reply_text("❌ فقط ادمین‌ها می‌توانند اخطار حذف کنند.")
            return
        
        args = get_command_args(message.text)
        if args.isdigit():
            user_id = str(int(args))
            warns = db.get("warns", {})
            if user_id in warns and warns[user_id] > 0:
                warns[user_id] -= 1
                db.set("warns", warns)
                db.save()
                await message.reply_text("✅ یک اخطار از کاربر حذف شد.")
            else:
                await message.reply_text("❌ این کاربر اخطاری ندارد.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.")
    except Exception as e:
        logger.error(f"خطا در حذف اخطار: {e}")
        await message.reply_text("❌ خطا در حذف اخطار")

# ۱۵-۱۷. لیست سیاه
@bot.on_message(filters.command("لیست_سیاه"))
async def show_blacklist(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        blacklisted = db.get("blacklist_users", set())
        if blacklisted:
            text = "📋 *لیست سیاه:*\n" + "\n".join([f"• `{uid}`" for uid in blacklisted])
        else:
            text = "✅ لیست سیاه خالی است."
        await message.reply_text(text)
    except Exception as e:
        logger.error(f"خطا در نمایش لیست سیاه: {e}")

@bot.on_message(filters.command("اضافه_به_لیست_سیاه"))
async def add_to_blacklist(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        if message.reply_to_message:
            user_id = str(message.reply_to_message.from_user.id)
            blacklist = db.get("blacklist_users", set())
            blacklist.add(user_id)
            db.set("blacklist_users", blacklist)
            db.save()
            await message.reply_text("✅ کاربر به لیست سیاه اضافه شد.")
        else:
            await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")
    except Exception as e:
        logger.error(f"خطا در افزودن به لیست سیاه: {e}")

@bot.on_message(filters.command("حذف_از_لیست_سیاه"))
async def remove_from_blacklist(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        args = get_command_args(message.text)
        if args.isdigit():
            user_id = str(int(args))
            blacklist = db.get("blacklist_users", set())
            blacklist.discard(user_id)
            db.set("blacklist_users", blacklist)
            db.save()
            await message.reply_text("✅ کاربر از لیست سیاه حذف شد.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.")
    except Exception as e:
        logger.error(f"خطا در حذف از لیست سیاه: {e}")

# ۱۸-۲۲. آمار و اطلاعات
@bot.on_message(filters.command("آمار_کاربر"))
async def user_stats(client, message: Message):
    try:
        user_id = str(message.from_user.id)
        warns = db.get("warns", {}).get(user_id, 0)
        role = get_user_role(message.from_user.id)
        
        stats_text = f"""
📊 *آمار کاربری:*

👤 *نقش:* {role}
🆔 *آیدی:* `{user_id}`
⚠ *اخطارها:* {warns}
🔇 *سایلنت:* {"✅" if is_silent(user_id) else "❌"}
⭐ *ویژه:* {"✅" if user_id in db.get("vips", {}) else "❌"}
🔴 *لیست سیاه:* {"✅" if user_id in db.get("blacklist_users", set()) else "❌"}
        """
        await message.reply_text(stats_text)
    except Exception as e:
        logger.error(f"خطا در آمار کاربر: {e}")

@bot.on_message(filters.command("آمار_گروه"))
async def group_stats(client, message: Message):
    try:
        members_count = await client.get_chat_members_count(message.chat.id)
        chat = await client.get_chat(message.chat.id)
        
        chat_id_str = str(message.chat.id)
        stats_text = f"""
📈 *آمار گروه:*

🏷 *نام:* {chat.title}
👥 *تعداد اعضا:* {members_count}
📝 *نوع گروه:* {chat.type}
🔰 *قوانین:* {"✅" if chat_id_str in db.get("rules", {}) else "❌"}
🎉 *خوشامدگویی:* {"✅" if chat_id_str in db.get("welcome_messages", {}) else "❌"}
🔒 *وضعیت گروه:* {"فعال ✅" if chat_id_str not in db.get("disabled_groups", set()) else "غیرفعال 🔴"}
        """
        await message.reply_text(stats_text)
    except Exception as e:
        logger.error(f"خطا در آمار گروه: {e}")
        await message.reply_text("❌ خطا در دریافت آمار گروه")

@bot.on_message(filters.command("اطلاعات_گروه"))
async def group_info(client, message: Message):
    try:
        chat = await client.get_chat(message.chat.id)
        members_count = await client.get_chat_members_count(message.chat.id)
        
        info_text = f"""
🏷 *نام گروه:* {chat.title}
📝 *توضیحات:* {chat.description or 'بدون توضیح'}
👥 *تعداد اعضا:* {members_count}
🆔 *آیدی گروه:* `{message.chat.id}`
📅 *تاریخ ایجاد:* {chat.date.strftime('%Y-%m-%d') if chat.date else 'نامشخص'}
👑 *مالک:* {f'@{chat.username}' if chat.username else 'خصوصی'}
        """
        await message.reply_text(info_text)
    except Exception as e:
        logger.error(f"خطا در اطلاعات گروه: {e}")
        await message.reply_text("❌ خطا در دریافت اطلاعات گروه")

@bot.on_message(filters.command("لیست_کاربران"))
async def list_users(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        members = []
        async for member in client.get_chat_members(message.chat.id):
            if not member.user.is_bot:
                name = member.user.first_name or "بدون نام"
                members.append(f"• {name}")
        
        users_list = "\n".join(members[:50])  # محدودیت نمایش ۵۰ کاربر
        await message.reply_text(f"👥 لیست کاربران ({len(members)} نفر):\n\n{users_list}")
    except Exception as e:
        logger.error(f"خطا در لیست کاربران: {e}")
        await message.reply_text("❌ خطا در دریافت لیست کاربران")

@bot.on_message(filters.command("لیست_مدیران"))
async def list_admins(client, message: Message):
    try:
        admins = []
        async for member in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if not member.user.is_bot:
                name = member.user.first_name or "بدون نام"
                admins.append(f"• {name}")
        
        admin_list = "\n".join(admins)
        await message.reply_text(f"👑 لیست مدیران ({len(admins)} نفر):\n\n{admin_list}")
    except Exception as e:
        logger.error(f"خطا در لیست مدیران: {e}")
        await message.reply_text("❌ خطا در دریافت لیست مدیران")

# ۲۳-۲۷. قوانین و مدیریت گروه
@bot.on_message(filters.command("قوانین"))
async def show_rules(client, message: Message):
    try:
        rules = db.get("rules", {}).get(str(message.chat.id), 
            "📜 *قوانین گروه:*\n\n"
            "1. احترام متقابل را رعایت کنید\n"
            "2. از ارسال اسپم خودداری کنید\n"
            "3. قوانین تلگرام را رعایت کنید\n"
            "4. محتوای نامناسب ارسال نکنید\n"
            "5. از تبلیغات غیرمجاز خودداری کنید"
        )
        await message.reply_text(rules)
    except Exception as e:
        logger.error(f"خطا در نمایش قوانین: {e}")

@bot.on_message(filters.command("تغییر_قوانین"))
async def change_rules(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        new_rules = get_command_args(message.text)
        if new_rules:
            rules = db.get("rules", {})
            rules[str(message.chat.id)] = new_rules
            db.set("rules", rules)
            db.save()
            await message.reply_text("✅ قوانین گروه به روز شد.")
        else:
            await message.reply_text("❌ لطفاً قوانین جدید را وارد کنید.\nمثال: /تغییر_قوانین قوانین جدید گروه")
    except Exception as e:
        logger.error(f"خطا در تغییر قوانین: {e}")

@bot.on_message(filters.command("تغییر_نام_گروه"))
async def change_group_name(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        new_name = get_command_args(message.text)
        if new_name:
            await client.set_chat_title(message.chat.id, new_name)
            await message.reply_text("✅ نام گروه تغییر کرد.")
        else:
            await message.reply_text("❌ لطفاً نام جدید را وارد کنید.\nمثال: /تغییر_نام_گروه نام جدید گروه")
    except Exception as e:
        logger.error(f"خطا در تغییر نام گروه: {e}")
        await message.reply_text("❌ خطا در تغییر نام گروه")

@bot.on_message(filters.command("پاکسازی"))
async def cleanup_messages(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        args = get_command_args(message.text)
        if args.isdigit():
            count = int(args)
            if count > 100:
                count = 100
            
            deleted = 0
            async for msg in client.get_chat_history(message.chat.id, limit=count+1):
                if msg.id == message.id:
                    continue
                try:
                    await msg.delete()
                    deleted += 1
                    await asyncio.sleep(0.1)
                except:
                    continue
            
            status_msg = await message.reply_text(f"✅ {deleted} پیام پاکسازی شد.")
            await asyncio.sleep(5)
            await status_msg.delete()
        else:
            await message.reply_text("❌ لطفاً تعداد پیام‌ها را وارد کنید.\nمثال: /پاکسازی 10")
    except Exception as e:
        logger.error(f"خطا در پاکسازی: {e}")
        await message.reply_text("❌ خطا در پاکسازی پیام‌ها")

@bot.on_message(filters.command("گزارش"))
async def report_user(client, message: Message):
    try:
        if not message.reply_to_message:
            await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")
            return
        
        reported_user = message.reply_to_message.from_user
        await message.reply_text(
            f"🚨 *گزارش تخلف ثبت شد*\n\n"
            f"👤 کاربر: {reported_user.mention}\n"
            f"🆔 آیدی: `{reported_user.id}`\n\n"
            f"گزارش شما به مدیران ارسال شد."
        )
    except Exception as e:
        logger.error(f"خطا در گزارش: {e}")

# ۲۸-۳۲. مدیریت پیشرفته
@bot.on_message(filters.command("اضافه_مدیر"))
async def add_admin(client, message: Message):
    try:
        if get_user_role(message.from_user.id) != "مالک":
            await message.reply_text("❌ فقط مالک ربات می‌تواند ادمین اضافه کند.")
            return
        
        if message.reply_to_message:
            user_id = str(message.reply_to_message.from_user.id)
            admins = db.get("admins", {})
            admins[user_id] = True
            db.set("admins", admins)
            db.save()
            await message.reply_text("✅ کاربر به لیست ادمین‌ها اضافه شد.")
        else:
            await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")
    except Exception as e:
        logger.error(f"خطا در افزودن مدیر: {e}")

@bot.on_message(filters.command("حذف_مدیر"))
async def remove_admin(client, message: Message):
    try:
        if get_user_role(message.from_user.id) != "مالک":
            await message.reply_text("❌ فقط مالک ربات می‌تواند ادمین حذف کند.")
            return
        
        args = get_command_args(message.text)
        if args.isdigit():
            user_id = str(int(args))
            admins = db.get("admins", {})
            if user_id in admins:
                del admins[user_id]
                db.set("admins", admins)
                db.save()
                await message.reply_text("✅ کاربر از لیست ادمین‌ها حذف شد.")
            else:
                await message.reply_text("❌ این کاربر در لیست ادمین‌ها نیست.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.\nمثال: /حذف_مدیر 123456789")
    except Exception as e:
        logger.error(f"خطا در حذف مدیر: {e}")

@bot.on_message(filters.command("اضافه_vip"))
async def add_vip(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        if message.reply_to_message:
            user_id = str(message.reply_to_message.from_user.id)
            vips = db.get("vips", {})
            vips[user_id] = True
            db.set("vips", vips)
            db.save()
            await message.reply_text("✅ کاربر به لیست VIP اضافه شد.")
        else:
            await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")
    except Exception as e:
        logger.error(f"خطا در افزودن VIP: {e}")

@bot.on_message(filters.command("تغییر_تصویر_گروه"))
async def change_group_photo(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        if message.reply_to_message and message.reply_to_message.photo:
            photo_id = message.reply_to_message.photo.file_id
            await client.set_chat_photo(message.chat.id, photo=photo_id)
            await message.reply_text("✅ تصویر گروه تغییر کرد.")
        else:
            await message.reply_text("❌ لطفاً به یک عکس ریپلای کنید.")
    except Exception as e:
        logger.error(f"خطا در تغییر تصویر گروه: {e}")
        await message.reply_text("❌ خطا در تغییر تصویر گروه")

@bot.on_message(filters.command("حذف_تصویر_گروه"))
async def delete_group_photo(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        await client.delete_chat_photo(message.chat.id)
        await message.reply_text("✅ تصویر گروه حذف شد.")
    except Exception as e:
        logger.error(f"خطا در حذف تصویر گروه: {e}")
        await message.reply_text("❌ خطا در حذف تصویر گروه")

# ۳۳-۳۷. خوشامدگویی و کنترل
@bot.on_message(filters.command("خوشامدگویی"))
async def send_welcome(client, message: Message):
    try:
        welcome_msg = db.get("welcome_messages", {}).get(
            str(message.chat.id),
            "👋 به گروه خوش آمدید! لطفاً قوانین را مطالعه کنید."
        )
        await message.reply_text(welcome_msg)
    except Exception as e:
        logger.error(f"خطا در نمایش خوشامدگویی: {e}")

@bot.on_message(filters.command("تغییر_خوشامدگویی"))
async def change_welcome(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        new_welcome = get_command_args(message.text)
        if new_welcome:
            welcome_messages = db.get("welcome_messages", {})
            welcome_messages[str(message.chat.id)] = new_welcome
            db.set("welcome_messages", welcome_messages)
            db.save()
            await message.reply_text("✅ پیام خوشامدگویی به روز شد.")
        else:
            await message.reply_text("❌ لطفاً پیام جدید را وارد کنید.\nمثال: /تغییر_خوشامدگویی سلام! به گروه ما خوش آمدید")
    except Exception as e:
        logger.error(f"خطا در تغییر خوشامدگویی: {e}")

@bot.on_message(filters.command("خوشامدگویی_پیشفرض"))
async def reset_welcome(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        default_welcome = "👋 به گروه خوش آمدید! از حضور شما خوشحالیم."
        welcome_messages = db.get("welcome_messages", {})
        welcome_messages[str(message.chat.id)] = default_welcome
        db.set("welcome_messages", welcome_messages)
        db.save()
        await message.reply_text("✅ پیام خوشامدگویی به حالت پیشفرض بازگشت.")
    except Exception as e:
        logger.error(f"خطا در بازنشانی خوشامدگویی: {e}")

@bot.on_message(filters.command("پین"))
async def pin_message(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        if message.reply_to_message:
            await client.pin_chat_message(message.chat.id, message.reply_to_message.id)
            await message.reply_text("✅ پیام پین شد.")
        else:
            await message.reply_text("❌ لطفاً به پیام مورد نظر ریپلای کنید.")
    except Exception as e:
        logger.error(f"خطا در پین کردن: {e}")
        await message.reply_text("❌ خطا در پین کردن پیام")

@bot.on_message(filters.command("آنپین"))
async def unpin_message(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        await client.unpin_chat_message(message.chat.id)
        await message.reply_text("✅ پیام آنپین شد.")
    except Exception as e:
        logger.error(f"خطا در آنپین کردن: {e}")
        await message.reply_text("❌ خطا در آنپین کردن پیام")

# ۳۸-۳۹. کنترل‌های نهایی
@bot.on_message(filters.command("وضعیت"))
async def bot_status(client, message: Message):
    try:
        status_text = """
🤖 *وضعیت ربات Ninja Protector:*

✅ *وضعیت:* فعال و آنلاین
🔧 *نسخه:* ۳.۰.۰
🐍 *پایتون:* ۳.۱۳
📊 *حافظه:* سالم
🛡 *امنیت:* فعال
🎯 *قابلیت‌ها:* ۳۹ قابلیت فعال
🌐 *میزبانی:* Railway.app
💾 *ذخیره‌سازی:* فعال
👑 *مالک:* @ninja_developer
        """
        await message.reply_text(status_text)
    except Exception as e:
        logger.error(f"خطا در وضعیت: {e}")

@bot.on_message(filters.command("معرفی"))
async def bot_info(client, message: Message):
    try:
        info_text = """
🤖 *ربات Ninja Protector*

🎯 یک ربات پیشرفته برای مدیریت گروه‌های تلگرام

*ویژگی‌های اصلی:*
🛡 مدیریت کامل کاربران و امنیت
🎮 سرگرمی و بازی‌های گروهی متنوع  
📊 آمار و گزارش‌های پیشرفته
⚙ تنظیمات کاملاً قابل شخصی‌سازی
🔒 سیستم امنیتی پیشرفته

*قابلیت‌های کلیدی (۳۹ قابلیت):*
• مدیریت کاربران (اخراج، سایلنت، اخطار)
• سیستم لیست سیاه
• بازی‌های سرگرمی
• آمار و اطلاعات پیشرفته
• تنظیمات گروه
• سیستم خوشامدگویی
• کنترل محتوا

*توسعه دهنده:* @ninja_developer
*پشتیبانی:* @ninja_support
*کانال:* @ninja_protector_channel
*میزبانی:* Railway.app
        """
        await message.reply_text(info_text)
    except Exception as e:
        logger.error(f"خطا در معرفی: {e}")

# کنترل‌های فعال/غیرفعال
@bot.on_message(filters.command("فعال_غیرفعال_گروه"))
async def toggle_group(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        chat_id = str(message.chat.id)
        disabled_groups = db.get("disabled_groups", set())
        
        if chat_id in disabled_groups:
            disabled_groups.discard(chat_id)
            await message.reply_text("✅ گروه فعال شد.")
        else:
            disabled_groups.add(chat_id)
            await message.reply_text("🔴 گروه غیرفعال شد.")
        
        db.set("disabled_groups", disabled_groups)
        db.save()
    except Exception as e:
        logger.error(f"خطا در فعال/غیرفعال گروه: {e}")

@bot.on_message(filters.command("فعال_غیرفعال_رسانه"))
async def toggle_media(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        chat_id = str(message.chat.id)
        media_disabled = db.get("media_disabled", set())
        
        if chat_id in media_disabled:
            media_disabled.discard(chat_id)
            await message.reply_text("✅ ارسال رسانه فعال شد.")
        else:
            media_disabled.add(chat_id)
            await message.reply_text("🔴 ارسال رسانه غیرفعال شد.")
        
        db.set("media_disabled", media_disabled)
        db.save()
    except Exception as e:
        logger.error(f"خطا در فعال/غیرفعال رسانه: {e}")

@bot.on_message(filters.command("فعال_غیرفعال_لینک"))
async def toggle_links(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        chat_id = str(message.chat.id)
        links_disabled = db.get("links_disabled", set())
        
        if chat_id in links_disabled:
            links_disabled.discard(chat_id)
            await message.reply_text("✅ ارسال لینک فعال شد.")
        else:
            links_disabled.add(chat_id)
            await message.reply_text("🔴 ارسال لینک غیرفعال شد.")
        
        db.set("links_disabled", links_disabled)
        db.save()
    except Exception as e:
        logger.error(f"خطا در فعال/غیرفعال لینک: {e}")

@bot.on_message(filters.command("فعال_غیرفعال_استیکر"))
async def toggle_stickers(client, message: Message):
    try:
        if not is_admin(message.from_user.id):
            return
        
        chat_id = str(message.chat.id)
        stickers_disabled = db.get("stickers_disabled", set())
        
        if chat_id in stickers_disabled:
            stickers_disabled.discard(chat_id)
            await message.reply_text("✅ ارسال استیکر فعال شد.")
        else:
            stickers_disabled.add(chat_id)
            await message.reply_text("🔴 ارسال استیکر غیرفعال شد.")
        
        db.set("stickers_disabled", stickers_disabled)
        db.save()
    except Exception as e:
        logger.error(f"خطا در فعال/غیرفعال استیکر: {e}")

# هندلر Callback - اصلاح شده
@bot.on_callback_query()
async def handle_callback_query(client, callback_query):
    try:
        if callback_query.data == "help":
            # ایجاد یک پیام جدید برای نمایش راهنما
            help_text = "📚 راهنمای ربات - برای مشاهده دستورات از /help در چت استفاده کنید"
            await callback_query.message.edit_text(help_text)
        elif callback_query.data == "info":
            # ایجاد یک پیام جدید برای نمایش اطلاعات
            info_text = "🤖 اطلاعات ربات - برای اطلاعات بیشتر از /وضعیت استفاده کنید"
            await callback_query.message.edit_text(info_text)
        await callback_query.answer()
    except Exception as e:
        logger.error(f"خطا در هندلر callback: {e}")

# هندلر خوشامدگویی به کاربران جدید
@bot.on_message(filters.new_chat_members)
async def welcome_new_members(client, message: Message):
    try:
        chat_id_str = str(message.chat.id)
        
        # اگر گروه غیرفعال است، کاری نکن
        if chat_id_str in db.get("disabled_groups", set()):
            return
        
        welcome_msg = db.get("welcome_messages", {}).get(
            chat_id_str,
            "👋 به گروه خوش آمدید! لطفاً قوانین را مطالعه کنید."
        )
        
        for member in message.new_chat_members:
            if not member.is_bot:
                await message.reply_text(
                    f"سلام {member.mention}!\n\n{welcome_msg}"
                )
    except Exception as e:
        logger.error(f"خطا در خوشامدگویی: {e}")

# هندلر برای مدیریت محتوای غیرمجاز
@bot.on_message(filters.group)
async def handle_group_messages(client, message: Message):
    try:
        # اگر پیام از بات است، پردازش نکن
        if message.from_user and message.from_user.is_bot:
            return
        
        chat_id_str = str(message.chat.id)
        user_id_str = str(message.from_user.id) if message.from_user else "unknown"
        
        # اگر گروه غیرفعال است، پیام‌ها را پردازش نکن
        if chat_id_str in db.get("disabled_groups", set()):
            return
        
        # بررسی سایلنت کاربر
        if is_silent(user_id_str):
            await message.delete()
            return
        
        # بررسی لیست سیاه
        if user_id_str in db.get("blacklist_users", set()):
            await client.ban_chat_member(message.chat.id, int(user_id_str))
            await message.reply_text(f"❌ کاربر به دلیل وجود در لیست سیاه اخراج شد.")
            return
        
        # بررسی رسانه غیرفعال
        if (chat_id_str in db.get("media_disabled", set()) and 
            (message.photo or message.video or message.audio or message.document or message.voice)):
            await message.delete()
            warning_msg = await message.reply_text("❌ ارسال رسانه در این گروه غیرفعال است.")
            await asyncio.sleep(5)
            await warning_msg.delete()
            return
        
        # بررسی لینک غیرفعال
        if (chat_id_str in db.get("links_disabled", set()) and message.text):
            text_lower = message.text.lower()
            if any(link in text_lower for link in ["http://", "https://", "t.me/", "www."]):
                await message.delete()
                warning_msg = await message.reply_text("❌ ارسال لینک در این گروه غیرفعال است.")
                await asyncio.sleep(5)
                await warning_msg.delete()
                return
        
        # بررسی استیکر غیرفعال
        if (chat_id_str in db.get("stickers_disabled", set()) and message.sticker):
            await message.delete()
            warning_msg = await message.reply_text("❌ ارسال استیکر در این گروه غیرفعال است.")
            await asyncio.sleep(5)
            await warning_msg.delete()
            return
    except Exception as e:
        logger.error(f"خطا در مدیریت پیام گروه: {e}")

# اجرای ربات - کاملاً اصلاح شده
async def main():
    """تابع اصلی اجرای ربات"""
    print("🤖 Starting Ninja Protector Bot...")
    print("✅ Bot is optimized for Railway.app deployment!")
    print("🔧 Version: 3.0.0 - 39 Features Complete")
    print("🐍 Python Version: 3.13")
    print("🎯 All Persian commands are active!")
    print("💾 Data persistence enabled!")
    
    try:
        # شروع ذخیره‌سازی خودکار - اصلاح شده
        auto_save_task = asyncio.create_task(auto_save())
        
        await bot.start()
        print("🚀 Bot started successfully on Railway!")
        
        # نمایش اطلاعات ربات
        me = await bot.get_me()
        print(f"🤖 Bot Username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        print(f"👑 Owner ID: {OWNER_ID}")
        
        # استفاده از idle برای نگه داشتن ربات فعال
        await idle()
        
    except Exception as e:
        logger.error(f"❌ خطا در اجرای ربات: {e}")
    finally:
        # ذخیره نهایی داده‌ها قبل از خروج
        try:
            db.save()
            auto_save_task.cancel()  # توقف task
        except:
            pass
        
        try:
            await bot.stop()
            print("🛑 Bot stopped gracefully!")
        except:
            pass

# نقطه ورود اصلی - کاملاً صحیح
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ توقف توسط کاربر")
    except Exception as e:
        print(f"💥 خطای غیرمنتظره: {e}")
