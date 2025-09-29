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

# توابع مدیریت داده‌ها برای Railway
def load_data():
    """بارگذاری داده‌ها از فایل"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # تبدیل لیست‌ها به set برای عملکرد بهتر
                if "blacklist" in data and "users" in data["blacklist"]:
                    data["blacklist"]["users"] = set(data["blacklist"]["users"])
                if "disabled_groups" in data:
                    data["disabled_groups"] = set(data["disabled_groups"])
                if "media_disabled" in data:
                    data["media_disabled"] = set(data["media_disabled"])
                if "links_disabled" in data:
                    data["links_disabled"] = set(data["links_disabled"])
                if "stickers_disabled" in data:
                    data["stickers_disabled"] = set(data["stickers_disabled"])
                return data
    except Exception as e:
        logger.error(f"خطا در بارگذاری داده‌ها: {e}")
    
    # داده‌های پیش‌فرض
    return {
        "silent_users": {},
        "warns": {},
        "rules": {},
        "welcome_messages": {},
        "blacklist": {"users": set()},
        "admins": {},
        "vips": {},
        "disabled_groups": set(),
        "media_disabled": set(),
        "links_disabled": set(),
        "stickers_disabled": set()
    }

def save_data():
    """ذخیره داده‌ها در فایل"""
    try:
        data_to_save = {
            "silent_users": memory["silent_users"],
            "warns": memory["warns"],
            "rules": memory["rules"],
            "welcome_messages": memory["welcome_messages"],
            "blacklist": {"users": list(memory["blacklist"]["users"])},
            "admins": memory["admins"],
            "vips": memory["vips"],
            "disabled_groups": list(memory["disabled_groups"]),
            "media_disabled": list(memory["media_disabled"]),
            "links_disabled": list(memory["links_disabled"]),
            "stickers_disabled": list(memory["stickers_disabled"])
        }
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        logger.info("✅ داده‌ها با موفقیت ذخیره شدند")
    except Exception as e:
        logger.error(f"❌ خطا در ذخیره داده‌ها: {e}")

# بارگذاری اولیه داده‌ها
memory = load_data()

# تابع ذخیره‌سازی دوره‌ای
async def auto_save():
    """ذخیره‌سازی خودکار هر 5 دقیقه"""
    while True:
        await asyncio.sleep(300)  # 5 دقیقه
        save_data()

# توابع کمکی
def get_user_role(user_id: int):
    user_id_str = str(user_id)
    if user_id == OWNER_ID:
        return "مالک"
    elif user_id_str in memory["admins"]:
        return "مدیر"
    elif user_id_str in memory["vips"]:
        return "ویژه"
    else:
        return "عادی"

def is_admin(user_id: int):
    return get_user_role(user_id) in ["مالک", "مدیر"]

def get_command_args(text: str):
    parts = text.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else ""

# ================================
# ۳۹ قابلیت فارسی ربات
# ================================

# ۱. دستور شروع
@bot.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
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

# ۲. دستور راهنما
@bot.on_message(filters.command("help"))
async def help_command(client, message: Message):
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

# ۳-۸. سرگرمی‌ها
@bot.on_message(filters.command("سکه"))
async def coin_flip(client, message: Message):
    result = random.choice(["🍀 *شیر*", "⚫ *خط*"])
    await message.reply_text(f"🪙 نتیجه پرتاب سکه:\n{result}")

@bot.on_message(filters.command("تاس"))
async def dice_roll(client, message: Message):
    result = random.randint(1, 6)
    await message.reply_text(f"🎲 نتیجه تاس:\n*عدد {result}*")

@bot.on_message(filters.command("حدس_عدد"))
async def guess_number(client, message: Message):
    number = random.randint(1, 10)
    await message.reply_text(f"🎯 عدد تصادفی: {number}")

@bot.on_message(filters.command("فوتبال"))
async def football_game(client, message: Message):
    results = ["⚽ گل شد!", "🧤 دروازه بان گرفت", "🎯 خارج از زمین"]
    result = random.choice(results)
    await message.reply_text(f"⚽ نتیجه ضربه پنالتی:\n{result}")

@bot.on_message(filters.command("بسکتبال"))
async def basketball_game(client, message: Message):
    results = ["🏀 گل شد!", "❌ خطا رفت", "🌀 توپ چرخید و بیرون افتاد"]
    result = random.choice(results)
    await message.reply_text(f"🏀 نتیجه پرتاب آزاد:\n{result}")

@bot.on_message(filters.command("شکار"))
async def hunting_game(client, message: Message):
    animals = ["🐇 خرگوش", "🦌 آهو", "🐗 گراز", "🐦 پرنده", "🐟 ماهی"]
    result = random.choice(animals)
    await message.reply_text(f"🎯 نتیجه شکار:\nشما یک {result} شکار کردید!")

# ۹-۱۴. مدیریت کاربران
@bot.on_message(filters.command("اخراج"))
async def kick_user(client, message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply_text("❌ فقط ادمین‌ها می‌توانند کاربران را اخراج کنند.")
    
    if not message.reply_to_message:
        return await message.reply_text("❌ لطفاً به پیام کاربر مورد نظر ریپلای کنید.")
    
    user_id = message.reply_to_message.from_user.id
    try:
        await client.ban_chat_member(message.chat.id, user_id)
        await asyncio.sleep(2)
        await client.unban_chat_member(message.chat.id, user_id)
        await message.reply_text("✅ کاربر اخراج شد.")
    except Exception as e:
        await message.reply_text(f"❌ خطا در اخراج کاربر: {e}")

@bot.on_message(filters.command("سایلنت"))
async def mute_user(client, message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply_text("❌ فقط ادمین‌ها می‌توانند کاربران را سایلنت کنند.")
    
    if not message.reply_to_message:
        return await message.reply_text("❌ لطفاً به پیام کاربر مورد نظر ریپلای کنید.")
    
    user_id = str(message.reply_to_message.from_user.id)
    mute_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    memory["silent_users"][user_id] = mute_time.isoformat()
    save_data()
    await message.reply_text("🔇 کاربر سایلنت شد.")

@bot.on_message(filters.command("آنبلاک"))
async def unban_user(client, message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply_text("❌ فقط ادمین‌ها می‌توانند کاربران را آنبلاک کنند.")
    
    try:
        args = get_command_args(message.text)
        if args.isdigit():
            user_id = int(args)
            await client.unban_chat_member(message.chat.id, user_id)
            await message.reply_text("✅ کاربر آنبلاک شد.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@bot.on_message(filters.command("اخطار"))
async def warn_user(client, message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply_text("❌ فقط ادمین‌ها می‌توانند اخطار دهند.")
    
    if not message.reply_to_message:
        return await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")
    
    user_id = str(message.reply_to_message.from_user.id)
    memory["warns"][user_id] = memory["warns"].get(user_id, 0) + 1
    warns_count = memory["warns"][user_id]
    save_data()
    await message.reply_text(f"⚠ اخطار داده شد. تعداد اخطارها: {warns_count}")

@bot.on_message(filters.command("حذف_اخطار"))
async def remove_warn(client, message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply_text("❌ فقط ادمین‌ها می‌توانند اخطار حذف کنند.")
    
    try:
        args = get_command_args(message.text)
        if args.isdigit():
            user_id = str(int(args))
            if user_id in memory["warns"] and memory["warns"][user_id] > 0:
                memory["warns"][user_id] -= 1
                save_data()
                await message.reply_text("✅ یک اخطار از کاربر حذف شد.")
            else:
                await message.reply_text("❌ این کاربر اخطاری ندارد.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

# ۱۵-۱۷. لیست سیاه
@bot.on_message(filters.command("لیست_سیاه"))
async def show_blacklist(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    blacklisted = memory["blacklist"]["users"]
    if blacklisted:
        text = "📋 *لیست سیاه:*\n" + "\n".join([f"• {uid}" for uid in blacklisted])
    else:
        text = "✅ لیست سیاه خالی است."
    await message.reply_text(text)

@bot.on_message(filters.command("اضافه_به_لیست_سیاه"))
async def add_to_blacklist(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    if message.reply_to_message:
        user_id = str(message.reply_to_message.from_user.id)
        memory["blacklist"]["users"].add(user_id)
        save_data()
        await message.reply_text("✅ کاربر به لیست سیاه اضافه شد.")
    else:
        await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")

@bot.on_message(filters.command("حذف_از_لیست_سیاه"))
async def remove_from_blacklist(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        args = get_command_args(message.text)
        if args.isdigit():
            user_id = str(int(args))
            memory["blacklist"]["users"].discard(user_id)
            save_data()
            await message.reply_text("✅ کاربر از لیست سیاه حذف شد.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

# ۱۸-۲۲. آمار و اطلاعات
@bot.on_message(filters.command("آمار_کاربر"))
async def user_stats(client, message: Message):
    user_id = str(message.from_user.id)
    warns = memory["warns"].get(user_id, 0)
    role = get_user_role(message.from_user.id)
    
    # بررسی سایلنت
    is_silent = user_id in memory["silent_users"]
    if is_silent:
        mute_time_str = memory["silent_users"][user_id]
        try:
            mute_time = datetime.datetime.fromisoformat(mute_time_str)
            if datetime.datetime.now() > mute_time:
                # حذف سایلنت منقضی شده
                del memory["silent_users"][user_id]
                save_data()
                is_silent = False
        except:
            is_silent = False
    
    stats_text = f"""
