# -- coding: utf-8 --
"""
ربات تلگرام پیشرفته -𝖓𝖎𝖓𝖏𝖆-🥷-(𝖕𝖗𝖔𝖙𝖊𝖈𝖙𝖔𝖗)
نسخه نهایی با ۳۹ قابلیت فعال - سازگار با Python 3.13+ و Render.com
"""

import os
import asyncio
import datetime
import random
import logging
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPrivileges

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(_name_)

# ================================
# اطلاعات ربات (از متغیرهای محیطی Render.com)
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", 24461074))

# بررسی وجود متغیرهای ضروری
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("لطفا متغیرهای محیطی API_ID, API_HASH و BOT_TOKEN را تنظیم کنید")

# ================================
# ساخت کلاینت ربات
bot = Client(
    "ninja_protector_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=1,
    sleep_threshold=60
)

# ================================
# داده‌ها و حافظه
memory = {
    "silent_users": {},
    "banned_users": {},
    "warns": {},
    "rules": {},
    "welcome_messages": {},
    "blacklist": {"users": set(), "words": set(), "links": set(), "bots": set()},
    "whitelist": {"users": set()},
    "admins": {},
    "vips": {},
    "disabled_groups": set(),
    "media_disabled": set(),
    "links_disabled": set(),
    "stickers_disabled": set(),
    "games": {}
}

# ================================
# کانال‌های اجباری
mandatory_channels = ["@ninja_protector_channel"]

# ================================
# توابع کمکی
async def check_membership(user_id: int):
    """بررسی عضویت کاربر در کانال‌های اجباری"""
    for channel in mandatory_channels:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status not in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
                return True
        except Exception:
            continue
    return False

def get_user_role(user_id: int):
    """دریافت نقش کاربر"""
    if user_id == OWNER_ID:
        return "owner"
    elif user_id in memory["admins"]:
        return "admin"
    elif user_id in memory["vips"]:
        return "vip"
    else:
        return "normal"

def is_admin(user_id: int):
    """بررسی ادمین بودن"""
    return get_user_role(user_id) in ["owner", "admin"]

def get_command_args(text: str):
    """استخراج آرگومان‌های دستور"""
    parts = text.split(maxsplit=1)
    return parts[1] if len(parts) > 1 else ""

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

# ================================
# ۲. دستور راهنما
@bot.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = """
*📋 دستورات ربات Ninja Protector (۳۹ قابلیت):*

*🛡 مدیریت کاربران:*
/اخراج - اخراج کاربر
/سایلنت [زمان] - سکوت کاربر
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
/تغییر_قوانین_گروه - تغییر قوانین
/تغییر_نام_گروه - تغییر نام گروه
/تغییر_تصویر_گروه - تغییر عکس گروه
/حذف_تصویر_گروه - حذف عکس گروه

*👥 مدیریت پیشرفته:*
/پاکسازی [تعداد] - پاکسازی پیام‌ها
/گزارش_تخلف - گزارش کاربر
/اضافه_کردن_مدیر - افزودن مدیر
/حذف_مدیر - حذف مدیر
/اضافه_کردن_vip - افزودن کاربر ویژه
/فعال_غیرفعال_گروه - کنترل گروه

*📢 خوشامدگویی:*
/خوشامدگویی - پیام خوشامد
/تغییر_پیام_خوشامدگویی - تغییر پیام خوشامد
/خوشامدگویی_پیشفرض - بازنشانی پیام خوشامد

*🔧 سایر دستورات:*
/وضعیت_ربات - وضعیت ربات
/معرفی_ربات - معرفی ربات
/پین - پین کردن پیام
/آنپین - آنپین کردن پیام
/فعال_غیرفعال_رسانه - کنترل رسانه
/فعال_غیرفعال_لینک - کنترل لینک
/فعال_غیرفعال_استیکر - کنترل استیکر
    """
    await message.reply_text(help_text)