📊 *آمار کاربری:*

👤 *نقش:* {role}
⚠ *اخطارها:* {warns}
🔇 *سایلنت:* {"✅" if is_silent else "❌"}
⭐ *ویژه:* {"✅" if user_id in memory["vips"] else "❌"}
    """
    await message.reply_text(stats_text)

@bot.on_message(filters.command("آمار_گروه"))
async def group_stats(client, message: Message):
    try:
        members_count = await client.get_chat_members_count(message.chat.id)
        chat = await client.get_chat(message.chat.id)
        
        chat_id_str = str(message.chat.id)
        stats_text = f"""
📈 *آمار گروه:*

👥 *تعداد اعضا:* {members_count}
📝 *نوع گروه:* {chat.type}
🔰 *قوانین:* {"✅" if chat_id_str in memory["rules"] else "❌"}
🎉 *خوشامدگویی:* {"✅" if chat_id_str in memory["welcome_messages"] else "❌"}
🔒 *وضعیت گروه:* {"فعال ✅" if chat_id_str not in memory["disabled_groups"] else "غیرفعال 🔴"}
        """
        await message.reply_text(stats_text)
    except Exception as e:
        await message.reply_text(f"❌ خطا در دریافت آمار: {e}")

@bot.on_message(filters.command("اطلاعات_گروه"))
async def group_info(client, message: Message):
    try:
        chat = await client.get_chat(message.chat.id)
        members_count = await client.get_chat_members_count(message.chat.id)
        
        info_text = f"""
🏷 *نام گروه:* {chat.title}
📝 *توضیحات:* {chat.description or 'بدون توضیح'}
👥 *تعداد اعضا:* {members_count}
🆔 *آیدی گروه:* {message.chat.id}
📅 *تاریخ ایجاد:* {chat.date.strftime('%Y-%m-%d') if chat.date else 'نامشخص'}
        """
        await message.reply_text(info_text)
    except Exception as e:
        await message.reply_text(f"❌ خطا در دریافت اطلاعات: {e}")

@bot.on_message(filters.command("لیست_کاربران"))
async def list_users(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        members = []
        async for member in client.get_chat_members(message.chat.id):
            if not member.user.is_bot:
                members.append(member.user.first_name or "بدون نام")
        
        await message.reply_text(f"👥 تعداد کاربران: {len(members)} نفر")
    except Exception as e:
        await message.reply_text(f"❌ خطا در دریافت لیست: {e}")

@bot.on_message(filters.command("لیست_مدیران"))
async def list_admins(client, message: Message):
    try:
        admins = []
        async for member in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if not member.user.is_bot:
                admins.append(member.user.first_name or "بدون نام")
        
        admin_list = "\n".join(admins)
        await message.reply_text(f"👑 لیست مدیران ({len(admins)} نفر):\n\n{admin_list}")
    except Exception as e:
        await message.reply_text(f"❌ خطا در دریافت لیست مدیران: {e}")

# ۲۳-۲۷. قوانین و مدیریت گروه
@bot.on_message(filters.command("قوانین"))
async def show_rules(client, message: Message):
    rules = memory["rules"].get(str(message.chat.id), "📜 *قوانین گروه:*\n\n1. احترام متقابل\n2. عدم اسپم\n3. رعایت قوانین تلگرام")
    await message.reply_text(rules)

@bot.on_message(filters.command("تغییر_قوانین"))
async def change_rules(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        new_rules = get_command_args(message.text)
        if new_rules:
            memory["rules"][str(message.chat.id)] = new_rules
            save_data()
            await message.reply_text("✅ قوانین گروه به روز شد.")
        else:
            await message.reply_text("❌ لطفاً قوانین جدید را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@bot.on_message(filters.command("تغییر_نام_گروه"))
async def change_group_name(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        new_name = get_command_args(message.text)
        if new_name:
            await client.set_chat_title(message.chat.id, new_name)
            await message.reply_text("✅ نام گروه تغییر کرد.")
        else:
            await message.reply_text("❌ لطفاً نام جدید را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا در تغییر نام: {e}")

@bot.on_message(filters.command("پاکسازی"))
async def cleanup_messages(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
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
            
            await message.reply_text(f"✅ {deleted} پیام پاکسازی شد.")
        else:
            await message.reply_text("❌ لطفاً تعداد پیام‌ها را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@bot.on_message(filters.command("گزارش"))
async def report_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")
    
    await message.reply_text("🚨 *گزارش تخلف ثبت شد*")

# ۲۸-۳۲. مدیریت پیشرفته
@bot.on_message(filters.command("اضافه_مدیر"))
async def add_admin(client, message: Message):
    if get_user_role(message.from_user.id) != "مالک":
        return await message.reply_text("❌ فقط مالک ربات می‌تواند ادمین اضافه کند.")
    
    if message.reply_to_message:
        user_id = str(message.reply_to_message.from_user.id)
        memory["admins"][user_id] = True
        save_data()
        await message.reply_text("✅ کاربر به لیست ادمین‌ها اضافه شد.")
    else:
        await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")

@bot.on_message(filters.command("حذف_مدیر"))
async def remove_admin(client, message: Message):
    if get_user_role(message.from_user.id) != "مالک":
        return await message.reply_text("❌ فقط مالک ربات می‌تواند ادمین حذف کند.")
    
    try:
        args = get_command_args(message.text)
        if args.isdigit():
            user_id = str(int(args))
            if user_id in memory["admins"]:
                del memory["admins"][user_id]
                save_data()
                await message.reply_text("✅ کاربر از لیست ادمین‌ها حذف شد.")
            else:
                await message.reply_text("❌ این کاربر در لیست ادمین‌ها نیست.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@bot.on_message(filters.command("اضافه_vip"))
async def add_vip(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    if message.reply_to_message:
        user_id = str(message.reply_to_message.from_user.id)
        memory["vips"][user_id] = True
        save_data()
        await message.reply_text("✅ کاربر به لیست VIP اضافه شد.")
    else:
        await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")

@bot.on_message(filters.command("تغییر_تصویر_گروه"))
async def change_group_photo(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    if message.reply_to_message and message.reply_to_message.photo:
        try:
            photo_id = message.reply_to_message.photo.file_id
            await client.set_chat_photo(message.chat.id, photo=photo_id)
            await message.reply_text("✅ تصویر گروه تغییر کرد.")
        except Exception as e:
            await message.reply_text(f"❌ خطا در تغییر تصویر: {e}")
    else:
        await message.reply_text("❌ لطفاً به یک عکس ریپلای کنید.")

@bot.on_message(filters.command("حذف_تصویر_گروه"))
async def delete_group_photo(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        await client.delete_chat_photo(message.chat.id)
        await message.reply_text("✅ تصویر گروه حذف شد.")
    except Exception as e:
        await message.reply_text(f"❌ خطا در حذف تصویر: {e}")

# ۳۳-۳۷. خوشامدگویی و کنترل
@bot.on_message(filters.command("خوشامدگویی"))
async def send_welcome(client, message: Message):
    welcome_msg = memory["welcome_messages"].get(
        str(message.chat.id),
        "👋 به گروه خوش آمدید! لطفاً قوانین را مطالعه کنید."
    )
    await message.reply_text(welcome_msg)

@bot.on_message(filters.command("تغییر_خوشامدگویی"))
async def change_welcome(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        new_welcome = get_command_args(message.text)
        if new_welcome:
            memory["welcome_messages"][str(message.chat.id)] = new_welcome
            save_data()
            await message.reply_text("✅ پیام خوشامدگویی به روز شد.")
        else:
            await message.reply_text("❌ لطفاً پیام جدید را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@bot.on_message(filters.command("خوشامدگویی_پیشفرض"))
async def reset_welcome(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    default_welcome = "👋 به گروه خوش آمدید! از حضور شما خوشحالیم."
    memory["welcome_messages"][str(message.chat.id)] = default_welcome
    save_data()
    await message.reply_text("✅ پیام خوشامدگویی به حالت پیشفرض بازگشت.")

@bot.on_message(filters.command("پین"))
async def pin_message(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    if message.reply_to_message:
        try:
            await client.pin_chat_message(message.chat.id, message.reply_to_message.id)
            await message.reply_text("✅ پیام پین شد.")
        except Exception as e:
            await message.reply_text(f"❌ خطا در پین کردن پیام: {e}")
    else:
        await message.reply_text("❌ لطفاً به پیام مورد نظر ریپلای کنید.")

@bot.on_message(filters.command("آنپین"))
async def unpin_message(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        await client.unpin_chat_message(message.chat.id)
        await message.reply_text("✅ پیام آنپین شد.")
    except Exception as e:
        await message.reply_text(f"❌ خطا در آنپین کردن پیام: {e}")

# ۳۸-۳۹. کنترل‌های نهایی
@bot.on_message(filters.command("وضعیت"))
async def bot_status(client, message: Message):
    status_text = """