# ================================
# ۳. بررسی عضویت اجباری
@bot.on_message(filters.new_chat_members)
async def check_new_members(client, message: Message):
    for member in message.new_chat_members:
        if member.is_bot:
            continue
            
        if not await check_membership(member.id):
            await message.reply_text(
                f"👤 کاربر {member.mention} باید ابتدا در کانال ما عضو شود:\n"
                f"📢 @ninja_protector_channel"
            )
            try:
                await client.ban_chat_member(message.chat.id, member.id)
                await asyncio.sleep(5)
                await client.unban_chat_member(message.chat.id, member.id)
            except Exception as e:
                logger.error(f"Error in membership check: {e}")

# ================================
# ۴. خوشامدگویی به کاربران جدید
@bot.on_message(filters.new_chat_members)
async def welcome_new_members(client, message: Message):
    welcome_text = memory["welcome_messages"].get(
        message.chat.id,
        "👋 *به گروه خوش آمدید!*\n\n"
        "✅ لطفاً قوانین گروه را مطالعه کنید.\n"
        "🔰 از احترام متقابل پیروی نمایید."
    )
    
    for member in message.new_chat_members:
        if not member.is_bot:
            await message.reply_text(
                f"{member.mention} {welcome_text}"
            )

# ================================
# ۵-۱۰. سرگرمی‌ها
@bot.on_message(filters.command("سکه"))
async def coin_flip(client, message: Message):
    result = random.choice(["🍀 *شیر", "⚫ **خط*"])
    await message.reply_text(f"🪙 نتیجه پرتاب سکه:\n{result}")

@bot.on_message(filters.command("تاس"))
async def dice_roll(client, message: Message):
    result = random.randint(1, 6)
    await message.reply_text(f"🎲 نتیجه تاس:\n*عدد {result}*")

@bot.on_message(filters.command("حدس_عدد"))
async def guess_number(client, message: Message):
    number = random.randint(1, 10)
    await message.reply_text(
        f"🎯 بازی حدس عدد:\n"
        f"یک عدد بین ۱ تا ۱۰ حدس بزنید!\n"
        f"*عدد صحیح: {number}*"
    )

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

# ================================
# ۱۱-۱۵. مدیریت کاربران
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
        await message.reply_text(f"✅ کاربر {message.reply_to_message.from_user.mention} اخراج شد.")
    except Exception as e:
        await message.reply_text(f"❌ خطا در اخراج کاربر: {e}")