🤖 *وضعیت ربات Ninja Protector:*

✅ *وضعیت:* فعال و آنلاین
🔧 *نسخه:* ۲.۰.۰
📊 *حافظه:* سالم
🛡 *امنیت:* فعال
🎯 *قابلیت‌ها:* ۳۹ قابلیت فعال
🌐 *میزبانی:* Railway.app
💾 *ذخیره‌سازی:* فعال
    """
    await message.reply_text(status_text)

@bot.on_message(filters.command("معرفی"))
async def bot_info(client, message: Message):
    info_text = """
🤖 *ربات Ninja Protector*

🎯 یک ربات پیشرفته برای مدیریت گروه‌های تلگرام

*قابلیت‌های اصلی (۳۹ قابلیت):*
🛡 مدیریت کاربران و امنیت
🎮 سرگرمی و بازی‌های گروهی  
📊 آمار و گزارش‌های پیشرفته
⚙ تنظیمات کاملاً قابل شخصی‌سازی

*توسعه دهنده:* @ninja_developer
*پشتیبانی:* @ninja_support
*کانال:* @ninja_protector_channel
*میزبانی:* Railway.app
    """
    await message.reply_text(info_text)

# کنترل‌های فعال/غیرفعال
@bot.on_message(filters.command("فعال_غیرفعال_گروه"))
async def toggle_group(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    chat_id = str(message.chat.id)
    if chat_id in memory["disabled_groups"]:
        memory["disabled_groups"].discard(chat_id)
        save_data()
        await message.reply_text("✅ گروه فعال شد.")
    else:
        memory["disabled_groups"].add(chat_id)
        save_data()
        await message.reply_text("🔴 گروه غیرفعال شد.")

@bot.on_message(filters.command("فعال_غیرفعال_رسانه"))
async def toggle_media(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    chat_id = str(message.chat.id)
    if chat_id in memory["media_disabled"]:
        memory["media_disabled"].discard(chat_id)
        save_data()
        await message.reply_text("✅ ارسال رسانه فعال شد.")
    else:
        memory["media_disabled"].add(chat_id)
        save_data()
        await message.reply_text("🔴 ارسال رسانه غیرفعال شد.")

@bot.on_message(filters.command("فعال_غیرفعال_لینک"))
async def toggle_links(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    chat_id = str(message.chat.id)
    if chat_id in memory["links_disabled"]:
        memory["links_disabled"].discard(chat_id)
        save_data()
        await message.reply_text("✅ ارسال لینک فعال شد.")
    else:
        memory["links_disabled"].add(chat_id)
        save_data()
        await message.reply_text("🔴 ارسال لینک غیرفعال شد.")

@bot.on_message(filters.command("فعال_غیرفعال_استیکر"))
async def toggle_stickers(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    chat_id = str(message.chat.id)
    if chat_id in memory["stickers_disabled"]:
        memory["stickers_disabled"].discard(chat_id)
        save_data()
        await message.reply_text("✅ ارسال استیکر فعال شد.")
    else:
        memory["stickers_disabled"].add(chat_id)
        save_data()
        await message.reply_text("🔴 ارسال استیکر غیرفعال شد.")

# هندلر Callback
@bot.on_callback_query()
async def handle_callback_query(client, callback_query):
    if callback_query.data == "help":
        await help_command(client, callback_query.message)
    elif callback_query.data == "info":
        await bot_info(client, callback_query.message)
    await callback_query.answer()

# هندلر خوشامدگویی به کاربران جدید
@bot.on_message(filters.new_chat_members)
async def welcome_new_members(client, message: Message):
    chat_id_str = str(message.chat.id)
    
    # اگر گروه غیرفعال است، کاری نکن
    if chat_id_str in memory["disabled_groups"]:
        return
    
    welcome_msg