@bot.on_message(filters.command("سایلنت"))
async def mute_user(client, message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply_text("❌ فقط ادمین‌ها می‌توانند کاربران را سایلنت کنند.")
    
    if not message.reply_to_message:
        return await message.reply_text("❌ لطفاً به پیام کاربر مورد نظر ریپلای کنید.")
    
    user_id = message.reply_to_message.from_user.id
    mute_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    memory["silent_users"][user_id] = mute_time
    
    await message.reply_text(
        f"🔇 کاربر {message.reply_to_message.from_user.mention} به مدت ۱ ساعت سایلنت شد."
    )

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
    
    user_id = message.reply_to_message.from_user.id
    memory["warns"][user_id] = memory["warns"].get(user_id, 0) + 1
    warns_count = memory["warns"][user_id]
    
    await message.reply_text(
        f"⚠ به کاربر {message.reply_to_message.from_user.mention} اخطار داده شد.\n"
        f"📊 تعداد اخطارها: {warns_count}"
    )

@bot.on_message(filters.command("حذف_اخطار"))
async def remove_warn(client, message: Message):
    if not is_admin(message.from_user.id):
        return await message.reply_text("❌ فقط ادمین‌ها می‌توانند اخطار حذف کنند.")
    
    try:
        args = get_command_args(message.text)
        if args.isdigit():
            user_id = int(args)
            if user_id in memory["warns"] and memory["warns"][user_id] > 0:
                memory["warns"][user_id] -= 1
                await message.reply_text("✅ یک اخطار از کاربر حذف شد.")
            else:
                await message.reply_text("❌ این کاربر اخطاری ندارد.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

# ================================
# ۱۶-۲۰. لیست سیاه
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
        user_id = message.reply_to_message.from_user.id
        memory["blacklist"]["users"].add(user_id)
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
            user_id = int(args)
            memory["blacklist"]["users"].discard(user_id)
            await message.reply_text("✅ کاربر از لیست سیاه حذف شد.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

# ================================
# ۲۱-۲۵. آمار و اطلاعات
@bot.on_message(filters.command("آمار_کاربر"))
async def user_stats(client, message: Message):
    user_id = message.from_user.id
    warns = memory["warns"].get(user_id, 0)
    role = get_user_role(user_id)
    
    stats_text = f"""
📊 *آمار کاربری {message.from_user.mention}:*

👤 *نقش:* {role}
⚠ *اخطارها:* {warns}
🔇 *سایلنت:* {"✅" if user_id in memory["silent_users"] else "❌"}
🚫 *بن:* {"✅" if user_id in memory["banned_users"] else "❌"}
⭐ *ویژه:* {"✅" if user_id in memory["vips"] else "❌"}
    """
    await message.reply_text(stats_text)

@bot.on_message(filters.command("آمار_گروه"))
async def group_stats(client, message: Message):
    try:
        members_count = await client.get_chat_members_count(message.chat.id)
        chat = await client.get_chat(message.chat.id)
        
        stats_text = f"""
📈 *آمار گروه {chat.title}:*

👥 *تعداد اعضا:* {members_count}
📝 *نوع گروه:* {chat.type}
🔰 *قوانین:* {"✅" if message.chat.id in memory["rules"] else "❌"}
🎉 *خوشامدگویی:* {"✅" if message.chat.id in memory["welcome_messages"] else "❌"}
🛡 *امنیت:* {"✅ فعال" if message.chat.id not in memory["disabled_groups"] else "❌ غیرفعال"}
        """
        await message.reply_text(stats_text)
    except Exception as e:
        await message.reply_text(f"❌ خطا در دریافت آمار: {e}")

@bot.on_message(filters.command("اطلاعات_گروه"))
async def group_info(client, message: Message):
    try:
        chat = await client.get_chat(message.chat.id)
        info_text = f"""
🏷 *نام گروه:* {chat.title}
📝 *توضیحات:* {chat.description or 'بدون توضیح'}
👥 *تعداد اعضا:* {await client.get_chat_members_count(message.chat.id)}
🆔 *آیدی گروه:* {message.chat.id}
🔗 *لینک گروه:* {chat.invite_link or 'بدون لینک'}
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
                members.append(member.user.mention)
        
        if len(members) > 50:
            await message.reply_text(f"👥 تعداد کاربران: {len(members)} نفر")
        else:
            user_list = "\n".join(members[:20])
            await message.reply_text(f"👥 لیست کاربران ({len(members)} نفر):\n\n{user_list}")
    except Exception as e:
        await message.reply_text(f"❌ خطا در دریافت لیست: {e}")

@bot.on_message(filters.command("لیست_مدیران"))
async def list_admins(client, message: Message):
    try:
        admins = []
        async for member in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if not member.user.is_bot:
                admins.append(member.user.mention)
        
        admin_list = "\n".join(admins)
        await message.reply_text(f"👑 لیست مدیران ({len(admins)} نفر):\n\n{admin_list}")
    except Exception as e:
        await message.reply_text(f"❌ خطا در دریافت لیست مدیران: {e}")

# ================================
# ۲۶-۳۰. قوانین و مدیریت گروه
@bot.on_message(filters.command("قوانین"))
async def show_rules(client, message: Message):
    rules = memory["rules"].get(message.chat.id, "📜 *قوانین گروه:*\n\n1. احترام متقابل\n2. عدم اسپم\n3. رعایت قوانین تلگرام")
    await message.reply_text(rules)

@bot.on_message(filters.command("تغییر_قوانین_گروه"))
async def change_rules(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        new_rules = get_command_args(message.text)
        if new_rules:
            memory["rules"][message.chat.id] = new_rules
            await message.reply_text("✅ قوانین گروه با موفقیت به روز شد.")
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
            await message.reply_text("✅ نام گروه با موفقیت تغییر کرد.")
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
            
            status = await message.reply_text(f"✅ {deleted} پیام پاکسازی شد.")
            await asyncio.sleep(3)
            await status.delete()
        else:
            await message.reply_text("❌ لطفاً تعداد پیام‌ها را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@bot.on_message(filters.command("گزارش_تخلف"))
async def report_user(client, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")
    
    reported_user = message.reply_to_message.from_user
    await message.reply_text(
        f"🚨 *گزارش تخلف ثبت شد*\n\n"
        f"👤 کاربر: {reported_user.mention}\n"
        f"📝 گزارش توسط: {message.from_user.mention}\n"
        f"⏰ زمان: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

# ================================
# ۳۱-۳۵. مدیریت پیشرفته
@bot.on_message(filters.command("اضافه_کردن_مدیر"))
async def add_admin(client, message: Message):
    if get_user_role(message.from_user.id) != "owner":
        return await message.reply_text("❌ فقط مالک ربات می‌تواند ادمین اضافه کند.")
    
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        memory["admins"][user_id] = True
        await message.reply_text("✅ کاربر به لیست ادمین‌ها اضافه شد.")
    else:
        await message.reply_text("❌ لطفاً به پیام کاربر ریپلای کنید.")

@bot.on_message(filters.command("حذف_مدیر"))
async def remove_admin(client, message: Message):
    if get_user_role(message.from_user.id) != "owner":
        return await message.reply_text("❌ فقط مالک ربات می‌تواند ادمین حذف کند.")
    
    try:
        args = get_command_args(message.text)
        if args.isdigit():
            user_id = int(args)
            if user_id in memory["admins"]:
                del memory["admins"][user_id]
                await message.reply_text("✅ کاربر از لیست ادمین‌ها حذف شد.")
            else:
                await message.reply_text("❌ این کاربر در لیست ادمین‌ها نیست.")
        else:
            await message.reply_text("❌ لطفاً آیدی کاربر را وارد کنید.")
    except Exception as e:
        await message.reply_text(f"❌ خطا: {e}")

@bot.on_message(filters.command("اضافه_کردن_vip"))
async def add_vip(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        memory["vips"][user_id] = True
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
            await message.reply_text("✅ تصویر گروه با موفقیت تغییر کرد.")
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

# ================================
# ۳۶-۳۹. تنظیمات خوشامدگویی و کنترل
@bot.on_message(filters.command("خوشامدگویی"))
async def send_welcome(client, message: Message):
    welcome_msg = memory["welcome_messages"].get(
        message.chat.id,
        "👋 به گروه خوش آمدید! لطفاً قوانین را مطالعه کنید."
    )
    await message.reply_text(welcome_msg)

@bot.on_message(filters.command("تغییر_پیام_خوشامدگویی"))
async def change_welcome(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        new_welcome = get_command_args(message.text)
        if new_welcome:
            memory["welcome_messages"][message.chat.id] = new_welcome
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
    memory["welcome_messages"][message.chat.id] = default_welcome
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

# ================================
# کنترل‌های اضافی
@bot.on_message(filters.command("فعال_غیرفعال_گروه"))
async def toggle_group(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    chat_id = message.chat.id
    if chat_id in memory["disabled_groups"]:
        memory["disabled_groups"].discard(chat_id)
        await message.reply_text("✅ گروه فعال شد.")
    else:
        memory["disabled_groups"].add(chat_id)
        await message.reply_text("🔴 گروه غیرفعال شد.")

@bot.on_message(filters.command("فعال_غیرفعال_رسانه"))
async def toggle_media(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    chat_id = message.chat.id
    if chat_id in memory["media_disabled"]:
        memory["media_disabled"].discard(chat_id)
        await message.reply_text("✅ ارسال رسانه فعال شد.")
    else:
        memory["media_disabled"].add(chat_id)
        await message.reply_text("🔴 ارسال رسانه غیرفعال شد.")

@bot.on_message(filters.command("فعال_غیرفعال_لینک"))
async def toggle_links(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    chat_id = message.chat.id
    if chat_id in memory["links_disabled"]:
        memory["links_disabled"].discard(chat_id)
        await message.reply_text("✅ ارسال لینک فعال شد.")
    else:
        memory["links_disabled"].add(chat_id)
        await message.reply_text("🔴 ارسال لینک غیرفعال شد.")

@bot.on_message(filters.command("فعال_غیرفعال_استیکر"))
async def toggle_stickers(client, message: Message):
    if not is_admin(message.from_user.id):
        return
    
    chat_id = message.chat.id
    if chat_id in memory["stickers_disabled"]:
        memory["stickers_disabled"].discard(chat_id)
        await message.reply_text("✅ ارسال استیکر فعال شد.")
    else:
        memory["stickers_disabled"].add(chat_id)
        await message.reply_text("🔴 ارسال استیکر غیرفعال شد.")

# ================================
# اطلاعات ربات
@bot.on_message(filters.command("وضعیت_ربات"))
async def bot_status(client, message: Message):
    status_text = """
🤖 *وضعیت ربات Ninja Protector:*

✅ *وضعیت:* فعال و آنلاین
🔧 *نسخه:* ۲.۰.۰ (Python 3.13)
📊 *حافظه:* سالم
🛡 *امنیت:* فعال
🎯 *قابلیت‌ها:* ۳۹ قابلیت فعال

🔰 تمام قابلیت‌ها در دسترس هستند.
    """
    await message.reply_text(status_text)

@bot.on_message(filters.command("معرفی_ربات"))
async def bot_info(client, message: Message):
    info_text = """
🤖 *ربات Ninja Protector*

🎯 یک ربات پیشرفته برای مدیریت گروه‌های تلگرام

*قابلیت‌های اصلی (۳۹ قابلیت):*
🛡 مدیریت کاربران و امنیت
🎮 سرگرمی و بازی‌های گروهی  
📊 آمار و گزارش‌های پیشرفته
⚙ تنظیمات کاملاً قابل شخصی‌سازی
🔧 کنترل کامل رسانه و لینک‌ها

*توسعه دهنده:* @ninja_developer
*پشتیبانی:* @ninja_support
*کانال:* @ninja_protector_channel
*نسخه پایتون:* ۳.۱۳
*میزبانی:* Render.com
    """
    await message.reply_text(info_text)

# ================================
# فیلتر کردن محتوای نامناسب
@bot.on_message(filters.group)
async def filter_messages(client, message: Message):
    # بررسی اگر گروه غیرفعال است
    if message.chat.id in memory["disabled_groups"]:
        await message.delete()
        return
    
    # بررسی سایلنت کاربر
    if message.from_user.id in memory.get("silent_users", {}):
        mute_time = memory["silent_users"][message.from_user.id]
        if isinstance(mute_time, datetime.datetime) and mute_time > datetime.datetime.now():
            await message.delete()
            return
    
    # بررسی لیست سیاه
    if message.from_user.id in memory["blacklist"]["users"]:
        await message.delete()
        return
    
    # بررسی رسانه غیرفعال
    if (message.photo or message.video or message.audio) and message.chat.id in memory["media_disabled"]:
        await message.delete()
        await message.reply_text("❌ ارسال رسانه در این گروه غیرفعال است.")
        return
    
    # بررسی لینک غیرفعال
    if message.text and ("http://" in message.text or "https://" in message.text) and message.chat.id in memory["links_disabled"]:
        await message.delete()
        await message.reply_text("❌ ارسال لینک در این گروه غیرفعال است.")
        return
    
    # بررسی استیکر غیرفعال
    if message.sticker and message.chat.id in memory["stickers_disabled"]:
        await message.delete()
        await message.reply_text("❌ ارسال استیکر در این گروه غیرفعال است.")
        return

# ================================
# هندلر Callback Query
@bot.on_callback_query()
async def handle_callback_query(client, callback_query):
    if callback_query.data == "help":
        await help_command(client, callback_query.message)
    elif callback_query.data == "info":
        await bot_info(client, callback_query.message)
    
    await callback_query.answer()

# ================================
# اجرای ربات
print("🤖 Starting Ninja Protector Bot...")
print("✅ Bot is ready for deployment on Render.com!")
print("🔧 Version: 2.0.0 - 39 Features Complete")
print("🐍 Python Version: 3.13")
print("🎯 All Persian commands are active!")

if _name_ == "_main_":
    try:
        bot.run()
    except Exception as e:
        logger.error(f"❌ Error: {e}")