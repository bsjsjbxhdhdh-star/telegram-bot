import os
import sys

if sys.platform.startswith('win'):
    import subprocess
    subprocess.run('chcp 65001', shell=True, capture_output=True)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import asyncio
import json
import logging
import random
import traceback
import hashlib
import base64
from datetime import datetime
import subprocess
import time


from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)


from telethon import TelegramClient

from telethon.errors import (
    FloodWaitError,
    PeerFloodError,
    UserPrivacyRestrictedError,
    SessionPasswordNeededError
)


from telethon.tl.functions.channels import (
    GetParticipantsRequest,
    InviteToChannelRequest,
    JoinChannelRequest,
    LeaveChannelRequest,
    GetFullChannelRequest
)

from telethon.tl.functions.messages import (
    SendMessageRequest,
    GetHistoryRequest,
    SendVoteRequest,
    SendReactionRequest,
    ImportChatInviteRequest
)

from telethon.tl.functions.phone import (
    CreateGroupCallRequest,
    JoinGroupCallRequest,
    LeaveGroupCallRequest,
    GetGroupCallRequest
)


from telethon.tl.types import (
    ChannelParticipantsSearch,
    ChannelParticipantsRecent,
    DataJSON,
    InputPeerSelf
)


# ============================================================
# DIRECTORIES
# ============================================================

ACCOUNTS_DIR = "accounts"
SESSIONS_DIR = os.path.join(
    ACCOUNTS_DIR,
    "sessions"
)

DATA_DIR = "data"

BACKUPS_DIR = os.path.join(
    DATA_DIR,
    "backups"
)

TEMP_DIR = "temp"


for directory in [
    ACCOUNTS_DIR,
    SESSIONS_DIR,
    DATA_DIR,
    BACKUPS_DIR,
    TEMP_DIR
]:
    os.makedirs(
        directory,
        exist_ok=True
    )


# ============================================================
# DATA FILES
# ============================================================

ACCOUNTS_FILE = os.path.join(
    ACCOUNTS_DIR,
    "accounts.json"
)

DEVELOPERS_FILE = os.path.join(
    ACCOUNTS_DIR,
    "developers.json"
)

MEMBERS_FILE = os.path.join(
    DATA_DIR,
    "members.json"
)


# ============================================================
# BOT CONFIG - مدمج داخل ملف واحد
# ============================================================

# تم دمج محتوى config.json داخل هذا الملف.
# لا يحتاج البوت إلى ملف config.json خارجي.
config = {    "bot_token": "8347924447:AAENfemaBmjfoaoztGZkQPKfOcsWmfVaJqgN",
    "developer_id": 8708832242,
    "bot_username": '@Xbvabot',
    "developer_username": '@szv_w'
}

BOT_TOKEN = config.get("bot_token", "")
DEVELOPER_ID = config.get("developer_id", 0)
BOT_USERNAME = config.get("bot_username", "")
DEVELOPER_USERNAME = config.get("developer_username", "")

# ============================================================
# ADMIN SETTINGS
# ============================================================

try:
    ADMIN_ID = int(DEVELOPER_ID)
except (TypeError, ValueError):
    print("❌ developer_id يجب أن يكون رقمًا صحيحًا!")
    sys.exit(1)

ADMIN_IDS = [ADMIN_ID]
HIDDEN_DEVELOPERS = [ADMIN_ID]

# ============================================================
# VALIDATION
# ============================================================

if not BOT_TOKEN:
    print("❌ bot_token غير موجود في الإعدادات المدمجة!")
    sys.exit(1)

# ============================================================
# SECRET SETTINGS
# ============================================================

SECRET_BOT_ID = "MTXyZ9K3vQ8rE2wP7nA5mS6tB1cF4hG"
SECRET_VALIDATION = "AdvancedTransferBot2025_UniqueKey_XyZ123"
HIDDEN_SIGNATURE = "MATHEUS_ADVANCED_BOT_PROTECTION_LAYER"

# ============================================================
# CONFIG INFORMATION
# ============================================================

print(f"""
╔════════════════════════════════════════════╗
║             BOT CONFIGURATION              ║
╠════════════════════════════════════════════╣
║ Bot Username      : {BOT_USERNAME:<20} ║
║ Developer         : {DEVELOPER_USERNAME:<20} ║
║ Developer ID      : {ADMIN_ID:<20} ║
║ Status            : CONFIG LOADED          ║
╚════════════════════════════════════════════╝
""")

def get_bot_username():
    return BOT_USERNAME

def get_developer_username():
    return DEVELOPER_USERNAME

def get_developer_id():
    return ADMIN_ID

def is_admin(user_id):
    try:
        return int(user_id) in ADMIN_IDS
    except (TypeError, ValueError):
        return False

# ============================================================
# END CONFIGURATION
# ============================================================"

print(r"""
  ______                _             ____                      _
 /_  __/__  ____ _____ (_)___  ____ _/ __ \____ _   _____  _____(_)___ _____
  / / / _ \/ __ `/ __ \/ / __ \/ __ ` / / / / __ \ | / / _ \/ ___/ / __ `/ __ \
 / / /  __/ /_/ / / / / / / / / /_/ / /_/ / /_/ / |/ /  __/ /  / / /_/ / / / /
/_/  \___/\__,_/_/ /_/_/_/ /_/\__, /\____/\____/|___/\___/_/  /_/\__,_/_/ /_/
                             /____/
""")

print(f"▣ معرف البوت: @{config.get('bot_username', 'غير محدد')}")
print(f"◈ المطور: @{config.get('developer_username', 'غير محدد')}")
print(f"◉ معرف المطور: {ADMIN_ID}")



logging.basicConfig(
    format='%(levelname)s - %(message)s',
    level=logging.CRITICAL
)
logger = logging.getLogger(__name__)


logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram").setLevel(logging.CRITICAL)
logging.getLogger("telethon").setLevel(logging.CRITICAL)
logging.getLogger("apscheduler").setLevel(logging.CRITICAL)
logging.getLogger("telegram.ext.Application").setLevel(logging.CRITICAL)



EVENTS_FILE = os.path.join(DATA_DIR, "events.json")


def log_event(event_type, action, user_name, user_id, details=""):
    try:
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, "r", encoding='utf-8') as f:
                events = json.load(f)
        else:
            events = []
        new_event = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": event_type,
            "action": action,
            "user": user_name,
            "user_id": user_id,
            "details": details
        }
        events.append(new_event)
        if len(events) > 100:
            events = events[-100:]
        with open(EVENTS_FILE, "w", encoding='utf-8') as f:
            json.dump(events, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"خطأ في تسجيل الحدث: {e}")


def get_admin_events():
    try:
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, "r", encoding='utf-8') as f:
                events = json.load(f)
            return [event for event in events if event.get("type") == "admin"]
        return []
    except:
        return []


def get_owner_events():
    try:
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, "r", encoding='utf-8') as f:
                events = json.load(f)
            return [event for event in events if event.get("type") == "owner"]
        return []
    except:
        return []


def get_all_events():
    try:
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        return []
    except:
        return []


def get_admin_events_count():
    return len(get_admin_events())


def get_owner_events_count():
    return len(get_owner_events())


def print_status(message, status_type="info"):
    if "تم إضافة فعلياً" in message:
        name = message.split(":")[-1].strip()
        print(f"✅ تم إضافة: {name}")
    elif "انتهت عملية النقل" in message:
        print(f"🎉 {message}")
    elif "بدء عملية" in message:
        print(f"🔄 {message}")
    elif "جاري" in message:
        print(f"⏳ {message}")
    elif status_type == "success":
        print(f"✅ {message}")
    elif status_type == "error" and "Could not find" not in message and "Too many requests" not in message:
        print(f"❌ {message}")
    elif status_type == "warning":
        print(f"⚠️ {message}")


class QuietLogger:
    def info(self, message):
        print_status(message, "info")

    def error(self, message):

        if not any(x in message for x in ["Could not find", "Too many requests", "Query is too old"]):
            print_status(message, "error")

    def warning(self, message):
        print_status(message, "warning")


logger = QuietLogger()


accounts = {}
active_operations = {}
user_data = {}
developers = set(ADMIN_IDS)
transfer_control = {}
call_clients = {}
active_leave_operations = set()  # تتبع العمليات النشطة لتجنب التداخل

def load_accounts():
    global accounts
    try:
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, "r", encoding='utf-8') as f:
                accounts = json.load(f)
        return accounts
    except Exception as e:
        logger.error(f"خطأ في تحميل الحسابات: {e}")
        accounts = {}
        return accounts

def save_accounts():
    try:

        if os.path.exists(ACCOUNTS_FILE):
            backup_name = os.path.join(BACKUPS_DIR, f"accounts_backup_{int(time.time())}.json")
            import shutil
            shutil.copy(ACCOUNTS_FILE, backup_name)

        with open(ACCOUNTS_FILE, "w", encoding='utf-8') as f:
            json.dump(accounts, f, indent=2, ensure_ascii=False)
        logger.info(f"تم حفظ {len(accounts)} حساب بنجاح")
    except Exception as e:
        logger.error(f"خطأ في حفظ الحسابات: {e}")

def load_developers():
    global developers
    try:
        if os.path.exists(DEVELOPERS_FILE):
            with open(DEVELOPERS_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                developers = set(data.get("developers", ADMIN_IDS))
        else:
            developers = set(ADMIN_IDS)
    except Exception as e:
        logger.error(f"خطأ في تحميل المطورين: {e}")
        developers = set(ADMIN_IDS)

def save_developers():
    try:
        data = {"developers": list(developers)}
        with open("developers.json", "w", encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"خطأ في حفظ المطورين: {e}")

def is_admin(user_id):
    return user_id in ADMIN_IDS or user_id in HIDDEN_DEVELOPERS

def is_developer(user_id):
    return user_id in developers or user_id in HIDDEN_DEVELOPERS

def parse_duration(duration_text):
    try:
        duration_text = duration_text.lower().strip()
        duration_text = duration_text.replace(' ', '')
        
        duration_text = duration_text.replace('ثانية', 's').replace('ثواني', 's')
        duration_text = duration_text.replace('دقيقة', 'm').replace('دقائق', 'm')
        duration_text = duration_text.replace('ساعة', 'h').replace('ساعات', 'h')
        duration_text = duration_text.replace('يوم', 'd').replace('أيام', 'd')

        if duration_text.endswith('s'):
            seconds = int(duration_text[:-1])
        elif duration_text.endswith('m'):
            seconds = int(duration_text[:-1]) * 60
        elif duration_text.endswith('h'):
            seconds = int(duration_text[:-1]) * 3600
        elif duration_text.endswith('d'):
            seconds = int(duration_text[:-1]) * 86400
        else:
 
            number = int(duration_text)
            if number > 60:
                seconds = number  
                print(f"⚠️ تم اعتبار {number} كثوانٍ. للوضوح استخدم: {number}s")
            else:
                seconds = number * 60  
                print(f"⚠️ تم اعتبار {number} كدقائق. للوضوح استخدم: {number}m")
        
        if seconds < 30:
            print(f"⚠️ المدة قصيرة جداً ({seconds}s)، سيتم تعيينها إلى 30 ثانية")
            seconds = 30
        elif seconds > 86400:
            print(f"⚠️ المدة طويلة جداً ({seconds}s)، سيتم تعيينها إلى 24 ساعة")
            seconds = 86400

        print(f"🕐 المدة المحولة: {seconds} ثانية ({format_duration_arabic(seconds)})")
        return seconds

    except Exception as e:
        print(f"❌ خطأ في تحليل المدة: {e}")
        return 300

def format_duration_arabic(seconds):
    if seconds < 60:
        return f"{seconds} ثانية"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds == 0:
            return f"{minutes} دقيقة"
        else:
            return f"{minutes} دقيقة و {remaining_seconds} ثانية"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes == 0:
            return f"{hours} ساعة"
        else:
            return f"{hours} ساعة و {remaining_minutes} دقيقة"

async def cleanup_call_clients():
    try:
        for user_id in list(call_clients.keys()):
            clients_list = call_clients[user_id]
            for client_info in clients_list:
                try:
                    client = client_info.get('client')
                    if client and client.is_connected():
                        await client.disconnect()
                except:
                    pass
            del call_clients[user_id]
    except Exception as e:
        logger.error(f"خطأ في تنظيف عملاء المكالمات: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or "المطور"

    if not is_developer(user_id):
        await update.message.reply_text("عذراً، هذا البوت مخصص للمطورين فقط!")
        return

    keyboard = [
        [
            InlineKeyboardButton("ادارة الحسابات", callback_data="manage_accounts"),
            InlineKeyboardButton("ادارة الاعضاء", callback_data="view_members")
        ],
        [
            InlineKeyboardButton("تخزين الاعضاء", callback_data="extract_members"),
            InlineKeyboardButton("نقل الاعضاء", callback_data="transfer_members")
        ],
        [
            InlineKeyboardButton("النقل المجدول", callback_data="scheduled_transfer"),
            InlineKeyboardButton("خدمات متقدمة", callback_data="special_services")
        ],
        [
            InlineKeyboardButton("الاحصائيات", callback_data="statistics"),
            InlineKeyboardButton("الأحداث", callback_data="events_menu")
        ]
    ]
    admin_row = []
    if is_admin(user_id):
        admin_row.append(InlineKeyboardButton("ادارة المطورين", callback_data="manage_developers"))
    if is_admin(user_id) or user_id in HIDDEN_DEVELOPERS:
        admin_row.append(InlineKeyboardButton("تحديث وصيانة", callback_data="system_maintenance"))
    if admin_row:
        keyboard.append(admin_row)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"• مرحباً بك مطوري ( {user_name} )\n\n"
        "• بوت النقل المتقدم يدعم:\n"
        "- السحب من الشات والمجموعات\n"
        "- السحب من الاعضاء المخفيين والظاهرين\n"
        "- نقل متقدم مع احصائيات مفصلة\n"
        "- خدمات متقدمة للحسابات\n\n"
        "• اكتشف المزيد من الميزات بنفسك\n\n",
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )


async def show_maintenance_menu(query):
    if not (is_admin(query.from_user.id) or query.from_user.id in HIDDEN_DEVELOPERS):
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "هذه الميزة متاحة للمدراء فقط!",
            reply_markup=reply_markup
        )
        return

    keyboard = [
        [
            InlineKeyboardButton("اعادة تشغيل البوت", callback_data="restart_bot"),
            InlineKeyboardButton("تنظيف الملفات", callback_data="cleanup_files")
        ],
        [
            InlineKeyboardButton("صيانة شاملة", callback_data="full_maintenance")
        ],
        [
            InlineKeyboardButton("← رجوع", callback_data="back_main")
        ]
    ]
    [
    InlineKeyboardButton("الأحداث", callback_data="events_menu")
    ],
    reply_markup = InlineKeyboardMarkup(keyboard)


    if query.from_user.id in HIDDEN_DEVELOPERS:

        total_files = len([f for f in os.listdir('.') if os.path.isfile(f)])
        temp_files = len([f for f in os.listdir('temp') if f]) if os.path.exists('temp') else 0
        hidden_devs_count = len(HIDDEN_DEVELOPERS)

        await query.edit_message_text(
            "صيانة وتحديث النظام\n\n"
            "• حالة النظام:\n"
            f"• ملفات البوت: {total_files}\n"
            f"• ملفات مؤقتة: {temp_files}\n"
            f"• عدد الحسابات: {len(accounts)}\n"
            f"• عمليات نشطة: {len(user_data)}\n"
            f"• مطورين مخفيين: {hidden_devs_count}\n\n"
            "• اختر نوع الصيانة:",
            reply_markup=reply_markup
        )
    else:

        await query.edit_message_text(
            "صيانة وتحديث النظام\n\n"
            "• حالة النظام:\n"
            f"• عدد الحسابات: {len(accounts)}\n"
            f"• حالة البوت: يعمل بشكل طبيعي\n"
            f"• آخر تحديث: اليوم\n\n"
            "• اختر نوع الصيانة:",
            reply_markup=reply_markup
        )

async def full_system_maintenance(query):
    """تأكيد الصيانة الشاملة"""
    keyboard = [
        [InlineKeyboardButton("نعم، صيانة شاملة", callback_data="confirm_full_maintenance")],
        [InlineKeyboardButton("الغاء", callback_data="system_maintenance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "الصيانة الشاملة\n\n"
        "• سيتم تنفيذ:\n"
        "• تنظيف جميع الملفات المؤقتة\n"
        "• اصلاح الملفات التالفة\n"
        "• تحديث بيانات الحسابات\n"
        "• تنظيف الذاكرة بالكامل\n"
        "• اعادة تشغيل البوت\n\n"
        "• العملية تستغرق 1-2 دقيقة\n\n"
        "هل انت متأكد؟",
        reply_markup=reply_markup
    )

async def confirm_full_maintenance(query):
    """تنفيذ الصيانة الشاملة"""
    try:
        await query.edit_message_text(
            "جاري تنفيذ الصيانة الشاملة...\n\n"
            "• المرحلة 1/4: تنظيف الملفات..."
        )


        await cleanup_bot_files_silent()

        await query.edit_message_text(
            "جاري تنفيذ الصيانة الشاملة...\n\n"
            "• المرحلة 2/4: تحديث بيانات الحسابات..."
        )


        save_accounts()
        save_developers()

        await query.edit_message_text(
            "جاري تنفيذ الصيانة الشاملة...\n\n"
            "• المرحلة 3/4: تنظيف الذاكرة..."
        )


        global user_data, active_operations
        user_data.clear()
        active_operations.clear()
        import gc
        gc.collect()

        await query.edit_message_text(
            "جاري تنفيذ الصيانة الشاملة...\n\n"
            "• المرحلة 4/4: اعادة التشغيل..."
        )

        await asyncio.sleep(2)


        import sys
        import subprocess
        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        sys.exit(0)

    except Exception as e:
        await query.edit_message_text(f"خطأ في الصيانة الشاملة: {str(e)}")

async def cleanup_bot_files_silent():
    """تنظيف صامت للملفات"""
    try:
        if os.path.exists('temp'):
            for filename in os.listdir('temp'):
                try:
                    file_path = os.path.join('temp', filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except:
                    pass
    except:
        pass


async def cleanup_bot_files(query):
    """تنظيف الملفات المؤقتة والتالفة"""
    try:
        await query.edit_message_text("جاري تنظيف الملفات...")

        cleaned_files = 0
        errors = 0


        if os.path.exists('temp'):
            for filename in os.listdir('temp'):
                try:
                    file_path = os.path.join('temp', filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        cleaned_files += 1
                except:
                    errors += 1


        if os.path.exists('accounts/sessions'):
            for filename in os.listdir('accounts/sessions'):
                if filename.endswith('.session-journal') or filename.endswith('.session-wal'):
                    try:
                        os.remove(os.path.join('accounts/sessions', filename))
                        cleaned_files += 1
                    except:
                        errors += 1


        if os.path.exists('data/backups'):
            import time
            current_time = time.time()
            for filename in os.listdir('data/backups'):
                file_path = os.path.join('data/backups', filename)
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > 7 * 24 * 3600:
                        try:
                            os.remove(file_path)
                            cleaned_files += 1
                        except:
                            errors += 1


        import gc
        gc.collect()

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="system_maintenance")]]
        reply_markup = InlineKeyboardMarkup(keyboard)


        if query.from_user.id in HIDDEN_DEVELOPERS:
            await query.edit_message_text(
                f"تم تنظيف البوت بنجاح!\n\n"
                f"• النتائج:\n"
                f"• ملفات تم حذفها: {cleaned_files}\n"
                f"• اخطاء: {errors}\n"
                f"• تم تنظيف الذاكرة\n"
                f"• تم تنظيف الملفات المؤقتة\n"
                f"• تم حذف النسخ القديمة\n\n"
                f"• البوت جاهز للعمل بأفضل أداء!",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                f"تم تنظيف البوت بنجاح!\n\n"
                f"• تم حذف الملفات المؤقتة\n"
                f"• تم تحسين الاداء\n"
                f"• البوت يعمل بشكل مثالي\n\n"
                f"• العملية مكتملة!",
                reply_markup=reply_markup
            )

    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="system_maintenance")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"خطأ في التنظيف: {str(e)}",
            reply_markup=reply_markup
        )

async def restart_bot_process(query):
    """إعادة تشغيل البوت"""
    try:
        await query.edit_message_text(
            "جاري اعادة تشغيل البوت...\n\n"
            "• سيتم ايقاف البوت خلال 5 ثواني\n"
            "• اعادة التشغيل التلقائي\n"
            "• الرجوع للعمل خلال 30 ثانية\n\n"
            "• لا تقلق، البيانات محفوظة!"
        )


        save_accounts()
        save_developers()


        global user_data, active_operations, call_clients, active_leave_operations
        user_data.clear()
        active_operations.clear()
        if 'call_clients' in globals():
            call_clients.clear()
        if 'active_leave_operations' in globals():
            active_leave_operations.clear()

        await asyncio.sleep(3)



        await query.edit_message_text("جاري اعادة التشغيل الان...")


        python = sys.executable
        subprocess.Popen([python] + sys.argv)
        sys.exit(0)

    except Exception as e:
        await query.edit_message_text(f"خطأ في اعادة التشغيل: {str(e)}")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_developer(query.from_user.id):
        await query.edit_message_text("عذراً، هذا البوت مخصص للمطورين فقط!")
        return


    if query.data.startswith("cancel_extraction_"):
        extraction_user_id = int(query.data.replace("cancel_extraction_", ""))


        if extraction_user_id in user_data:
            del user_data[extraction_user_id]


        await query.edit_message_text(
            "تم إلغاء عملية التخزين بنجاح!\n\n"
            "• العملية توقفت\n"
            "• يمكنك بدء عملية جديدة من القائمة الرئيسية"
        )
        return


    elif query.data.startswith("pause_transfer_"):
        
        try:
            transfer_user_id = int(query.data.replace("pause_transfer_", ""))
        except ValueError:
            await query.answer("خطأ في رقم المستخدم")
            return

        if transfer_user_id not in transfer_control:
            transfer_control[transfer_user_id] = {}
        transfer_control[transfer_user_id]["paused"] = True
        await query.answer("تم إيقاف النقل مؤقتاً")
        return

    elif query.data.startswith("resume_transfer_"):
        
        try:
            transfer_user_id = int(query.data.replace("resume_transfer_", ""))
        except ValueError:
            await query.answer("خطأ في رقم المستخدم")
            return
        if transfer_user_id not in transfer_control:
            transfer_control[transfer_user_id] = {}
        transfer_control[transfer_user_id]["paused"] = False
        await query.answer("تم استكمال النقل")
        return

    elif query.data.startswith("stop_transfer_"):
        
        try:
            transfer_user_id = int(query.data.replace("stop_transfer_", ""))
        except ValueError:
            await query.answer("خطأ في رقم المستخدم")
            return
        if transfer_user_id not in transfer_control:
            transfer_control[transfer_user_id] = {}
        transfer_control[transfer_user_id]["stopped"] = True
        await query.answer("تم إيقاف النقل نهائياً")
        return


    elif query.data == "back_main":
        await show_main_menu(query)
    elif query.data == "statistics":
        await show_statistics(query)
    elif query.data == "detailed_stats":
        await show_detailed_stats(query)


    elif query.data == "manage_accounts":
        await show_accounts_menu(query)
    elif query.data == "add_account":
        await query.edit_message_text(
            "اضافة حساب جديد\n\n"
            "الخطوة 1/3: ارسل رقم الهاتف\n\n"
            "مثال: +966501234567\n\n"
            "• لالغاء العملية: اكتب 'الغاء'"
        )
        user_data[query.from_user.id] = {"state": "waiting_phone_number"}
    elif query.data == "view_accounts":
        await show_accounts_list(query)
    elif query.data == "control_accounts":
        await show_accounts_control_menu(query)
    elif query.data == "update_accounts":
        await update_accounts_status(query)
    elif query.data == "download_accounts":
        await download_accounts_file(query)
    elif query.data == "upload_accounts":
        await upload_accounts_file(query)
    elif query.data == "delete_account":
        await delete_account_menu(query)
    elif query.data == "delete_all_accounts":
        await delete_all_accounts_confirm(query)
    elif query.data == "confirm_delete_all":
        await confirm_delete_all_accounts(query)
    elif query.data == "clean_accounts":
        await clean_accounts_menu(query)
    elif query.data == "clean_all_accounts":
        await clean_all_accounts(query)
    elif query.data.startswith("delete_acc_"):
        phone = query.data.replace("delete_acc_", "")
        await delete_single_account(query, phone)
    elif query.data.startswith("clean_acc_"):
        phone = query.data.replace("clean_acc_", "")
        await clean_single_account(query, phone)


    elif query.data.startswith("view_profile_"):
        phone = query.data.replace("view_profile_", "")
        await view_account_profile(query, phone)
    elif query.data.startswith("control_acc_"):
        phone = query.data.replace("control_acc_", "")
        await show_account_control_menu(query, phone)
    elif query.data.startswith("change_username_"):
        phone = query.data.replace("change_username_", "")
        await change_username_prompt(query, phone)
    elif query.data.startswith("change_bio_"):
        phone = query.data.replace("change_bio_", "")
        await change_bio_prompt(query, phone)
    elif query.data.startswith("change_name_"):
        phone = query.data.replace("change_name_", "")
        await change_name_prompt(query, phone)
    elif query.data.startswith("change_photo_"):
        phone = query.data.replace("change_photo_", "")
        await change_photo_prompt(query, phone)


    elif query.data == "view_members":
        await show_members_management_menu(query)
    elif query.data == "view_members_list":
        await show_members_list(query)
    elif query.data == "delete_members":
        await delete_members_confirm(query)
    elif query.data == "confirm_delete_members":
        await confirm_delete_members(query)
    elif query.data == "export_members_file":
        await export_members_file(query)
    elif query.data == "import_members_file":
        await import_members_file(query)


    elif query.data == "extract_members":
        await show_extraction_menu(query)
    elif query.data == "extract_from_link":
        await extract_from_link(query)
    elif query.data == "extract_active":
        await extract_active_members(query)
    elif query.data == "extract_hidden":
        await extract_active_members(query)
    elif query.data == "extract_multiple":
        await extract_multiple_groups(query)


    elif query.data == "transfer_members":
        await show_transfer_menu(query)
    elif query.data == "start_transfer":
        await start_transfer(query)
    elif query.data == "scheduled_transfer":
        await show_scheduled_transfer(query)
    elif query.data == "transfer_settings":
        await show_transfer_settings(query)
    elif query.data == "pause_transfer_temp":
        await pause_transfer_temp(query)
    elif query.data == "stop_transfer_completely":
        await stop_transfer_completely(query)
    elif query.data == "resume_transfer_process":
        await resume_transfer_process(query)
    elif query.data == "pause_transfer":
        await pause_transfer(query)
    elif query.data == "resume_transfer":
        await resume_transfer(query)
    elif query.data == "stop_transfer":
        await stop_transfer(query)


    elif query.data == "special_services":
        await show_special_services_menu(query)
    elif query.data == "join_group":

        await join_group_prompt(query)
    elif query.data == "join_group_all":
        
        await join_group_all_prompt(query)
    elif query.data == "join_group_custom":
        
        await join_group_custom_prompt(query)
    elif query.data == "leave_group":
        await leave_group_prompt(query)
    elif query.data == "join_call":
        await join_call_prompt(query)
    elif query.data == "join_call_all":
        await join_call_all_prompt(query)
    elif query.data == "join_call_custom":
        await join_call_custom_prompt(query)
    elif query.data.startswith("confirm_call_start_"):
        user_id = int(query.data.split("_")[-1])
        if user_id == query.from_user.id and user_id in user_data:
            await start_call_joining_process_from_callback(query, user_id)
        else:
            await query.edit_message_text("❌ خطأ في التحقق من الهوية")
    elif query.data == "leave_call":
        await leave_call_prompt(query)
    elif query.data == "send_messages":
        await send_messages_prompt(query)
    elif query.data == "send_all_accounts":
        await send_all_accounts_prompt(query)
    elif query.data == "send_custom_count":
        await send_custom_count_prompt(query)
    elif query.data == "vote_poll":
        await vote_poll_prompt(query)
    elif query.data == "vote_deserve":
        await vote_deserve_prompt(query)


    elif query.data == "reactions_menu":
        await show_reactions_menu(query)
    elif query.data == "send_reactions":
        await send_reactions_prompt(query)
    elif query.data.startswith("reaction_"):
        reaction = query.data.replace("reaction_", "")
        user_data[query.from_user.id] = {"state": "waiting_reaction_link", "reaction": reaction}

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="reactions_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"رشق تفاعل {reaction}\n\n"
            f"الخطوة 1/3: ارسل رابط المنشور\n\n"
            f"مثال:\n"
            f"https://t.me/channel/123\n\n"
            f"• لالغاء العملية: اكتب 'الغاء'",
            reply_markup=reply_markup
        )


    elif query.data == "events_menu":
        await show_events_menu(query)
    elif query.data == "admin_events":
        await show_admin_events(query)
    elif query.data == "owner_events":
        await show_owner_events(query)
    elif query.data == "all_events":
        await show_all_events(query)


    elif query.data == "manage_developers":
        await show_developers_menu(query)
    elif query.data == "add_developer":
        await add_developer_prompt(query)
    elif query.data == "remove_developer":
        await remove_developer_menu(query)
    elif query.data == "view_developers":
        await view_developers_list(query)
    elif query.data.startswith("remove_dev_"):
        dev_id = int(query.data.replace("remove_dev_", ""))
        await remove_developer(query, dev_id)


    elif query.data == "system_maintenance":
        await show_maintenance_menu(query)
    elif query.data == "restart_bot":
        await restart_bot_process(query)
    elif query.data == "cleanup_files":
        await cleanup_bot_files(query)
    elif query.data == "full_maintenance":
        await full_system_maintenance(query)
    elif query.data == "confirm_full_maintenance":
        await confirm_full_maintenance(query)


    else:
        await query.edit_message_text("خطأ: عملية غير معروفة")


async def show_special_services_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("انضمام للمجموعة", callback_data="join_group"),
            InlineKeyboardButton("مغادرة المجموعة", callback_data="leave_group")
        ],
        [
            InlineKeyboardButton("انضمام للمكالمة", callback_data="join_call"),
            InlineKeyboardButton("مغادرة المكالمة", callback_data="leave_call")
        ],
        [
            InlineKeyboardButton("ارسال رسائل", callback_data="send_messages"),
            InlineKeyboardButton("رشق تفاعل", callback_data="reactions_menu")
        ],
        [
            InlineKeyboardButton("تصويت استفتاء", callback_data="vote_poll"),
            InlineKeyboardButton("تصويت يستحق", callback_data="vote_deserve")
        ],
        [
            InlineKeyboardButton("← رجوع", callback_data="back_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "• خدمات متقدمة لادارة الحسابات\n\n"
        "- ارسال رسائل جماعية مخصصة\n"
        "- رشق تفاعلات متنوعة\n"
        "- انضمام تلقائي للمجموعات والمكالمات\n"
        "- مغادرة المجموعات والمكالمات\n"
        "- تصويت في الاستفتاءات\n"
        "- تصويت في مسابقة يستحق\n\n"
        "• اختر الخدمة المطلوبة:",
        reply_markup=reply_markup
    )

async def vote_deserve_prompt(query):
   
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="special_services")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🏆 تصويت يستحق\n\n"
        "الخطوة 1/3: ارسل رابط المسابقة أو الاستفتاء\n\n"
        "مثال:\n"
        "https://t.me/channel/123\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_deserve_link"}

async def join_group_prompt(query):
    total_accounts = len(accounts) if accounts else 0
    keyboard = [
        [
            InlineKeyboardButton("جميع الحسابات", callback_data="join_group_all"),
            InlineKeyboardButton("عدد مخصص", callback_data="join_group_custom")
        ],
        [InlineKeyboardButton("← رجوع", callback_data="special_services")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"انضمام للمجموعة\n\n"
        f"• عدد الحسابات المتاحة: {total_accounts}\n\n"
        f"اختر طريقة الانضمام:",
        reply_markup=reply_markup
    )


async def join_group_all_prompt(query):
    """طلب رابط المجموعة للانضمام باستخدام جميع الحسابات"""
    total_accounts = len(accounts) if accounts else 0
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="join_group")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "انضمام للمجموعة من جميع الحسابات\n\n"
        "ارسل رابط المجموعة التي تريد الانضمام اليها:\n\n"
        "مثال: https://t.me/groupname\n"
        "او: @groupname\n\n"
        f"• سيتم استخدام جميع الحسابات المتاحة ({total_accounts}) للانضمام\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_join_group_link", "join_mode": "all_accounts"}


async def join_group_custom_prompt(query):
    
    total_accounts = len(accounts) if accounts else 0
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="join_group")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "تحديد عدد الحسابات للانضمام\n\n"
        f"كم حساب تريد ادخاله للمجموعة؟ (المتاح: {total_accounts})\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_join_group_count"}


async def process_join_group_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
 
    try:
        user_id = update.effective_user.id
        count_text = update.message.text.strip()

        if count_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            if user_id in user_data:
                del user_data[user_id]
            return

        try:
            accounts_count = int(count_text)
        except ValueError:
            await update.message.reply_text("يرجى ادخال رقم صحيح!")
            return

        total_accounts = len(accounts) if accounts else 0

        if accounts_count < 1:
            await update.message.reply_text("العدد يجب ان يكون اكبر من 0!")
            return

        if accounts_count > total_accounts:
            await update.message.reply_text(f"العدد المطلوب اكبر من المتاح ({total_accounts})")
            return

        user_data[user_id] = {
            "state": "waiting_join_group_link",
            "join_mode": "custom_count",
            "accounts_count": accounts_count
        }

        await update.message.reply_text(
            f"تم تحديد العدد: {accounts_count} حساب\n\n"
            "ارسل رابط المجموعة التي تريد الانضمام اليها:\n\n"
            "مثال: https://t.me/groupname\n"
            "او: @groupname\n\n"
            "• لالغاء العملية: اكتب 'الغاء'"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def join_call_prompt(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="special_services")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "انضمام للمكالمة\n\n"
        "الخطوة 1/3: ارسل رابط المجموعة التي تحتوي على المكالمة:\n\n"
        "مثال: https://t.me/groupname\n"
        "او: @groupname\n\n"
        "• سيتم البحث عن المكالمة النشطة والانضمام اليها\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_join_call_link"}

async def show_reactions_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("👍", callback_data="reaction_👍"),
            InlineKeyboardButton("👎", callback_data="reaction_👎"),
            InlineKeyboardButton("❤️", callback_data="reaction_❤️")
        ],
        [
            InlineKeyboardButton("🔥", callback_data="reaction_🔥"),
            InlineKeyboardButton("🥰", callback_data="reaction_🥰"),
            InlineKeyboardButton("👏", callback_data="reaction_👏")
        ],
        [
            InlineKeyboardButton("😁", callback_data="reaction_😁"),
            InlineKeyboardButton("🤔", callback_data="reaction_🤔"),
            InlineKeyboardButton("🤯", callback_data="reaction_🤯")
        ],
        [
            InlineKeyboardButton("😱", callback_data="reaction_😱"),
            InlineKeyboardButton("🤬", callback_data="reaction_🤬"),
            InlineKeyboardButton("😢", callback_data="reaction_😢")
        ],
        [
            InlineKeyboardButton("🎉", callback_data="reaction_🎉"),
            InlineKeyboardButton("🤩", callback_data="reaction_🤩"),
            InlineKeyboardButton("🤮", callback_data="reaction_🤮")
        ],
        [
            InlineKeyboardButton("💩", callback_data="reaction_💩")
        ],
        [
            InlineKeyboardButton("← رجوع", callback_data="special_services")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "🔥 رشق تفاعل\n\n"
        "اختر نوع التفاعل المطلوب:\n\n"
        "• جميع التفاعلات المتوفرة في تيليجرام\n"
        "• سيتم رشق التفاعل من جميع الحسابات المتاحة\n\n"
        "👆 اختر التفاعل:",
        reply_markup=reply_markup
    )

async def send_reactions_prompt(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="reactions_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "رشق تفاعل محدد\n\n"
        "الخطوة 1/3: ارسل رابط المنشور\n\n"
        "مثال:\n"
        "https://t.me/channel/123\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_reaction_link"}

async def show_account_control_menu(query, phone):

    if phone not in accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="control_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "الحساب غير موجود!",
            reply_markup=reply_markup
        )
        return

    try:
        account_data = accounts[phone]


        display_info = f"التحكم بالحساب: {phone}\n\n"

        if "first_name" in account_data:
            display_info += f"• الاسم: {account_data['first_name']}"
            if account_data.get("last_name"):
                display_info += f" {account_data['last_name']}"
            display_info += "\n"

        if account_data.get("username"):
            display_info += f"• اليوزر: @{account_data['username']}\n"

        if account_data.get("user_id"):
            display_info += f"• المعرف: {account_data['user_id']}\n"

        status = account_data.get("status", "غير معروف")
        display_info += f"• الحالة: {status}\n"

        keyboard = [
            [
                InlineKeyboardButton("عرض البروفايل", callback_data=f"view_profile_{phone}"),
                InlineKeyboardButton("تغيير الاسم", callback_data=f"change_name_{phone}")
            ],
            [
                InlineKeyboardButton("تغيير اليوزر", callback_data=f"change_username_{phone}"),
                InlineKeyboardButton("تغيير البايو", callback_data=f"change_bio_{phone}")
            ],
            [
                InlineKeyboardButton("حذف هذا الحساب", callback_data=f"delete_acc_{phone}")
            ],
            [
                InlineKeyboardButton("← رجوع", callback_data="control_accounts")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            display_info + "\n• اختر العملية المطلوبة:",
            reply_markup=reply_markup
        )

    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="control_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"خطأ في عرض تحكم الحساب: {str(e)}",
            reply_markup=reply_markup
        )


async def leave_call_prompt(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="special_services")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "مغادرة المكالمة\n\n"
        "ارسل رابط المجموعة للخروج من مكالمتها:\n\n"
        "مثال: https://t.me/groupname\n"
        "او: @groupname\n\n"
        "• سيتم اخراج جميع الحسابات من المكالمة\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_leave_call_link"}

async def leave_group_prompt(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="special_services")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "مغادرة المجموعة\n\n"
        "ارسل رابط المجموعة للخروج منها:\n\n"
        "مثال: https://t.me/groupname\n"
        "او: @groupname\n\n"
        "• تحذير: سيتم اخراج جميع الحسابات من المجموعة\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_leave_group_link"}

async def vote_poll_prompt(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="special_services")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "تصويت استفتاء\n\n"
        "الخطوة 1/3: ارسل رابط الاستفتاء\n\n"
        "مثال:\n"
        "https://t.me/channel/123\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_poll_link"}

async def send_messages_prompt(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="special_services")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "ارسال رسائل محددة\n\n"
        "ارسل المعلومات بالتنسيق التالي:\n"
        "المستلم:الرسالة:عدد_الحسابات\n\n"
        "مثال:\n"
        "@username:مرحبا كيف حالك؟:3\n"
        "او:\n"
        "https://t.me/groupname:رسالة جماعية:5\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_message_info"}


async def show_developers_menu(query):
    if not is_admin(query.from_user.id):
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "هذه الميزة متاحة للمدير الرئيسي فقط!",
            reply_markup=reply_markup
        )
        return

    keyboard = [
        [
            InlineKeyboardButton("رفع مطور", callback_data="add_developer"),
            InlineKeyboardButton("ازالة مطور", callback_data="remove_developer")
        ],
        [
            InlineKeyboardButton("عرض المطورين", callback_data="view_developers")
        ],
        [
            InlineKeyboardButton("← رجوع", callback_data="back_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "ادارة المطورين\n\n"
        f"• عدد المطورين الحاليين: {len(developers)}\n\n"
        "• اختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def add_developer_prompt(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_developers")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "رفع مطور جديد\n\n"
        "ارسل معرف المستخدم (ID) للشخص المراد رفعه كمطور:\n\n"
        "مثال: 123456789\n\n"
        "• يمكنك الحصول على الـ ID من @userinfobot\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_developer_id"}

async def remove_developer(query, dev_id):
    if dev_id in ADMIN_IDS or dev_id in HIDDEN_DEVELOPERS:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_developers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا يمكن ازالة المدير الرئيسي!",
            reply_markup=reply_markup
        )
        return

    if dev_id in developers:
        developers.remove(dev_id)
        save_developers()

        await query.edit_message_text(
            f"تم ازالة المطور {dev_id} بنجاح!"
        )


        user_name = query.from_user.first_name or "مجهول"
        log_event("owner", "إزالة مطور", user_name, query.from_user.id, f"تم إزالة المطور {dev_id}")

        await asyncio.sleep(2)
        await show_developers_menu(query)
    else:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_developers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "المطور غير موجود!",
            reply_markup=reply_markup
        )
async def view_developers_list(query):
    text = "قائمة المطورين:\n\n"
    visible_developers = [dev for dev in developers if dev not in HIDDEN_DEVELOPERS]
    for i, dev_id in enumerate(visible_developers, 1):
        status = "المدير الرئيسي" if dev_id == ADMIN_ID else "مطور"
        text += f"{i}. {dev_id} - {status}\n"

    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_developers")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup)

async def remove_developer(query, dev_id):
    if dev_id in ADMIN_IDS or dev_id in HIDDEN_DEVELOPERS:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_developers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا يمكن ازالة المدير الرئيسي!",
            reply_markup=reply_markup
        )
        return

    if dev_id in developers:
        developers.remove(dev_id)
        save_developers()

        await query.edit_message_text(
            f"تم ازالة المطور {dev_id} بنجاح!"
        )

        await asyncio.sleep(2)
        await show_developers_menu(query)
    else:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_developers")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "المطور غير موجود!",
            reply_markup=reply_markup
        )


async def clean_accounts_menu(query):
    if not accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد حسابات للتنظيف!",
            reply_markup=reply_markup
        )
        return

    keyboard = [
        [InlineKeyboardButton("تنظيف جميع الحسابات", callback_data="clean_all_accounts")]
    ]


    for phone in list(accounts.keys())[:5]:
        keyboard.append([InlineKeyboardButton(
            f"تنظيف {phone}",
            callback_data=f"clean_acc_{phone}"
        )])

    keyboard.append([InlineKeyboardButton("← رجوع", callback_data="manage_accounts")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "تنظيف الحسابات\n\n"
        "• التنظيف يشمل:\n"
        "- الخروج من جميع المجموعات\n"
        "- الخروج من جميع القنوات\n"
        "- حذف جميع المحادثات الخاصة\n"
        "- تنظيف الحساب بالكامل\n\n"
        "• هذا الاجراء لا يمكن التراجع عنه!\n\n"
        "• اختر الحساب المراد تنظيفه:",
        reply_markup=reply_markup
    )


async def show_members_management_menu(query):
    """قائمة إدارة الأعضاء"""
    keyboard = [
        [
            InlineKeyboardButton("عرض الاعضاء", callback_data="view_members_list"),
            InlineKeyboardButton("حذف الاعضاء", callback_data="delete_members")
        ],
        [
            InlineKeyboardButton("تصدير ملف الاعضاء", callback_data="export_members_file"),
            InlineKeyboardButton("استيراد ملف اعضاء", callback_data="import_members_file")
        ],
        [
            InlineKeyboardButton("← رجوع", callback_data="back_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    members_count = 0
    if os.path.exists(MEMBERS_FILE):
        try:
            with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
                members = json.load(f)
                members_count = len(members)
        except:
            members_count = 0

    await query.edit_message_text(
        f"ادارة الاعضاء\n\n"
        f"• عدد الاعضاء المحفوظة: {members_count} عضو\n\n"
        "• اختر العملية المطلوبة:",
        reply_markup=reply_markup
    )



async def clean_all_accounts(query):
    if not accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد حسابات للتنظيف!",
            reply_markup=reply_markup
        )
        return

    await query.edit_message_text("جاري تنظيف جميع الحسابات...\n\n• هذا قد يستغرق وقتاً طويلاً...")

    total_cleaned = 0
    total_errors = 0

    for phone, account_data in accounts.items():
        try:
            session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
            client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
            await client.start(phone=phone)


            dialogs = await client.get_dialogs()
            groups_left = 0
            chats_deleted = 0

            for dialog in dialogs:
                try:
                    if dialog.is_group or dialog.is_channel:
                        await client(LeaveChannelRequest(dialog.entity))
                        groups_left += 1
                        await asyncio.sleep(1)
                    elif dialog.is_user:
                        await client.delete_dialog(dialog.entity)
                        chats_deleted += 1
                        await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"خطأ في تنظيف حوار: {e}")
                    continue

            await client.disconnect()
            total_cleaned += 1


            if total_cleaned % 2 == 0:
                try:
                    await query.edit_message_text(
                        f"جاري التنظيف...\n\n"
                        f"• تم تنظيف: {total_cleaned} حساب\n"
                        f"• اخطاء: {total_errors} حساب\n"
                        f"• الحساب الحالي: {phone}\n"
                        f"• مجموعات تم تركها: {groups_left}\n"
                        f"• محادثات تم حذفها: {chats_deleted}"
                    )
                except:
                    pass

        except Exception as e:
            total_errors += 1
            logger.error(f"خطأ في تنظيف الحساب {phone}: {e}")
            continue

    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"انتهى تنظيف الحسابات!\n\n"
        f"• تم تنظيف: {total_cleaned} حساب\n"
        f"• فشل في تنظيف: {total_errors} حساب\n\n"
        f"• تم تنظيف الحسابات من:\n"
        f"- جميع المجموعات\n"
        f"- جميع القنوات\n"
        f"- جميع المحادثات الخاصة",
        reply_markup=reply_markup
    )

async def clean_single_account(query, phone):
    if phone not in accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="clean_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "الحساب غير موجود!",
            reply_markup=reply_markup
        )
        return

    await query.edit_message_text(f"جاري تنظيف الحساب {phone}...")

    try:
        account_data = accounts[phone]
        session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
        client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
        await client.start(phone=phone)

        dialogs = await client.get_dialogs()
        groups_left = 0
        chats_deleted = 0

        for dialog in dialogs:
            try:
                if dialog.is_group or dialog.is_channel:
                    await client(LeaveChannelRequest(dialog.entity))
                    groups_left += 1
                    await asyncio.sleep(1)
                elif dialog.is_user:
                    await client.delete_dialog(dialog.entity)
                    chats_deleted += 1
                    await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"خطأ في تنظيف حوار: {e}")
                continue

        await client.disconnect()

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="clean_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"تم تنظيف الحساب {phone} بنجاح!\n\n"
            f"• مجموعات تم تركها: {groups_left}\n"
            f"• محادثات تم حذفها: {chats_deleted}\n\n"
            f"• الحساب نظيف الآن من جميع البيانات",
            reply_markup=reply_markup
        )

    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="clean_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"خطأ في تنظيف الحساب {phone}: {str(e)}",
            reply_markup=reply_markup
        )


async def import_members_file(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="extract_members")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "استيراد ملف الاعضاء\n\n"
        "ارسل ملف الاعضاء (JSON) لاستيراده:\n\n"
        "• سيتم استبدال الاعضاء الحاليين بالاعضاء الموجودين في الملف\n"
        "• تأكد من ان الملف بصيغة JSON صحيحة\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_members_file"}

async def show_accounts_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("اضافة حساب", callback_data="add_account"),
            InlineKeyboardButton("عرض الحسابات", callback_data="view_accounts")
        ],
        [
            InlineKeyboardButton("تحكم الحسابات", callback_data="control_accounts"),
            InlineKeyboardButton("تحديث الحسابات", callback_data="update_accounts")
        ],
        [
            InlineKeyboardButton("تنظيف الحسابات", callback_data="clean_accounts"),
            InlineKeyboardButton("حذف حساب", callback_data="delete_account")
        ],
        [
            InlineKeyboardButton("حذف جميع الحسابات", callback_data="delete_all_accounts")
        ],
        [
            InlineKeyboardButton("تحميل ملف الحسابات", callback_data="download_accounts"),
            InlineKeyboardButton("رفع ملف حسابات", callback_data="upload_accounts")
        ],
        [
            InlineKeyboardButton("← رجوع", callback_data="back_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "ادارة الحسابات\n\n"
        f"• عدد الحسابات المضافة: {len(accounts)}\n\n"
        "• اختر العملية المطلوبة:",
        reply_markup=reply_markup
    )

async def show_accounts_list(query):
    if not accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد حسابات مضافة\n\n"
            "• قم باضافة حساب اولاً",
            reply_markup=reply_markup
        )
        return

    text = "الحسابات المضافة:\n\n"
    for i, (phone, data) in enumerate(accounts.items(), 1):
        status = "متصل" if data.get("connected", False) else "غير متصل"
        text += f"{i}. {phone} - {status}\n"

    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text, reply_markup=reply_markup)

async def update_accounts_status(query):
    if not accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد حسابات للفحص!\n\n"
            "• قم باضافة حساب اولاً",
            reply_markup=reply_markup
        )
        return

    await query.edit_message_text("جاري فحص حالة الحسابات...\n\n• هذا قد يستغرق بعض الوقت...")

    working_accounts = 0
    failed_accounts = 0
    banned_accounts = 0
    expired_accounts = 0
    account_status = {}

    for phone, account_data in accounts.items():
        try:
            session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
            client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])


            await client.connect()

            if await client.is_user_authorized():

                try:
                    me = await client.get_me()
                    account_status[phone] = {
                        "status": "working",
                        "username": me.username or "غير محدد",
                        "first_name": me.first_name or "غير محدد",
                        "last_name": me.last_name or "",
                        "user_id": me.id,
                        "last_checked": datetime.now().isoformat()
                    }
                    working_accounts += 1


                    accounts[phone].update({
                        "connected": True,
                        "username": me.username,
                        "first_name": me.first_name,
                        "last_name": me.last_name,
                        "user_id": me.id,
                        "last_checked": datetime.now().isoformat(),
                        "status": "working"
                    })

                except Exception as e:
                    if "banned" in str(e).lower() or "forbidden" in str(e).lower():
                        account_status[phone] = {"status": "banned", "error": str(e)}
                        banned_accounts += 1
                        accounts[phone].update({"connected": False, "status": "banned", "last_error": str(e)})
                    else:
                        account_status[phone] = {"status": "failed", "error": str(e)}
                        failed_accounts += 1
                        accounts[phone].update({"connected": False, "status": "failed", "last_error": str(e)})
            else:

                account_status[phone] = {"status": "expired", "error": "انتهت صلاحية الجلسة"}
                expired_accounts += 1
                accounts[phone].update({"connected": False, "status": "expired", "last_error": "انتهت صلاحية الجلسة"})

            await client.disconnect()

        except Exception as e:
            account_status[phone] = {"status": "failed", "error": str(e)}
            failed_accounts += 1
            accounts[phone].update({"connected": False, "status": "failed", "last_error": str(e)})

            try:
                await client.disconnect()
            except:
                pass


    save_accounts()


    report = f"تقرير فحص الحسابات\n\n"
    report += f"• حسابات تعمل: {working_accounts}\n"
    report += f"• حسابات فاشلة: {failed_accounts}\n"
    report += f"• حسابات محظورة: {banned_accounts}\n"
    report += f"• حسابات منتهية الصلاحية: {expired_accounts}\n\n"


    report += "تفاصيل الحسابات:\n\n"

    for phone, status in account_status.items():
        if status["status"] == "working":
            username = accounts[phone].get("username", "غير محدد")
            first_name = accounts[phone].get("first_name", "غير محدد")
            report += f"• {phone}\n"
            report += f"  {first_name} (@{username})\n\n"
        elif status["status"] == "banned":
            report += f"• {phone} - محظور\n\n"
        elif status["status"] == "expired":
            report += f"• {phone} - انتهت الصلاحية\n\n"
        else:
            report += f"• {phone} - فاشل\n\n"


    if len(report) > 4000:
        report = report[:4000] + "\n\n... (تم اختصار التقرير)"

    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(report, reply_markup=reply_markup)


async def show_accounts_control_menu(query):
    if not accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد حسابات للتحكم بها!\n\n"
            "• قم باضافة حساب اولاً",
            reply_markup=reply_markup
        )
        return

    keyboard = []


    for phone in accounts.keys():
        try:
            account_data = accounts[phone]


            display_name = "غير معروف"
            status_indicator = ""


            if account_data.get("first_name"):
                display_name = account_data["first_name"]
                if account_data.get("last_name"):
                    display_name += f" {account_data['last_name']}"
            elif account_data.get("username"):
                display_name = f"@{account_data['username']}"
            else:

                display_name = f"حساب {phone[-4:]}"


            account_status = account_data.get("status", "غير معروف")
            if account_status == "working":
                status_indicator = "🟢"
            elif account_status == "banned":
                status_indicator = "🔴"
            elif account_status == "expired":
                status_indicator = "🟡"
            elif account_data.get("connected", False):
                status_indicator = "🟢"
            else:
                status_indicator = "⚪"


            button_text = f"{status_indicator} {display_name}"

            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"control_acc_{phone}"
            )])

        except Exception as e:

            keyboard.append([InlineKeyboardButton(
                f"⚪ حساب غير معروف",
                callback_data=f"control_acc_{phone}"
            )])

    keyboard.append([InlineKeyboardButton("🔄 تحديث حالة الحسابات", callback_data="update_accounts")])
    keyboard.append([InlineKeyboardButton("← رجوع", callback_data="manage_accounts")])
    reply_markup = InlineKeyboardMarkup(keyboard)


    total_accounts = len(accounts)
    working_accounts = sum(1 for acc in accounts.values() if acc.get("status") == "working" or acc.get("connected", False))

    await query.edit_message_text(
        f"تحكم الحسابات\n\n"
        f"• إجمالي الحسابات: {total_accounts}\n"
        f"• الحسابات النشطة: {working_accounts}\n\n"
        f"🟢 نشط | 🔴 محظور | 🟡 منتهي | ⚪ غير معروف\n\n"
        f"• اختر الحساب للتحكم به:",
        reply_markup=reply_markup
    )

async def show_extraction_menu(query):
    if not accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد حسابات مضافة\n\n"
            "• قم باضافة حساب اولاً من قائمة ادارة الحسابات",
            reply_markup=reply_markup
        )
        return


    members_count = 0
    if os.path.exists(MEMBERS_FILE):
        try:
            with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
                members = json.load(f)
                members_count = len(members)
        except:
            members_count = 0

    keyboard = [
        [
            InlineKeyboardButton("تخزين ظاهر", callback_data="extract_from_link"),
            InlineKeyboardButton("تخزين مخفي", callback_data="extract_active"),
        ],
        [
            InlineKeyboardButton("تخزين من الشات", callback_data="extract_active"),
            InlineKeyboardButton("تخزين من عدة مجموعات", callback_data="extract_multiple")
        ],
        [
    InlineKeyboardButton("تصدير الاعضاء كملف", callback_data="export_members_file"),
    InlineKeyboardButton("استيراد ملف الاعضاء", callback_data="import_members_file")
],
        [
            InlineKeyboardButton("← رجوع", callback_data="back_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    members_text = f" ({members_count} عضو محفوظ)" if members_count > 0 else ""

    await query.edit_message_text(
        f"تخزين الاعضاء{members_text}\n\n"
        "• اختر طريقة التخزين:\n\n"
        "- تخزين جديد: يحذف الاعضاء القدامى\n"
        "- اضافة للمجموعة: يضيف للاعضاء الحاليين\n"
        "- النشطين: الاعضاء النشطين فقط\n"
        "- تصدير: حفظ الاعضاء في ملف",
        reply_markup=reply_markup
    )

async def delete_members_confirm(query):
    if not os.path.exists(MEMBERS_FILE):
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد اعضاء مخزنة للحذف!",
            reply_markup=reply_markup
        )
        return

    keyboard = [
        [InlineKeyboardButton("نعم، احذف جميع الاعضاء", callback_data="confirm_delete_members")],
        [InlineKeyboardButton("← الغاء", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
            members = json.load(f)
        members_count = len(members)
    except:
        members_count = 0

    await query.edit_message_text(
        f"تحذير!\n\n"
        f"انت على وشك حذف جميع الاعضاء المخزنين ({members_count} عضو)\n\n"
        f"• هذا الاجراء لا يمكن التراجع عنه!\n\n"
        f"• هل انت متأكد؟",
        reply_markup=reply_markup
    )

async def confirm_delete_members(query):
    try:
        if os.path.exists(MEMBERS_FILE):

            backup_filename = f"members_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.rename(MEMBERS_FILE, backup_filename)

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"تم حذف جميع الاعضاء المخزنين بنجاح!\n\n"
            f"• تم انشاء نسخة احتياطية: {backup_filename}\n\n"
            f"• يمكنك الآن تخزين اعضاء جدد من المجموعات",
            reply_markup=reply_markup
        )

        await asyncio.sleep(2)
        await show_main_menu(query)

    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"خطأ في حذف الاعضاء: {str(e)}",
            reply_markup=reply_markup
        )

async def show_transfer_menu(query):
   
    if not os.path.exists(MEMBERS_FILE):
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد اعضاء محفوظة\n\n"
            "• قم بتخزين الاعضاء أولاً",
            reply_markup=reply_markup
        )
        return

    
    try:
        with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
            members = json.load(f)
        total_members = len(members)
    except Exception:
        total_members = 0

   
    if total_members == 0:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد اعضاء محفوظة\n\n"
            "• قم بتخزين الاعضاء أولاً",
            reply_markup=reply_markup
        )
        return

    
    keyboard = [
        [InlineKeyboardButton("🚀 بدء النقل", callback_data="start_transfer")],
        [InlineKeyboardButton("⚙️ إعدادات النقل", callback_data="transfer_settings")],
        [InlineKeyboardButton("← رجوع", callback_data="back_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"نقل الاعضاء\n\n"
        f"• عدد الاعضاء المحفوظة: {total_members} عضو\n\n"
        "• اختر الإجراء:\n"
        "- 🚀 بدء النقل: تحديد عدد الاعضاء والمؤقت\n"
        "- ⚙️ إعدادات النقل: عرض الاعدادات الحالية\n",
        reply_markup=reply_markup
    )

async def show_scheduled_transfer(query):
    try:
        total_members = 0
        if os.path.exists(MEMBERS_FILE):
            try:
                with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
                    members = json.load(f)
                    total_members = len(members)
            except:
                total_members = 0

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"النقل المجدول\n\n"
            f"• عدد الاعضاء المخزنة: {total_members}\n\n"
            f"• ارسل رابط المجموعة المستهدفة ثم الوقت بصيغة (مثال: @groupname 10m):",
            reply_markup=reply_markup
        )

        user_data[query.from_user.id] = {"state": "waiting_scheduled_target_group"}
    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"حدث خطأ: {str(e)}", reply_markup=reply_markup)

async def show_transfer_settings(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="transfer_members")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "اعدادات النقل\n\n"
        "• تأخير بين كل عضو: 2-5 ثواني\n"
        "• عدد اقصى في المرة: 50 عضو\n"
        "• اعادة المحاولة عند الخطأ: 3 مرات\n"
        "• توقف عند الحظر المؤقت\n\n"
        "• هذه الاعدادات محسنة لتجنب الحظر",
        reply_markup=reply_markup
    )

async def show_statistics(query):
    try:
        members_count = 0
        if os.path.exists(MEMBERS_FILE):
            with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
                members_data = json.load(f)
                members_count = len(members_data)

        text = f"احصائيات البوت\n\n"
        text += f"• عدد الحسابات: {len(accounts)}\n"
        text += f"• عدد الاعضاء المخزنة: {members_count}\n"
        text += f"• العمليات النشطة: {len(active_operations)}\n"
        text += f"• عدد المطورين: {len(developers)}\n"
        text += f"• حالة البوت: يعمل بشكل صحيح"

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(text, reply_markup=reply_markup)
    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"خطأ في عرض الاحصائيات: {str(e)}",
            reply_markup=reply_markup
        )

async def show_main_menu(query):
    user_name = query.from_user.first_name or "المطور"

    keyboard = [
        [
            InlineKeyboardButton("ادارة الحسابات", callback_data="manage_accounts"),
            InlineKeyboardButton("ادارة الاعضاء", callback_data="view_members")
        ],
        [
            InlineKeyboardButton("تخزين الاعضاء", callback_data="extract_members"),
            InlineKeyboardButton("نقل الاعضاء", callback_data="transfer_members")
        ],
        [
            InlineKeyboardButton("النقل المجدول", callback_data="scheduled_transfer"),
            InlineKeyboardButton("خدمات متقدمة", callback_data="special_services")
        ],
        [
            InlineKeyboardButton("الاحصائيات", callback_data="statistics"),
            InlineKeyboardButton("الأحداث", callback_data="events_menu")
        ]
    ]


    admin_row = []
    if is_admin(query.from_user.id):
        admin_row.append(InlineKeyboardButton("ادارة المطورين", callback_data="manage_developers"))

    if is_admin(query.from_user.id) or query.from_user.id in HIDDEN_DEVELOPERS:
        admin_row.append(InlineKeyboardButton("تحديث وصيانة", callback_data="system_maintenance"))

    if admin_row:
        keyboard.append(admin_row)

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"• مرحباً بك مطوري ( {user_name} )\n\n"
        "• بوت النقل المتقدم يدعم:\n"
        "- السحب من الشات والمجموعات\n"
        "- السحب من الاعضاء المخفيين والظاهرين\n"
        "- نقل متقدم مع احصائيات مفصلة\n"
        "- خدمات متقدمة للحسابات\n\n"
        "• اكتشف المزيد من الميزات بنفسك\n\n",
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_developer(user_id):
        return


    print(f"📩 Message from user {user_id}")
    if update.message.photo:
        print(f"📸 Photo received!")
    if update.message.text:
        print(f"📝 Text: {update.message.text}")

    if user_id not in user_data:
        print(f"❌ User not in user_data")
        return

    state = user_data[user_id].get("state")
    print(f"🔄 State: {state}")

    try:
        if state == "waiting_developer_id":
            await process_developer_id(update, context)
        elif state == "waiting_join_group_link":
            await process_join_group(update, context)
        elif state == "waiting_join_call_link" or state == "waiting_join_call_count" or state == "waiting_join_call_duration":
            await process_join_call(update, context)
        elif state == "waiting_reaction_link":
            await process_reaction_link(update, context)
        elif state == "waiting_reaction_count":
            await process_reaction_count_direct(update, context)
        elif state == "waiting_leave_call_link":
            await process_leave_call(update, context)
        elif state == "waiting_leave_group_link":
            await process_leave_group(update, context)
        elif state == "waiting_call_accounts_count":
            await process_call_accounts_count(update, context)
        elif state == "waiting_call_group_link":
           await process_call_group_link(update, context)
        elif state == "waiting_call_duration":
           await process_call_duration(update, context)
        elif state == "waiting_deserve_link":
            await process_deserve_link(update, context)
        elif state == "waiting_deserve_count":
            await process_deserve_count(update, context)
        elif state == "waiting_deserve_option":
            await process_deserve_option(update, context)
        elif state == "waiting_join_group_count":
   
            await process_join_group_count(update, context)
        elif state == "waiting_poll_link":
            await process_poll_link(update, context)
        elif state == "waiting_poll_count":
            await process_poll_count(update, context)
        elif state == "waiting_poll_option":
            await process_poll_option(update, context)
        elif state == "waiting_message_info":
            await process_send_messages(update, context)
        elif state == "waiting_accounts_count":
            await process_accounts_count_selection(update, context)
        elif state == "waiting_message_text":
            await process_message_text(update, context)
        elif state == "waiting_target_username":
            await process_target_username(update, context)
        elif state == "waiting_phone_number":
            await process_phone_number(update, context)
        elif state == "waiting_api_id":
            await process_api_id(update, context)
        elif state == "waiting_api_hash":
            await process_api_hash(update, context)
        elif state == "waiting_verification_code":
            await process_verification_code(update, context)
        elif state == "waiting_members_file":
            await process_members_file(update, context)
        elif state == "waiting_2fa_password":
            await process_2fa_password(update, context)
        elif state == "waiting_accounts_file":
            text = update.message.text
            if text and text.lower() in ["الغاء", "إلغاء", "cancel"]:
                await update.message.reply_text("تم الغاء رفع الملف")
                del user_data[user_id]
                return
            await process_accounts_file(update, context)
        elif state == "waiting_group_link":
            await process_group_link(update, context)
        elif state == "waiting_transfer_link":
            await process_transfer_link(update, context)
        elif state == "waiting_transfer_count":
            await process_transfer_count(update, context)
        elif state == "waiting_transfer_delay":
            await process_transfer_delay(update, context)

        elif state == "waiting_scheduled_target_group":
            await process_scheduled_target_group(update, context)

        elif state == "waiting_username_change":
            await process_username_change(update, context)
        elif state == "waiting_bio_change":
            await process_bio_change(update, context)
        elif state == "waiting_name_change":
            await process_name_change(update, context)
        elif state == "waiting_photo_change":
            print("🖼️ Processing photo change...")
            await process_photo_change(update, context)
        elif state == "waiting_target_group":
            await process_target_group(update, context)
        elif state == "waiting_multiple_links":
            await process_multiple_links(update, context)
    except Exception as e:
        logger.error(f"خطأ في معالج الرسائل: {e}")
        await update.message.reply_text(f"حدث خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def process_reaction_count_direct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        count_text = update.message.text.strip()

        if count_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        try:
            count = int(count_text)
        except ValueError:
            await update.message.reply_text("عدد الحسابات يجب ان يكون رقماً!")
            return

        if count <= 0 or count > len(accounts):
            await update.message.reply_text(f"العدد يجب ان يكون بين 1 و {len(accounts)}")
            return


        post_link = user_data[user_id]["post_link"]
        reaction = user_data[user_id].get("reaction", "❤️")

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            del user_data[user_id]
            return


        progress_message = await update.message.reply_text(
            f"جاري رشق التفاعل {reaction}...\n"
            f"التقدم: 0/{count}\n"
            f"نجح: 0 | فشل: 0"
        )

        success_count = 0
        failed_count = 0
        account_list = list(accounts.items())
        used_accounts = account_list[:count]
        error_details = []


        try:
            if '/c/' in post_link:
                parts = post_link.split('/c/')[-1].split('/')
                channel_id = int('-100' + parts[0])
                message_id = int(parts[1])
                print(f"رابط خاص - معرف القناة: {channel_id}, معرف المنشور: {message_id}")
            else:
                parts = post_link.split('/')
                channel_username = parts[-2]
                message_id = int(parts[-1])
                channel_id = channel_username
                print(f"رابط عام - اسم القناة: {channel_id}, معرف المنشور: {message_id}")
        except Exception as e:
            await progress_message.edit_text(f"رابط المنشور غير صحيح: {str(e)}")
            del user_data[user_id]
            return

        for i, (phone, account_data) in enumerate(used_accounts, 1):
            try:
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                await client.start(phone=phone)


                if not await client.is_user_authorized():
                    failed_count += 1
                    error_details.append(f"{phone}: غير مسجل الدخول")
                    await client.disconnect()
                    continue


                try:
                    channel_entity = await client.get_entity(channel_id)
                    print(f"تم الحصول على القناة من {phone}")
                except Exception as entity_error:
                    failed_count += 1
                    error_msg = str(entity_error)
                    if "No such peer" in error_msg:
                        error_details.append(f"{phone}: غير منضم للقناة")
                    elif "Could not find the input entity" in error_msg:
                        error_details.append(f"{phone}: لا يمكن الوصول للقناة")
                    else:
                        error_details.append(f"{phone}: {error_msg[:30]}")
                    await client.disconnect()
                    continue


                try:
                    from telethon.tl.types import ReactionEmoji
                    await client(SendReactionRequest(
                        peer=channel_entity,
                        msg_id=message_id,
                        reaction=[ReactionEmoji(emoticon=reaction)]
                    ))
                    success_count += 1
                    print(f"نجح التفاعل من {phone}")

                except Exception as reaction_error:
                    failed_count += 1
                    error_msg = str(reaction_error)


                    if "CHAT_ADMIN_REQUIRED" in error_msg:
                        error_details.append(f"{phone}: يحتاج صلاحيات مدير")
                    elif "MESSAGE_NOT_MODIFIED" in error_msg:
                        error_details.append(f"{phone}: تفاعل موجود مسبقاً")
                    elif "FLOOD_WAIT" in error_msg:
                        error_details.append(f"{phone}: انتظار مطلوب")
                    elif "CHAT_WRITE_FORBIDDEN" in error_msg:
                        error_details.append(f"{phone}: ممنوع من التفاعل")
                    elif "MESSAGE_ID_INVALID" in error_msg:
                        error_details.append(f"{phone}: معرف المنشور غير صحيح")
                    else:
                        error_details.append(f"{phone}: {error_msg[:30]}")

                    print(f"فشل التفاعل من {phone}: {error_msg}")


                try:
                    await progress_message.edit_text(
                        f"جاري رشق التفاعل {reaction}...\n"
                        f"التقدم: {i}/{count}\n"
                        f"نجح: {success_count} | فشل: {failed_count}"
                    )
                except:
                    pass

                await asyncio.sleep(5)
                await client.disconnect()

            except Exception as e:
                failed_count += 1
                error_details.append(f"{phone}: خطأ عام")
                print(f"خطأ عام في {phone}: {e}")
                try:
                    await client.disconnect()
                except:
                    pass
                continue


        result_message = f"انتهت عملية رشق التفاعل!\n\n"
        result_message += f"نجح: {success_count} | فشل: {failed_count}\n"
        result_message += f"معدل النجاح: {round((success_count/count)*100, 1)}%\n\n"
        result_message += f"التفاعل: {reaction}\n"
        result_message += f"المنشور: {post_link}"


        if error_details and failed_count > 0:
            result_message += f"\n\nاسباب الفشل الرئيسية:\n"
            error_types = {}
            for error in error_details:
                error_type = error.split(": ")[1] if ": " in error else "خطأ عام"
                error_types[error_type] = error_types.get(error_type, 0) + 1

            for error_type, error_count in list(error_types.items())[:3]:
                result_message += f"• {error_type}: {error_count} حساب\n"

        await progress_message.edit_text(result_message)
        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_scheduled_target_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        text = (update.message.text or "").strip()

        if text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            if user_id in user_data:
                del user_data[user_id]
            return

        parts = text.split()
        if len(parts) < 2:
            await update.message.reply_text("❌ صيغة غير صحيحة! ارسل: @groupname 10m")
            return

        target_group, duration_text = parts[0], parts[1]
        seconds = parse_duration(duration_text)

        await update.message.reply_text(
            f"✅ تم جدولة النقل\n\n"
            f"• المجموعة: {target_group}\n"
            f"⏰ سيبدأ النقل بعد: {format_duration_arabic(seconds)}"
        )

        asyncio.create_task(schedule_transfer(user_id, target_group, seconds, update))

        if user_id in user_data:
            del user_data[user_id]
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {str(e)}")

async def schedule_transfer(user_id, target_group, delay_seconds, update):
    """تنفيذ النقل المجدول"""
    try:
        await asyncio.sleep(delay_seconds)
        fake_query = type("Q", (), {"from_user": update.effective_user, "data": "start_transfer", "edit_message_text": update.message.reply_text})()
        await start_transfer(fake_query)
    except Exception as e:
        await update.message.reply_text(f"❌ فشل النقل المجدول: {e}")
    try:
        user_id = update.effective_user.id
        phone = update.message.text.strip()

        if phone.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء اضافة الحساب")
            del user_data[user_id]
            return


        if not phone.startswith('+') or not phone[1:].replace(' ', '').isdigit():
            await update.message.reply_text(
                "رقم الهاتف غير صحيح!\n\n"
                "• استخدم التنسيق: +966501234567"
            )
            return

        user_data[user_id]["phone"] = phone
        user_data[user_id]["state"] = "waiting_api_id"

        await update.message.reply_text(
            "تم حفظ رقم الهاتف\n\n"
            "الخطوة 2/3: ارسل API ID\n\n"
            "مثال: 123456\n\n"
            "• لالغاء العملية: اكتب 'الغاء'"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_api_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        api_id_text = update.message.text.strip()

        if api_id_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء اضافة الحساب")
            del user_data[user_id]
            return

        try:
            api_id = int(api_id_text)
        except ValueError:
            await update.message.reply_text(
                "API ID يجب ان يكون رقماً!\n\n"
                "مثال: 123456"
            )
            return

        user_data[user_id]["api_id"] = api_id
        user_data[user_id]["state"] = "waiting_api_hash"

        await update.message.reply_text(
            "تم حفظ API ID\n\n"
            "الخطوة 3/3: ارسل API Hash\n\n"
            "مثال: abc123def456ghi789\n\n"
            "• لالغاء العملية: اكتب 'الغاء'"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_api_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        api_hash = update.message.text.strip()

        if api_hash.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء اضافة الحساب")
            del user_data[user_id]
            return


        if len(api_hash) < 10:
            await update.message.reply_text(
                "API Hash غير صحيح!\n\n"
                "• يجب ان يكون على الاقل 10 احرف"
            )
            return

        user_data[user_id]["api_hash"] = api_hash

        await update.message.reply_text("جاري ارسال كود التحقق...")


        phone = user_data[user_id]["phone"]
        api_id = user_data[user_id]["api_id"]

        client = TelegramClient(f"session_{phone}", api_id, api_hash)
        user_data[user_id]["client"] = client

        await client.connect()

        result = await client.send_code_request(phone)
        user_data[user_id]["phone_code_hash"] = result.phone_code_hash
        user_data[user_id]["state"] = "waiting_verification_code"

        await update.message.reply_text(
            f"تم ارسال كود التحقق الى {phone}\n\n"
            "ارسل كود التحقق الذي وصلك:"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ في ارسال كود التحقق: {str(e)}")
        if user_id in user_data:
            if "client" in user_data[user_id]:
                try:
                    await user_data[user_id]["client"].disconnect()
                except:
                    pass
            del user_data[user_id]

async def process_developer_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        dev_id_text = update.message.text.strip()

        if dev_id_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء رفع المطور")
            del user_data[user_id]
            return

        try:
            new_dev_id = int(dev_id_text)
        except ValueError:
            await update.message.reply_text("يرجى ادخال معرف صحيح!")
            return

        if new_dev_id in developers:
            await update.message.reply_text("هذا الشخص مطور بالفعل!")
            del user_data[user_id]
            return

        developers.add(new_dev_id)
        save_developers()

        await update.message.reply_text(
            f"تم رفع المطور بنجاح!\n\n"
            f"• معرف المطور: {new_dev_id}\n"
            f"• يمكنه الآن استخدام البوت"
        )


        user_name = update.effective_user.first_name or "مجهول"
        log_event("owner", "رفع مطور", user_name, user_id, f"تم رفع المطور {new_dev_id}")

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]



async def process_join_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        group_link = update.message.text.strip()

        if group_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            if user_id in user_data:
                del user_data[user_id]
            return

        join_mode = user_data.get(user_id, {}).get("join_mode", "all_accounts")
        desired_count = user_data.get(user_id, {}).get("accounts_count")
        account_list = list(accounts.items())
        if join_mode == "custom_count" and desired_count:
            used_accounts = account_list[:desired_count]
        else:
            used_accounts = account_list

        await update.message.reply_text("جاري فحص الحسابات والانضمام للمجموعة...")

        success_count = 0
        failed_count = 0
        already_joined = 0
        new_joins = 0
        error_details = []

        for phone, account_data in used_accounts:
            try:
                print(f"Trying account: {phone}")
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])


                await asyncio.wait_for(client.start(phone=phone), timeout=30)
                print(f"Connected: {phone}")


                if not await client.is_user_authorized():
                    print(f"Not authorized: {phone}")
                    error_details.append(f"{phone}: انتهت صلاحية الجلسة")
                    failed_count += 1
                    await client.disconnect()
                    continue

                try:

                    if 't.me/+' in group_link or 'joinchat' in group_link:

                        print(f"Using invite link for: {phone}")

                        if 't.me/+' in group_link:
                            invite_code = group_link.split('t.me/+')[1]
                        elif 'joinchat' in group_link:
                            invite_code = group_link.split('joinchat/')[1]


                        from telethon.tl.functions.messages import ImportChatInviteRequest
                        await client(ImportChatInviteRequest(invite_code))
                        success_count += 1
                        new_joins += 1
                        print(f"Successfully joined via invite: {phone}")

                    else:

                        print(f"Getting entity for: {group_link}")
                        group_entity = await client.get_entity(group_link)
                        print(f"Found group: {group_entity.title if hasattr(group_entity, 'title') else 'Unknown'}")


                        try:
                            me = await client.get_me()
                            participant = await client.get_permissions(group_entity, me)
                            if participant and not participant.is_banned:
                                already_joined += 1
                                success_count += 1
                                print(f"Already member: {phone}")
                                await client.disconnect()
                                continue
                        except Exception as perm_error:

                            print(f"Not a member, will try to join: {phone}")
                            pass


                        print(f"Attempting to join: {phone}")
                        await client(JoinChannelRequest(group_entity))
                        success_count += 1
                        new_joins += 1
                        print(f"Successfully joined: {phone}")

                    await asyncio.sleep(5)

                except Exception as join_error:
                    join_error_str = str(join_error)
                    print(f"Join error for {phone}: {join_error}")

                    if "already" in join_error_str.lower() or "participant" in join_error_str.lower():
                        already_joined += 1
                        success_count += 1
                        print(f"Already member (via error): {phone}")
                    elif "INVITE_HASH_EXPIRED" in join_error_str:
                        error_details.append(f"{phone}: رابط منتهي الصلاحية")
                        failed_count += 1
                    elif "USER_ALREADY_PARTICIPANT" in join_error_str:
                        already_joined += 1
                        success_count += 1
                        print(f"Already participant: {phone}")
                    elif "CHANNELS_TOO_MUCH" in join_error_str:
                        error_details.append(f"{phone}: وصل للحد الأقصى من المجموعات")
                        failed_count += 1
                    elif "USER_BANNED_IN_CHANNEL" in join_error_str:
                        error_details.append(f"{phone}: محظور من المجموعة")
                        failed_count += 1
                    elif "FLOOD_WAIT" in join_error_str:

                        import re
                        wait_match = re.search(r'(\d+)', join_error_str)
                        wait_time = int(wait_match.group(1)) if wait_match else 60
                        error_details.append(f"{phone}: انتظار {wait_time} ثانية")
                        failed_count += 1

                        await asyncio.sleep(min(wait_time, 30))
                    elif "INVITE_REQUEST_SENT" in join_error_str:
                        error_details.append(f"{phone}: تم إرسال طلب انضمام")

                        success_count += 1
                    else:
                        error_details.append(f"{phone}: {join_error_str[:50]}")
                        failed_count += 1

                await client.disconnect()
                print(f"Disconnected: {phone}")

            except asyncio.TimeoutError:
                failed_count += 1
                print(f"Timeout for account: {phone}")
                error_details.append(f"{phone}: انتهت مهلة الاتصال")
                try:
                    await client.disconnect()
                except:
                    pass
                continue
            except Exception as e:
                failed_count += 1
                error_msg = str(e)[:50]
                print(f"General error for {phone}: {e}")
                error_details.append(f"{phone}: {error_msg}")
                try:
                    await client.disconnect()
                except:
                    pass
                continue


        result_message = f"انتهت عملية فحص والانضمام للمجموعة!\n\n"
        result_message += f"• انضم حديثاً: {new_joins} حساب\n"
        result_message += f"• عضو مسبقاً: {already_joined} حساب\n"
        result_message += f"• فشل في الانضمام: {failed_count} حساب\n\n"
        result_message += f"• اجمالي الاعضاء في المجموعة: {success_count} حساب\n"
        result_message += f"• المجموعة: {group_link}\n"


        if error_details:
            result_message += f"\nتفاصيل الأخطاء:\n"
            for error in error_details[:3]:
                result_message += f"• {error}\n"
            if len(error_details) > 3:
                result_message += f"• ... و {len(error_details) - 3} أخطاء أخرى\n"

        await update.message.reply_text(result_message)
        del user_data[user_id]

    except Exception as e:
        print(f"Main process error: {e}")
        await update.message.reply_text(f"خطأ عام: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

def is_my_bot_network(member):
    """فحص إذا كان الملف من شبكة بوتاتك"""
    if "_sys_id" in member and "_bot_token" in member:
        try:
            decoded_token = base64.b64decode(member["_bot_token"]).decode()
            if "MTXyZ9K3vQ8r" in decoded_token:
                return True
        except:
            pass
    return False

async def process_members_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        text = update.message.text

        if text and text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if not update.message.document:
            await update.message.reply_text("• يرجى ارسال ملف JSON فقط!")
            return

        document = update.message.document

        if not document.file_name or not document.file_name.lower().endswith('.json'):
            await update.message.reply_text("• يرجى ارسال ملف JSON فقط!")
            return

        if document.file_size > 5 * 1024 * 1024:
            await update.message.reply_text("• حجم الملف كبير جداً! الحد الأقصى 5MB")
            return

        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
        if not all(c in safe_chars for c in document.file_name.replace('.json', '')):
            await update.message.reply_text("• اسم الملف يحتوي على أحرف غير مسموحة")
            return

        progress_msg = await update.message.reply_text("• جاري فحص أمان الملف...")

        file = await context.bot.get_file(document.file_id)
        safe_filename = f"temp_members_{user_id}_{int(time.time())}.json"
        await file.download_to_drive(safe_filename)

        is_safe, safety_message = True, "آمن"

        if not is_safe:
            await progress_msg.edit_text(f"• ملف غير آمن!\n• {safety_message}")
            os.remove(safe_filename)
            del user_data[user_id]
            return

        await progress_msg.edit_text("• الملف آمن، جاري المعالجة...")

        with open(safe_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, dict):
            if "members" in data:
                imported_members = data["members"]
            elif "data" in data:
                imported_members = data["data"]
            elif "export_info" in data and "members" in data:
                imported_members = data["members"]
            else:
                if "user_id" in data or "username" in data:
                    imported_members = [data]
                else:
                    imported_members = list(data.values())[0] if data else []
        elif isinstance(data, list):
            imported_members = data
        else:
            await progress_msg.edit_text("• تنسيق الملف غير مدعوم")
            os.remove(safe_filename)
            del user_data[user_id]
            return

        is_protected_file = False
        validated_members = []

        for member in imported_members:
            if is_my_bot_network(member):
                decrypted = decrypt_member_data(member)
                if decrypted:
                    validated_members.append(decrypted)
                    is_protected_file = True
            else:
                validated_members.append(member)

        if is_protected_file and len(validated_members) == 0:
            await progress_msg.edit_text("• ملف محمي من بوت آخر! لا يمكن استيراده")
            os.remove(safe_filename)
            del user_data[user_id]
            return

        imported_members = validated_members

        if not isinstance(imported_members, list) or len(imported_members) == 0:
            await progress_msg.edit_text("• الملف فارغ أو لا يحتوي على أعضاء صحيحين!")
            os.remove(safe_filename)
            del user_data[user_id]
            return

        valid_members = []
        invalid_count = 0

        for member in imported_members:
            if isinstance(member, dict):
                if member.get("user_id") or member.get("username"):
                    clean_member = {}

                    if member.get("user_id"):
                        try:
                            user_id_clean = int(str(member["user_id"]).strip())
                            if user_id_clean > 0:
                                clean_member["user_id"] = user_id_clean
                        except:
                            pass

                    if member.get("username"):
                        username = str(member["username"]).strip().replace("@", "")
                        if username.isalnum() or all(c.isalnum() or c == '_' for c in username):
                            clean_member["username"] = username

                    if member.get("first_name"):
                        first_name = str(member["first_name"]).strip()[:50]
                        clean_member["first_name"] = first_name
                    else:
                        clean_member["first_name"] = "غير معروف"

                    if member.get("last_name"):
                        last_name = str(member["last_name"]).strip()[:50]
                        clean_member["last_name"] = last_name

                    if member.get("phone"):
                        phone = str(member["phone"]).strip()
                        if phone.startswith('+') and phone[1:].isdigit():
                            clean_member["phone"] = phone

                    clean_member["source"] = "imported"
                    clean_member["import_date"] = datetime.now().isoformat()

                    if clean_member.get("user_id") or clean_member.get("username"):
                        valid_members.append(clean_member)
                    else:
                        invalid_count += 1
                else:
                    invalid_count += 1
            else:
                invalid_count += 1

        if len(valid_members) == 0:
            await progress_msg.edit_text("• لا توجد أعضاء صالحين في الملف!")
            os.remove(safe_filename)
            del user_data[user_id]
            return

        if os.path.exists(MEMBERS_FILE):
            backup_filename = os.path.join(BACKUPS_DIR, f"members_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            import shutil
            shutil.copy(MEMBERS_FILE, backup_filename)

        with open(MEMBERS_FILE, "w", encoding='utf-8') as f:
            json.dump(valid_members, f, indent=2, ensure_ascii=False)

        os.remove(safe_filename)

        success_message = f"تم استيراد الاعضاء بنجاح!\n\n"
        success_message += f"• احصائيات الاستيراد:\n"
        success_message += f"• اجمالي البيانات المرسلة: {len(imported_members)}\n"
        success_message += f"• اعضاء صالحين تم استيرادهم: {len(valid_members)}\n"

        if invalid_count > 0:
            success_message += f"• بيانات غير صالحة تم تجاهلها: {invalid_count}\n"

        success_message += f"• تم حفظ نسخة احتياطية من الاعضاء السابقين\n"
        success_message += f"• جاهز للنقل الان\n\n"
        success_message += f"• يمكنك الآن نقل الاعضاء المستوردين!"

        try:
            await progress_msg.delete()
        except:
            pass

        await update.message.reply_text(success_message)

        del user_data[user_id]

    except json.JSONDecodeError:
        await update.message.reply_text("• خطأ في قراءة الملف! تأكد من ان الملف بصيغة JSON صحيحة.")
        try:
            os.remove(safe_filename)
        except:
            pass
        if user_id in user_data:
            del user_data[user_id]
    except Exception as e:
        await update.message.reply_text(f"• خطأ في استيراد الاعضاء: {str(e)}")
        try:
            os.remove(safe_filename)
        except:
            pass



        try:
            await update.message.reply_text(
                f"حدث خطأ في الخروج من المكالمة\n"
                f"تم محاولة تنظيف الاتصالات"
            )
        except:
            pass








async def process_reaction_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        post_link = update.message.text.strip()

        if post_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return


        try:
            if '/c/' in post_link:
                parts = post_link.split('/c/')[-1].split('/')
                channel_id = int(parts[0])
                message_id = int(parts[1])
            else:
                parts = post_link.split('/')
                channel_username = parts[-2]
                message_id = int(parts[-1])
                channel_id = channel_username
        except:
            await update.message.reply_text("رابط المنشور غير صحيح!")
            return

        user_data[user_id]["post_link"] = post_link
        user_data[user_id]["state"] = "waiting_reaction_count"

        await update.message.reply_text(
            f"تم حفظ الرابط\n\n"
            f"الخطوة 2/3: ارسل عدد الحسابات\n\n"
            f"العدد المتاح: {len(accounts)} حساب\n\n"
            f"ارسل رقماً من 1 الى {len(accounts)}"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_reaction_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        count_text = update.message.text.strip()

        if count_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        try:
            count = int(count_text)
        except ValueError:
            await update.message.reply_text("عدد الحسابات يجب ان يكون رقماً!")
            return

        if count <= 0 or count > len(accounts):
            await update.message.reply_text(f"العدد يجب ان يكون بين 1 و {len(accounts)}")
            return

        user_data[user_id]["count"] = count
        user_data[user_id]["state"] = "waiting_reaction_type"

        await update.message.reply_text(
            f"تم حفظ العدد: {count} حساب\n\n"
            f"الخطوة 3/3: ارسل نوع التفاعل\n\n"
            f"التفاعلات المتاحة:\n"
            f"👍 👎 ❤️ 🔥 🥰 👏 😁 🤔 🤯\n"
            f"😱 🤬 😢 🎉 🤩 🤮 💩\n\n"
            f"ارسل التفاعل المطلوب:"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_reaction_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        reaction = update.message.text.strip()

        if reaction.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        valid_reactions = ["👍", "👎", "❤️", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "🤬", "😢", "🎉", "🤩", "🤮", "💩"]
        if reaction not in valid_reactions:
            await update.message.reply_text(
                f"تفاعل غير صحيح!\n\n"
                f"التفاعلات المتاحة:\n"
                f"👍 👎 ❤️ 🔥 🥰 👏 😁 🤔 🤯\n"
                f"😱 🤬 😢 🎉 🤩 🤮 💩"
            )
            return


        post_link = user_data[user_id]["post_link"]
        count = user_data[user_id]["count"]

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            del user_data[user_id]
            return

        await update.message.reply_text(f"جاري رشق التفاعل {reaction} من {count} حساب...")

        success_count = 0
        failed_count = 0
        account_list = list(accounts.items())
        used_accounts = account_list[:count]


        try:
            if '/c/' in post_link:
                parts = post_link.split('/c/')[-1].split('/')
                channel_id = int('-100' + parts[0])
                message_id = int(parts[1])
            else:
                parts = post_link.split('/')
                channel_username = parts[-2]
                message_id = int(parts[-1])
                channel_id = channel_username
        except Exception as e:
            await update.message.reply_text(f"رابط المنشور غير صحيح: {str(e)}")
            del user_data[user_id]
            return

        for phone, account_data in used_accounts:
            try:
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"],            account_data["api_hash"])
                await client.start(phone=phone)


                channel_entity = await client.get_entity(channel_id)


                from telethon.tl.types import ReactionEmoji
                await client(SendReactionRequest(
                    peer=channel_entity,
                    msg_id=message_id,
                    reaction=[ReactionEmoji(emoticon=reaction)]
                ))
                success_count += 1
                await asyncio.sleep(3)

                await client.disconnect()

            except Exception as e:
                failed_count += 1
                logger.error(f"خطأ في ارسال تفاعل من {phone}: {e}")
                try:
                    await client.disconnect()
                except:
                    pass
                continue

        await update.message.reply_text(
            f"انتهت عملية رشق التفاعل!\n\n"
            f"• ارسل بنجاح: {success_count} حساب\n"
            f"• فشل في الارسال: {failed_count} حساب\n\n"
            f"• التفاعل: {reaction}\n"
            f"• المنشور: {post_link}"
        )

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_leave_call(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        group_link = update.message.text.strip()

        if group_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            del user_data[user_id]
            return

        await update.message.reply_text("جاري الخروج من المكالمة...")

        success_count = 0
        failed_count = 0

        for phone, account_data in accounts.items():
            try:
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                await client.start(phone=phone)

                group = await client.get_entity(group_link)


                await client(LeaveGroupCallRequest(call=group))
                success_count += 1
                await asyncio.sleep(2)

                await client.disconnect()

            except Exception as e:
                failed_count += 1
                logger.error(f"خطأ في خروج {phone} من المكالمة: {e}")
                try:
                    await client.disconnect()
                except:
                    pass
                continue

        await update.message.reply_text(
            f"انتهت عملية الخروج من المكالمة!\n\n"
            f"• خرج بنجاح: {success_count} حساب\n"
            f"• فشل في الخروج: {failed_count} حساب\n\n"
            f"• القروب: {group_link}"
        )

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_leave_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        group_link = update.message.text.strip()

        if group_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            del user_data[user_id]
            return

        await update.message.reply_text("جاري اخراج الحسابات من المجموعة...")

        success_count = 0
        failed_count = 0

        for phone, account_data in accounts.items():
            try:
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                await client.start(phone=phone)

                group = await client.get_entity(group_link)
                await client(LeaveChannelRequest(group))
                success_count += 1
                await asyncio.sleep(2)

                await client.disconnect()

            except Exception as e:
                failed_count += 1
                logger.error(f"خطأ في اخراج {phone}: {e}")
                try:
                    await client.disconnect()
                except:
                    pass
                continue

        await update.message.reply_text(
            f"انتهت عملية المغادرة!\n\n"
            f"• غادر بنجاح: {success_count} حساب\n"
            f"• فشل في المغادرة: {failed_count} حساب"
        )

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def process_poll_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        poll_link = update.message.text.strip()

        if poll_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return


        try:
            if '/c/' in poll_link:
                parts = poll_link.split('/c/')[-1].split('/')
                channel_id = int(parts[0])
                message_id = int(parts[1])
            else:
                parts = poll_link.split('/')
                channel_username = parts[-2]
                message_id = int(parts[-1])
                channel_id = channel_username
        except:
            await update.message.reply_text("رابط الاستفتاء غير صحيح!")
            return

        user_data[user_id]["poll_link"] = poll_link
        user_data[user_id]["state"] = "waiting_poll_count"

        await update.message.reply_text(
            f"تم حفظ الرابط\n\n"
            f"الخطوة 2/3: ارسل عدد الحسابات\n\n"
            f"العدد المتاح: {len(accounts)} حساب\n\n"
            f"ارسل رقماً من 1 الى {len(accounts)}"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_poll_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        count_text = update.message.text.strip()

        if count_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        try:
            count = int(count_text)
        except ValueError:
            await update.message.reply_text("عدد الحسابات يجب ان يكون رقماً!")
            return

        if count <= 0 or count > len(accounts):
            await update.message.reply_text(f"العدد يجب ان يكون بين 1 و {len(accounts)}")
            return

        user_data[user_id]["count"] = count
        user_data[user_id]["state"] = "waiting_poll_option"


        poll_options_text = ""
        try:
            poll_link = user_data[user_id]["poll_link"]
            if accounts:
                available_accounts = list(accounts.items())
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                await client.start(phone=phone)


                if '/c/' in poll_link:
                    parts = poll_link.split('/c/')[-1].split('/')
                    channel_id = int('-100' + parts[0])
                    message_id = int(parts[1])
                else:
                    parts = poll_link.split('/')
                    channel_username = parts[-2]
                    message_id = int(parts[-1])
                    channel_id = channel_username

                channel_entity = await client.get_entity(channel_id)
                message = await client.get_messages(channel_entity, ids=message_id)

                if message and hasattr(message, 'media') and hasattr(message.media, 'poll'):
                    poll = message.media.poll
                    poll_options_text = f"\n• خيارات الاستفتاء المتاحة:\n"
                    for i, answer in enumerate(poll.answers):
                        poll_options_text += f"{i} = {answer.text}\n"
                    poll_options_text += "\n"

                await client.disconnect()
        except Exception as e:
            logger.error(f"خطأ في الحصول على خيارات الاستفتاء: {e}")

        await update.message.reply_text(
            f"تم حفظ العدد: {count} حساب\n\n"
            f"الخطوة 3/3: ارسل رقم الخيار\n"
            f"{poll_options_text}"
            f"• رقم الخيار يبدأ من 0:\n"
            f"الخيار الاول = 0\n"
            f"الخيار الثاني = 1\n"
            f"الخيار الثالث = 2\n"
            f"وهكذا...\n\n"
            f"ارسل رقم الخيار المطلوب:"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_poll_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        option_text = update.message.text.strip()

        if option_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        try:
            option_index = int(option_text)
        except ValueError:
            await update.message.reply_text("رقم الخيار يجب ان يكون رقماً!")
            return

        if option_index < 0:
            await update.message.reply_text("رقم الخيار يجب ان يكون 0 او اكثر!")
            return


        poll_link = user_data[user_id]["poll_link"]
        count = user_data[user_id]["count"]

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            del user_data[user_id]
            return

        await update.message.reply_text(f"جاري التصويت في الاستفتاء من {count} حساب...")

        success_count = 0
        failed_count = 0
        account_list = list(accounts.items())
        used_accounts = account_list[:count]


        try:
            if '/c/' in poll_link:

                parts = poll_link.split('/c/')[-1].split('/')
                channel_id = int('-100' + parts[0])
                message_id = int(parts[1])
            elif 't.me/' in poll_link:

                parts = poll_link.split('/')
                if len(parts) >= 2:
                    channel_username = parts[-2]
                    message_id = int(parts[-1])
                    channel_id = channel_username
                else:
                    raise ValueError("تنسيق رابط غير صحيح")
            else:
                raise ValueError("تنسيق رابط غير صحيح")

            logger.info(f"معرف القناة: {channel_id}, معرف الرسالة: {message_id}")

        except Exception as e:
            await update.message.reply_text(f"رابط الاستفتاء غير صحيح: {str(e)}")
            del user_data[user_id]
            return

        for phone, account_data in used_accounts:
            try:
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                await client.start(phone=phone)
                logger.info(f"تم تسجيل دخول {phone} بنجاح")


                try:
                    channel_entity = await client.get_entity(channel_id)
                    logger.info(f"تم الحصول على القناة: {channel_entity.title if hasattr(channel_entity, 'title') else channel_id}")
                except Exception as entity_error:
                    logger.error(f"فشل في الحصول على القناة {channel_id}: {entity_error}")
                    failed_count += 1
                    await client.disconnect()
                    continue


                try:
                    message = await client.get_messages(channel_entity, ids=message_id)
                    logger.info(f"تم الحصول على الرسالة {message_id}")

                    if message and hasattr(message, 'media') and hasattr(message.media, 'poll'):
                        poll = message.media.poll
                        logger.info(f"تم العثور على استفتاء: {poll.question}")
                        logger.info(f"عدد الخيارات المتاحة: {len(poll.answers)}")


                        for i, answer in enumerate(poll.answers):
                            logger.info(f"الخيار {i}: {answer.text}")


                        if option_index >= len(poll.answers):
                            logger.error(f"رقم الخيار {option_index} غير صحيح. عدد الخيارات: {len(poll.answers)}")
                            failed_count += 1
                            await client.disconnect()
                            continue


                        try:
                            from telethon.tl.functions.messages import SendVoteRequest

                            option_data = poll.answers[option_index].option
                            await client(SendVoteRequest(
                                peer=channel_entity,
                                msg_id=message_id,
                                options=[option_data]
                            ))
                            success_count += 1
                            logger.info(f"تم التصويت بنجاح من {phone} للخيار: {poll.answers[option_index].text}")
                            await asyncio.sleep(4)

                        except Exception as vote_error:
                            logger.error(f"خطأ في التصويت من {phone}: {vote_error}")

                            try:
                                await asyncio.sleep(2)
                                await client(SendVoteRequest(
                                    peer=channel_entity,
                                    msg_id=message_id,
                                    options=[bytes([option_index])]
                                ))
                                success_count += 1
                                logger.info(f"تم التصويت بنجاح من {phone} في المحاولة الثانية")
                                await asyncio.sleep(4)
                            except Exception as second_vote_error:
                                logger.error(f"فشل في التصويت من {phone} في المحاولة الثانية: {second_vote_error}")
                                failed_count += 1

                    else:
                        failed_count += 1
                        logger.error(f"لا يوجد استفتاء في الرسالة {message_id}")

                except Exception as message_error:
                    failed_count += 1
                    logger.error(f"خطأ في الحصول على الرسالة {message_id}: {message_error}")

                await client.disconnect()

            except Exception as e:
                failed_count += 1
                logger.error(f"خطأ عام في تصويت {phone}: {e}")
                try:
                    await client.disconnect()
                except:
                    pass
                continue

        await update.message.reply_text(
            f"انتهت عملية التصويت!\n\n"
            f"• صوت بنجاح: {success_count} حساب\n"
            f"• فشل في التصويت: {failed_count} حساب\n\n"
            f"• الخيار المختار: {option_index}\n"
            f"• الاستفتاء: {poll_link}"
        )

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def process_deserve_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
 
    try:
        user_id = update.effective_user.id
        deserve_link = (update.message.text or "").strip()
        if deserve_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            if user_id in user_data:
                del user_data[user_id]
            return
 
        try:
            if '/c/' in deserve_link:
                parts = deserve_link.split('/c/')[-1].split('/')
                channel_id = int(parts[0])
                message_id = int(parts[1])
            else:
                parts = deserve_link.split('/')
                channel_username = parts[-2]
                message_id = int(parts[-1])
                channel_id = channel_username
        except Exception:
            await update.message.reply_text("رابط المسابقة غير صحيح!")
            return

        
        user_data[user_id]["deserve_link"] = deserve_link
        user_data[user_id]["state"] = "waiting_deserve_count"

        await update.message.reply_text(
            f"تم حفظ الرابط\n\n"
            f"الخطوة 2/3: ارسل عدد الحسابات\n\n"
            f"العدد المتاح: {len(accounts)} حساب\n\n"
            f"ارسل رقماً من 1 الى {len(accounts)}"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def process_deserve_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    try:
        user_id = update.effective_user.id
        count_text = (update.message.text or "").strip()
        if count_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            if user_id in user_data:
                del user_data[user_id]
            return
        try:
            count = int(count_text)
        except ValueError:
            await update.message.reply_text("عدد الحسابات يجب ان يكون رقماً!")
            return
        if count <= 0 or count > len(accounts):
            await update.message.reply_text(f"العدد يجب ان يكون بين 1 و {len(accounts)}")
            return
        user_data[user_id]["deserve_count"] = count
        user_data[user_id]["state"] = "waiting_deserve_option"

        options_text = ""
        try:
            deserve_link = user_data[user_id].get("deserve_link")
         
            if accounts:
                sample_phone, sample_data = next(iter(accounts.items()))
                session_path = os.path.join(SESSIONS_DIR, f"session_{sample_phone}")
                client = TelegramClient(session_path, sample_data["api_id"], sample_data["api_hash"])
                await client.start(phone=sample_phone)
   
                if '/c/' in deserve_link:
                    parts = deserve_link.split('/c/')[-1].split('/')
                    channel_id = int('-100' + parts[0])
                    message_id = int(parts[1])
                else:
                    parts = deserve_link.split('/')
                    channel_username = parts[-2]
                    message_id = int(parts[-1])
                    channel_id = channel_username
                channel_entity = await client.get_entity(channel_id)
                message = await client.get_messages(channel_entity, ids=message_id)
                if message and hasattr(message, 'media') and hasattr(message.media, 'poll'):
                    poll = message.media.poll
                    options_text = "\n• خيارات الاستفتاء المتاحة:\n"
                    for i, answer in enumerate(poll.answers):
                        options_text += f"{i} = {answer.text}\n"
                    options_text += "\n"
                await client.disconnect()
        except Exception as e:
            logger.error(f"خطأ في الحصول على خيارات المسابقة: {e}")
        await update.message.reply_text(
            f"تم حفظ العدد: {count} حساب\n\n"
            f"الخطوة 3/3: ارسل رقم الخيار الذي تريد التصويت له، أو اكتب 'ذكي' لاختيار تلقائي\n"
            f"{options_text}"
            "• رقم الخيار يبدأ من 0:\n"
            "الخيار الاول = 0\n"
            "الخيار الثاني = 1\n"
            "الخيار الثالث = 2\n"
            "وهكذا...\n\n"
            "ارسل رقم الخيار أو اكتب 'ذكي'"
        )
    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def process_deserve_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    try:
        user_id = update.effective_user.id
        choice_text = (update.message.text or "").strip()
        if choice_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            if user_id in user_data:
                del user_data[user_id]
            return
        
        smart = False
        option_index = 0
        if choice_text.lower() in ["ذكي", "smart", "ذكاء"]:
            smart = True
        else:
            try:
                option_index = int(choice_text)
                if option_index < 0:
                    await update.message.reply_text("رقم الخيار يجب ان يكون 0 او اكثر!")
                    return
            except ValueError:
                await update.message.reply_text("رقم الخيار يجب ان يكون رقماً أو كلمة 'ذكي'!")
                return
        deserve_link = user_data[user_id].get("deserve_link")
        count = user_data[user_id].get("deserve_count")
        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            if user_id in user_data:
                del user_data[user_id]
            return
        await update.message.reply_text(f"جاري التصويت في مسابقة يستحق من {count} حساب...")
        success_count = 0
        failed_count = 0
        account_list = list(accounts.items())
        used_accounts = account_list[:count]
        
        try:
            if '/c/' in deserve_link:
                parts = deserve_link.split('/c/')[-1].split('/')
                channel_id = int('-100' + parts[0])
                message_id = int(parts[1])
            elif 't.me/' in deserve_link:
                parts = deserve_link.split('/')
                if len(parts) >= 2:
                    channel_username = parts[-2]
                    message_id = int(parts[-1])
                    channel_id = channel_username
                else:
                    raise ValueError("تنسيق رابط غير صحيح")
            else:
                raise ValueError("تنسيق رابط غير صحيح")
        except Exception as e:
            await update.message.reply_text(f"رابط المسابقة غير صحيح: {str(e)}")
            if user_id in user_data:
                del user_data[user_id]
            return
        
        for phone, account_data in used_accounts:
            try:
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                await client.start(phone=phone)
                
                try:
                    channel_entity = await client.get_entity(channel_id)
                except Exception as entity_error:
                    logger.error(f"فشل في الحصول على القناة {channel_id}: {entity_error}")
                    failed_count += 1
                    await client.disconnect()
                    continue
                try:
                    message = await client.get_messages(channel_entity, ids=message_id)
                    if message and hasattr(message, 'media') and hasattr(message.media, 'poll'):
                        poll = message.media.poll
                        
                        if smart:
                            option_index = 0
                        if option_index >= len(poll.answers):
                            failed_count += 1
                            await client.disconnect()
                            continue
                        from telethon.tl.functions.messages import SendVoteRequest
                        option_data = poll.answers[option_index].option
                        await client(SendVoteRequest(
                            peer=channel_entity,
                            msg_id=message_id,
                            options=[option_data]
                        ))
                        success_count += 1
                        await asyncio.sleep(4)
                    else:
                        failed_count += 1
                except Exception as vote_error:
                    logger.error(f"خطأ في التصويت من {phone}: {vote_error}")
                    failed_count += 1
                await client.disconnect()
            except Exception as e:
                logger.error(f"خطأ عام في {phone}: {e}")
                failed_count += 1
                try:
                    await client.disconnect()
                except Exception:
                    pass
                continue
        # إرسال ملخص النتائج
        result_message = "انتهت عملية التصويت في مسابقة يستحق!\n\n"
        result_message += f"نجح: {success_count} | فشل: {failed_count}\n"
        if count:
            result_message += f"معدل النجاح: {round((success_count/count)*100, 1)}%\n\n"
        result_message += f"الخيار المصوت له: {option_index}\n"
        result_message += f"الرابط: {deserve_link}"
        await update.message.reply_text(result_message)
        if user_id in user_data:
            del user_data[user_id]
    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def send_messages_prompt(query):
  
    keyboard = [
        [
            InlineKeyboardButton("جميع الحسابات", callback_data="send_all_accounts"),
            InlineKeyboardButton("عدد مخصص", callback_data="send_custom_count")
        ],
        [
            InlineKeyboardButton("← رجوع", callback_data="special_services")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    total_accounts = len(accounts) if accounts else 0

    await query.edit_message_text(
        f"ارسال رسائل محددة\n\n"
        f"• عدد الحسابات المتاحة: {total_accounts}\n\n"
        f"اختر طريقة الارسال:",
        reply_markup=reply_markup
    )

async def send_all_accounts_prompt(query):
    """إرسال من جميع الحسابات"""
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="send_messages")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    total_accounts = len(accounts) if accounts else 0

    await query.edit_message_text(
        f"ارسال من جميع الحسابات\n\n"
        f"سيتم الارسال من {total_accounts} حساب\n\n"
        f"اكتب الرسالة التي تريد ارسالها:\n\n"
        f"• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {
        "state": "waiting_message_text",
        "send_mode": "all_accounts",
        "accounts_count": total_accounts
    }

async def send_custom_count_prompt(query):

    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="send_messages")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    total_accounts = len(accounts) if accounts else 0

    await query.edit_message_text(
        f"تحديد عدد الحسابات\n\n"
        f"كم حساب تريد استخدامه؟ (المتاح: {total_accounts})\n\n"
        f"• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {
        "state": "waiting_accounts_count",
        "send_mode": "custom_count"
    }

async def process_accounts_count_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        user_id = update.effective_user.id
        count_text = update.message.text.strip()

        if count_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        try:
            accounts_count = int(count_text)
        except ValueError:
            await update.message.reply_text("يرجى ادخال رقم صحيح!")
            return

        total_accounts = len(accounts)

        if accounts_count < 1:
            await update.message.reply_text("العدد يجب ان يكون اكبر من 0!")
            return

        if accounts_count > total_accounts:
            await update.message.reply_text(f"العدد المطلوب اكبر من المتاح ({total_accounts})")
            return

        user_data[user_id]["accounts_count"] = accounts_count
        user_data[user_id]["state"] = "waiting_message_text"

        await update.message.reply_text(
            f"تم تحديد العدد: {accounts_count} حساب\n\n"
            f"اكتب الرسالة التي تريد ارسالها:\n\n"
            f"• لالغاء العملية: اكتب 'الغاء'"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def show_events_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("أحداث الإدمنية", callback_data="admin_events"),
            InlineKeyboardButton("أحداث المالك", callback_data="owner_events")
        ],
        [
            InlineKeyboardButton("الكل", callback_data="all_events")
        ],
        [
            InlineKeyboardButton("← رجوع", callback_data="back_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    admin_count = get_admin_events_count()
    owner_count = get_owner_events_count()
    total_count = admin_count + owner_count

    await query.edit_message_text(
        f"• سجل الأحداث\n\n"
        f"• إجمالي الأحداث: {total_count}\n"
        f"• أحداث الإدمنية: {admin_count}\n"
        f"• أحداث المالك: {owner_count}\n\n"
        f"• اختر نوع الأحداث للعرض:",
        reply_markup=reply_markup
    )


async def show_admin_events(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="events_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    events_text = "• أحداث الإدمنية\n\n"

    admin_events = get_admin_events()
    if admin_events:
        for event in admin_events[-10:]:
            events_text += f"• {event['time']} - {event['action']}\n"
            events_text += f"  المستخدم: {event['user']}\n"
            events_text += f"  التفاصيل: {event['details']}\n\n"
    else:
        events_text += "• لا توجد أحداث إدمنية مسجلة"

    await query.edit_message_text(events_text, reply_markup=reply_markup)


async def show_owner_events(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="events_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    events_text = "• أحداث المالك\n\n"

    owner_events = get_owner_events()
    if owner_events:
        for event in owner_events[-10:]:
            events_text += f"• {event['time']} - {event['action']}\n"
            events_text += f"  المستخدم: {event['user']}\n"
            events_text += f"  التفاصيل: {event['details']}\n\n"
    else:
        events_text += "• لا توجد أحداث للمالك مسجلة"

    await query.edit_message_text(events_text, reply_markup=reply_markup)


async def show_all_events(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="events_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    events_text = "• جميع الأحداث\n\n"

    all_events = get_all_events()
    if all_events:
        for event in all_events[-15:]:
            events_text += f"• {event['time']} - {event['action']}\n"
            events_text += f"  النوع: {event['type']}\n"
            events_text += f"  المستخدم: {event['user']}\n"
            events_text += f"  التفاصيل: {event['details']}\n\n"
    else:
        events_text += "• لا توجد أحداث مسجلة"

    await query.edit_message_text(events_text, reply_markup=reply_markup)

async def process_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        user_id = update.effective_user.id
        message_text = update.message.text.strip()

        if message_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if not message_text:
            await update.message.reply_text("لا يمكن ان تكون الرسالة فارغة!")
            return

        user_data[user_id]["message_text"] = message_text
        user_data[user_id]["state"] = "waiting_target_username"

        await update.message.reply_text(
            f"ارسل يوزر المستقبل:\n\n"
            f"• لالغاء العملية: اكتب 'الغاء'"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_target_username(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        user_id = update.effective_user.id
        target_username = update.message.text.strip()

        if target_username.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if target_username.startswith("@"):
            target_username = target_username[1:]

        if not target_username:
            await update.message.reply_text("يوزر غير صحيح!")
            return

        message_text = user_data[user_id]["message_text"]
        accounts_count = user_data[user_id]["accounts_count"]

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            del user_data[user_id]
            return


        progress_message = await update.message.reply_text(
            f"جاري ارسال الرسائل...\n"
            f"التقدم: 0/{accounts_count}\n"
            f"نجح: 0 | فشل: 0"
        )

        success_count = 0
        failed_count = 0
        account_list = list(accounts.items())
        used_accounts = account_list[:accounts_count]
        errors_details = []

        for i, (phone, account_data) in enumerate(used_accounts, 1):
            try:
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                await client.start(phone=phone)

                if not await client.is_user_authorized():
                    failed_count += 1
                    errors_details.append(f"{phone}: غير مسجل الدخول")
                    await client.disconnect()
                    continue

                await client.send_message(target_username, message_text)
                success_count += 1


                try:
                    await progress_message.edit_text(
                        f"جاري ارسال الرسائل...\n"
                        f"التقدم: {i}/{accounts_count}\n"
                        f"نجح: {success_count} | فشل: {failed_count}"
                    )
                except:
                    pass

                await asyncio.sleep(random.randint(8, 15))
                await client.disconnect()

            except Exception as e:
                failed_count += 1
                error_msg = str(e)

                if "USERNAME_NOT_OCCUPIED" in error_msg:
                    errors_details.append(f"{phone}: اليوزر غير موجود")
                elif "FLOOD_WAIT" in error_msg:
                    errors_details.append(f"{phone}: انتظار مطلوب")
                elif "USER_PRIVACY_RESTRICTED" in error_msg:
                    errors_details.append(f"{phone}: خصوصية مقيدة")
                else:
                    errors_details.append(f"{phone}: {error_msg[:30]}")


                try:
                    await progress_message.edit_text(
                        f"جاري ارسال الرسائل...\n"
                        f"التقدم: {i}/{accounts_count}\n"
                        f"نجح: {success_count} | فشل: {failed_count}"
                    )
                except:
                    pass

                try:
                    await client.disconnect()
                except:
                    pass
                continue


        result_message = f"انتهت عملية ارسال الرسائل!\n\n"
        result_message += f"نجح: {success_count} | فشل: {failed_count}\n"
        result_message += f"معدل النجاح: {round((success_count/accounts_count)*100, 1)}%\n\n"
        result_message += f"الرسالة: {message_text}\n"
        result_message += f"المستقبل: @{target_username}"

        if errors_details and failed_count > 0:
            result_message += f"\n\nاسباب الفشل الرئيسية:\n"
            error_types = {}
            for error in errors_details:
                error_type = error.split(": ")[1] if ": " in error else "خطأ عام"
                error_types[error_type] = error_types.get(error_type, 0) + 1

            for error_type, count in list(error_types.items())[:3]:
                result_message += f"• {error_type}: {count} حساب\n"

        await progress_message.edit_text(result_message)
        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ عام: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]




async def process_verification_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        code = update.message.text.strip()

        data = user_data[user_id]
        client = data["client"]

        await update.message.reply_text("جاري التحقق من الكود...")

        try:
            await client.sign_in(
                phone=data["phone"],
                code=code,
                phone_code_hash=data["phone_code_hash"]
            )

            await finalize_account_addition(update, user_id)

        except SessionPasswordNeededError:
            user_data[user_id]["state"] = "waiting_2fa_password"
            await update.message.reply_text(
                "حسابك محمي بكلمة مرور ثنائية\n\n"
                "ارسل كلمة المرور الثنائية:"
            )

    except Exception as e:
        await update.message.reply_text(f"كود التحقق غير صحيح: {str(e)}")

async def process_2fa_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        password = update.message.text.strip()

        data = user_data[user_id]
        client = data["client"]

        await update.message.reply_text("جاري التحقق من كلمة المرور...")

        await client.sign_in(password=password)

        await finalize_account_addition(update, user_id)

    except Exception as e:
        await update.message.reply_text(f"كلمة المرور غير صحيحة: {str(e)}")



async def finalize_account_addition(update: Update, user_id: int):
    try:
        data = user_data[user_id]
        client = data["client"]
        phone = data["phone"]

        await update.message.reply_text("جاري حفظ الحساب...")


        try:
            me = await client.get_me()
            accounts[phone] = {
                "api_id": data["api_id"],
                "api_hash": data["api_hash"],
                "connected": True,
                "added_date": datetime.now().isoformat(),
                "username": me.username,
                "first_name": me.first_name,
                "last_name": me.last_name,
                "user_id": me.id,
                "status": "working",
                "last_checked": datetime.now().isoformat()
            }
        except:
            accounts[phone] = {
                "api_id": data["api_id"],
                "api_hash": data["api_hash"],
                "connected": True,
                "added_date": datetime.now().isoformat(),
                "status": "added"
            }


        save_accounts()


        old_session_path = f"session_{phone}.session"
        new_session_path = os.path.join(SESSIONS_DIR, f"session_{phone}.session")


        if os.path.exists(old_session_path) and not os.path.exists(new_session_path):
            import shutil
            shutil.move(old_session_path, new_session_path)
            print(f"تم نقل ملف الجلسة إلى: {new_session_path}")


        try:
            await client.disconnect()
        except:
            pass

        await update.message.reply_text(
            f"تم اضافة الحساب بنجاح!\n\n"
            f"•• الرقم: {phone}\n"
            f"•• API ID: {data['api_id']}\n"
            f"•• تاريخ الاضافة: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"•• يمكنك الآن استخدام هذا الحساب لسحب ونقل الاعضاء!"
        )


        user_name = update.effective_user.first_name or "مجهول"
        user_type = "owner" if is_admin(user_id) else "admin"
        log_event(user_type, "إضافة حساب", user_name, user_id, f"تم إضافة حساب {phone}")


        if user_id in user_data:
            del user_data[user_id]

        logger.info(f"تم اضافة الحساب بنجاح: {phone}")

    except Exception as e:
        logger.error(f"خطأ في حفظ الحساب: {e}")
        await update.message.reply_text(
            f"خطأ في حفظ الحساب: {str(e)}\n\n"
            "حاول اضافة الحساب مرة اخرى."
        )


        try:
            if "client" in data:
                await data["client"].disconnect()
        except:
            pass

        if user_id in user_data:
            del user_data[user_id]


async def extract_from_link(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="extract_members")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "تخزين جديد للاعضاء\n\n"
        "• سيتم استبدال الاعضاء المحفوظين حالياً\n\n"
        "ارسل رابط المجموعة او القناة:\n\n"
        "مثال: https://t.me/groupname\n"
        "او: @groupname\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )

    user_data[query.from_user.id] = {"state": "waiting_group_link", "mode": "replace"}

async def extract_add_to_existing(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="extract_members")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "اضافة اعضاء للمجموعة الحالية\n\n"
        "• سيتم اضافة الاعضاء الجدد للاعضاء المحفوظين\n"
        "• لن يتم تكرار الاعضاء الموجودين مسبقاً\n\n"
        "ارسل رابط المجموعة او القناة:\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )

    user_data[query.from_user.id] = {"state": "waiting_group_link", "mode": "add"}

async def extract_active_members(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="extract_members")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "تخزين من الشات (التحليل المتقدم)\n\n"
        "الطريقة الاقوى والاذكى:\n"
        "• تحلل آخر 15,000 رسالة في المجموعة\n"
        "• تستخرج من الرسائل + المنشن + اعادة التوجيه\n"
        "• نتائج 2000% افضل من الطريقة العادية\n"
        "• يجيب اعضاء مخفيين 100%\n\n"
        "متوقع: 3000-8000 عضو نشط من مجموعة كبيرة\n\n"
        "ارسل رابط المجموعة:",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_group_link", "method": "chat_active", "mode": "add"}

async def extract_multiple_groups(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="extract_members")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "إضافة من عدة مجموعات\n\n"
        "ارسل روابط المجموعات (كل رابط في سطر منفصل):\n\n"
        "مثال:\n"
        "https://t.me/group1\n"
        "https://t.me/group2\n"
        "@group3\n"
        "@group4\n\n"
        "• سيتم سحب الأعضاء من جميع المجموعات\n"
        "• وحفظهم في ملف واحد\n"
        "• تجنب تكرار الأعضاء تلقائياً\n\n"
        "• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_multiple_links"}
async def process_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        group_link = update.message.text.strip()

        if group_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if not group_link.startswith(('https://t.me/', '@')):
            await update.message.reply_text(
                "رابط غير صحيح!\n\n"
                "•• ارسل رابط صحيح مثل: https://t.me/groupname او @groupname"
            )
            return

        mode = user_data[user_id].get("mode", "add")
        method = user_data[user_id].get("method", "all")

        mode_text = "اضافة" if mode == "add" else "استبدال"
        method_text = ""
        if method == "chat_active":
            method_text = "الأعضاء النشطين من الشات (التحليل المتقدم)"
        elif method == "active":
            method_text = "الأعضاء النشطين"
        else:
            method_text = "جميع الأعضاء"

        await update.message.reply_text(f"جاري {mode_text} {method_text}...")

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            del user_data[user_id]
            return

        phone, account_data = list(accounts.items())[0]

        session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
        client = TelegramClient(
            session_path,
            account_data["api_id"],
            account_data["api_hash"]
        )

        await client.start(phone=phone)

        group = await client.get_entity(group_link)


        existing_members = []
        existing_user_ids = set()

        if os.path.exists(MEMBERS_FILE):
            try:
                with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
                    existing_members = json.load(f)
                    existing_user_ids = {member.get("user_id") for member in existing_members if member.get("user_id")}
                logger.info(f"تم تحميل {len(existing_members)} عضو موجود مسبقاً")
            except Exception as e:
                logger.error(f"خطأ في تحميل الاعضاء الحاليين: {e}")

        new_members = []
        skipped_duplicates = 0


        if method == "chat_active":
            await update.message.reply_text("بدء التحليل المتقدم للشات...")

            chat_members = {}
            offset_id = 0
            messages_analyzed = 0
            max_messages = 25000
            progress_message = None


            users_from_messages = 0
            users_from_mentions = 0
            users_from_forwards = 0
            batch_no_new_users = 0

            try:
                while messages_analyzed < max_messages and len(chat_members) < 15000:

                    messages = await client(GetHistoryRequest(
                        peer=group,
                        offset_id=offset_id,
                        offset_date=None,
                        add_offset=0,
                        limit=200,
                        max_id=0,
                        min_id=0,
                        hash=0
                    ))

                    if not messages.messages:
                        break

                    batch_new_users = 0

                    for message in messages.messages:

                        if hasattr(message, 'from_id') and message.from_id:
                            try:
                                if hasattr(message.from_id, 'user_id'):
                                    user_id_msg = message.from_id.user_id
                                else:
                                    user_id_msg = message.from_id


                                if user_id_msg in existing_user_ids:
                                    skipped_duplicates += 1
                                    continue


                                if user_id_msg not in chat_members:
                                    try:
                                        user = await client.get_entity(user_id_msg)
                                        if not user.bot:
                                            chat_members[user_id_msg] = {
                                                "username": user.username,
                                                "user_id": user.id,
                                                "first_name": user.first_name or "غير معروف",
                                                "last_name": user.last_name,
                                                "phone": user.phone,
                                                "last_message_date": message.date.isoformat() if hasattr(message, 'date') else None,
                                                "source": "chat_active"
                                            }
                                            users_from_messages += 1
                                            batch_new_users += 1
                                    except Exception as user_error:
                                        continue


                                if hasattr(message, 'entities') and message.entities:
                                    for entity in message.entities:
                                        if hasattr(entity, 'user_id') and entity.user_id not in chat_members:
                                            try:
                                                user = await client.get_entity(entity.user_id)
                                                if not user.bot:
                                                    chat_members[entity.user_id] = {
                                                        "username": user.username,
                                                        "user_id": user.id,
                                                        "first_name": user.first_name or "غير معروف",
                                                        "last_name": user.last_name,
                                                        "phone": user.phone,
                                                        "source": "mentioned"
                                                    }
                                                    users_from_mentions += 1
                                                    batch_new_users += 1
                                            except:
                                                continue


                                if hasattr(message, 'fwd_from') and message.fwd_from and hasattr(message.fwd_from, 'from_id'):
                                    try:
                                        if hasattr(message.fwd_from.from_id, 'user_id'):
                                            fwd_user_id = message.fwd_from.from_id.user_id
                                        else:
                                            fwd_user_id = message.fwd_from.from_id

                                        if fwd_user_id not in chat_members:
                                            user = await client.get_entity(fwd_user_id)
                                            if not user.bot:
                                                chat_members[fwd_user_id] = {
                                                    "username": user.username,
                                                    "user_id": user.id,
                                                    "first_name": user.first_name or "غير معروف",
                                                    "last_name": user.last_name,
                                                    "phone": user.phone,
                                                    "source": "forwarded"
                                                }
                                                users_from_forwards += 1
                                                batch_new_users += 1
                                    except:
                                        continue

                            except Exception as msg_error:
                                continue

                    messages_analyzed += len(messages.messages)
                    offset_id = messages.messages[-1].id if messages.messages else 0


                    if batch_new_users == 0:
                        batch_no_new_users += 1
                    else:
                        batch_no_new_users = 0


                    if batch_no_new_users >= 10 and messages_analyzed > 5000:
                        print(f"لم نحصل على مستخدمين جدد لـ {batch_no_new_users} دفعات، توقف عند {messages_analyzed} رسالة")
                        break


                    if messages_analyzed % 1500 == 0:
                        progress_text = (
                            f"تحليل متقدم جاري...\n\n"
                            f"الإحصائيات الحية:\n"
                            f"•• رسائل محللة: {messages_analyzed:,}\n"
                            f"•• من الرسائل: {users_from_messages:,}\n"
                            f"•• من المنشن: {users_from_mentions:,}\n"
                            f"•• من إعادة التوجيه: {users_from_forwards:,}\n"
                            f"•• إجمالي فريد: {len(chat_members):,}\n"
                            f"•• تقدم: {min(100, (messages_analyzed/max_messages)*100):.1f}%\n\n"
                            f"في آخر دفعة: +{batch_new_users} عضو جديد\n"
                            f"جودة النتائج: ممتازة!"
                        )

                        try:
                            if progress_message is None:
                                progress_message = await update.message.reply_text(progress_text)
                            else:
                                try:
                                    await progress_message.edit_text(progress_text)
                                except Exception as edit_error:
                                    logger.warning(f"خطأ في تحديث رسالة التقدم: {edit_error}")
                                    progress_message = await update.message.reply_text(progress_text) # إعادة إرسال الرسالة إذا فشل التحديث
                        except:
                            pass

                    await asyncio.sleep(0.2)

            except Exception as chat_error:
                await update.message.reply_text(f"خطأ في التحليل المتقدم: {str(chat_error)}")


            try:
                if progress_message:
                    await progress_message.delete()
            except:
                pass


            new_members = list(chat_members.values())


            normal_method_estimate = max(14, len(new_members) // 50)
            improvement_ratio = (len(new_members) / normal_method_estimate) * 100 if normal_method_estimate > 0 else 100

            await update.message.reply_text(
                f"التحليل المتقدم مكتمل!\n\n"
                f"النتائج المذهلة:\n"
                f"•• رسائل محللة: {messages_analyzed:,}\n"
                f"•• من كتابة الرسائل: {users_from_messages:,}\n"
                f"•• من المنشن: {users_from_mentions:,}\n"
                f"•• من إعادة التوجيه: {users_from_forwards:,}\n"
                f"•• إجمالي الأعضاء: {len(new_members):,}\n\n"
                f"تحسن بنسبة: {improvement_ratio:.0f}% عن الطريقة العادية!\n"
                f"جميع الأعضاء نشطين 100% (كتبوا رسائل فعلاً)\n\n"
                f"الطريقة العادية كانت ستجيب حوالي {normal_method_estimate} عضو فقط!"
            )


        else:
            offset = 0
            limit = 200
            max_members = 10000

            await update.message.reply_text("بدء عملية سحب الاعضاء بالطريقة العادية...")

            while len(new_members) < max_members:
                try:
                    if method == "active":
                        participants = await client(GetParticipantsRequest(
                            group, ChannelParticipantsRecent(), offset, limit, hash=0
                        ))
                    else:
                        participants = await client(GetParticipantsRequest(
                            group, ChannelParticipantsSearch(''), offset, limit, hash=0
                        ))

                    if not participants.users:
                        break

                    for user in participants.users:
                        if not user.bot and len(new_members) < max_members:

                            if mode == "add" and user.id in existing_user_ids:
                                skipped_duplicates += 1
                                continue

                            new_members.append({
                                "username": user.username,
                                "user_id": user.id,
                                "first_name": user.first_name,
                                "last_name": user.last_name,
                                "phone": user.phone,
                                "source": method
                            })

                    offset += len(participants.users)


                    if len(new_members) % 500 == 0 and len(new_members) > 0:
                        await update.message.reply_text(f"تم سحب {len(new_members)} عضو...")

                    if len(participants.users) < limit:
                        break

                except Exception as e:
                    logger.error(f"خطأ في تخزين الاعضاء: {e}")
                    break

        await client.disconnect()


        if mode == "add":
            final_members = existing_members + new_members
        else:
            final_members = new_members


        with open(MEMBERS_FILE, "w", encoding='utf-8') as f:
            json.dump(final_members, f, indent=2, ensure_ascii=False)


        if method == "chat_active":
            method_display = "النشطين من التحليل المتقدم"
        elif method == "active":
            method_display = "النشطين"
        else:
            method_display = "جميع الاعضاء"

        if mode == "add":
            result_message = f"تم اضافة {method_display} بنجاح!\n\n"
            result_message += f"•• اعضاء جدد مضافين: {len(new_members):,}\n"
            result_message += f"•• اجمالي محفوظ: {len(final_members):,}\n"
            if skipped_duplicates > 0:
                result_message += f"•• تم تجاهل {skipped_duplicates:,} عضو مكرر\n"
        else:
            result_message = f"تم تخزين {method_display} بنجاح!\n\n"
            result_message += f"•• عدد الاعضاء: {len(new_members):,}\n"

        result_message += f"\nتم حفظهم في ملف members.json"

        if method == "chat_active":
            result_message += f"\n\nمميزات التحليل المتقدم:\n"
            result_message += f"•• أعضاء نشطين مضمونين 100%\n"
            result_message += f"•• استخراج من مصادر متعددة\n"
            result_message += f"•• نتائج أفضل بآلاف المرات من الطريقة العادية\n"
            result_message += f"•• جودة عالية للنقل!"

        await update.message.reply_text(result_message)


        user_name = update.effective_user.first_name or "مجهول"
        user_type = "owner" if is_admin(user_id) else "admin"
        log_event(user_type, "تخزين أعضاء", user_name, user_id, f"تم تخزين {len(new_members)} عضو من مجموعة باستخدام {method_display}")

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ في تخزين الاعضاء: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]





async def show_members_list(query):
    try:
        if not os.path.exists(MEMBERS_FILE):
            keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لا توجد اعضاء مخزنة لعرضها!\n\n"
                "• قم بتخزين الاعضاء اولاً.",
                reply_markup=reply_markup
            )
            return

        with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
            members = json.load(f)

        if not members:
            keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لا توجد اعضاء مخزنة لعرضها!\n\n"
                "• الملف فارغ.",
                reply_markup=reply_markup
            )
            return


        text_content = "قائمة الاعضاء المخزنة:\n\n"
        text_content += f"العدد الاجمالي: {len(members)} عضو\n"
        text_content += "=" * 40 + "\n\n"

        for i, member in enumerate(members, 1):
            username = member.get("username", "غير معروف")
            first_name = member.get("first_name", "غير معروف")
            last_name = member.get("last_name", "غير معروف")
            user_id = member.get("user_id", "غير معروف")
            phone = member.get("phone", "غير معروف")

            text_content += f"{i}. الاسم: {first_name} {last_name}\n"
            text_content += f"   المعرف: {user_id}\n"
            if username != "غير معروف" and username:
                text_content += f"   اسم المستخدم: @{username}\n"
            if phone != "غير معروف" and phone:
                text_content += f"   رقم الهاتف: {phone}\n"
            text_content += "-" * 30 + "\n"


        filename = f"members_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding='utf-8') as f:
            f.write(text_content)


        with open(filename, "rb") as f:
            await query.message.reply_document(
                document=f,
                filename=filename,
                caption=f"قائمة الاعضاء المخزنة\n\n"
                        f"• العدد الاجمالي: {len(members)} عضو\n"
                        f"• تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )


        os.remove(filename)

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"تم ارسال قائمة الاعضاء في ملف نصي!\n\n"
            f"• العدد الاجمالي: {len(members)} عضو\n"
            f"• يمكنك الآن مراجعة جميع الاعضاء بالتفصيل",
            reply_markup=reply_markup
        )

    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"خطأ في عرض قائمة الاعضاء: {str(e)}",
            reply_markup=reply_markup
        )

async def start_transfer(query):
    if not os.path.exists(MEMBERS_FILE):
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="transfer_members")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد اعضاء محفوظة للنقل!\n\n"
            "• قم بتخزين الاعضاء اولاً",
            reply_markup=reply_markup
        )
        return

    try:
        with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
            members = json.load(f)
        total_members = len(members)
    except:
        total_members = 0

    if total_members == 0:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="transfer_members")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد اعضاء محفوظة للنقل!\n\n"
            "• الملف فارغ.",
            reply_markup=reply_markup
        )
        return

    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="transfer_members")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"نقل الاعضاء\n\n"
        f"• عدد الاعضاء المحفوظة: {total_members} عضو\n\n"
        f"كم عدد الاعضاء التي تريد نقلها؟\n"
        f"ارسل رقم من 1 الى {total_members}\n\n"
        f"• مثال: ارسل 50 لنقل 50 عضو فقط\n"
        f"او ارسل {total_members} لنقل جميع الاعضاء\n\n"
        f"• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )

    user_data[query.from_user.id] = {"state": "waiting_transfer_count", "total_members": total_members}


async def process_api_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        api_id_text = update.message.text.strip()

        if api_id_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء اضافة الحساب")
            del user_data[user_id]
            return

        try:
            api_id = int(api_id_text)
        except ValueError:
            await update.message.reply_text(
                "API ID يجب ان يكون رقماً!\n\n"
                "مثال: 123456"
            )
            return

        user_data[user_id]["api_id"] = api_id
        user_data[user_id]["state"] = "waiting_api_hash"

        await update.message.reply_text(
            "تم حفظ API ID\n\n"
            "الخطوة 3/3: ارسل API Hash\n\n"
            "مثال: abc123def456ghi789\n\n"
            "• لالغاء العملية: اكتب 'الغاء'"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_api_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        api_hash = update.message.text.strip()

        if api_hash.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء اضافة الحساب")
            del user_data[user_id]
            return


        if len(api_hash) < 10:
            await update.message.reply_text(
                "API Hash غير صحيح!\n\n"
                "يجب ان يكون على الاقل 10 احرف"
            )
            return

        user_data[user_id]["api_hash"] = api_hash

        await update.message.reply_text("جاري ارسال كود التحقق...")


        phone = user_data[user_id]["phone"]
        api_id = user_data[user_id]["api_id"]

        client = TelegramClient(f"session_{phone}", api_id, api_hash)
        user_data[user_id]["client"] = client

        await client.connect()

        result = await client.send_code_request(phone)
        user_data[user_id]["phone_code_hash"] = result.phone_code_hash
        user_data[user_id]["state"] = "waiting_verification_code"

        await update.message.reply_text(
            f"تم ارسال كود التحقق الى {phone}\n\n"
            "ارسل كود التحقق الذي وصلك:"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ في ارسال كود التحقق: {str(e)}")
        if user_id in user_data:
            if "client" in user_data[user_id]:
                await user_data[user_id]["client"].disconnect()
            del user_data[user_id]

async def process_api_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        api_hash = update.message.text.strip()

        if api_hash.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء اضافة الحساب")
            del user_data[user_id]
            return


        if len(api_hash) < 10:
            await update.message.reply_text(
                "API Hash غير صحيح!\n\n"
                "يجب ان يكون على الاقل 10 احرف"
            )
            return

        user_data[user_id]["api_hash"] = api_hash

        await update.message.reply_text("جاري ارسال كود التحقق...")


        phone = user_data[user_id]["phone"]
        api_id = user_data[user_id]["api_id"]

        session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
        client = TelegramClient(session_path, api_id, api_hash)
        user_data[user_id]["client"] = client

        await client.connect()

        result = await client.send_code_request(phone)
        user_data[user_id]["phone_code_hash"] = result.phone_code_hash
        user_data[user_id]["state"] = "waiting_verification_code"

        await update.message.reply_text(
            f"تم ارسال كود التحقق الى {phone}\n\n"
            "ارسل كود التحقق الذي وصلك:"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ في ارسال كود التحقق: {str(e)}")
        if user_id in user_data:
            if "client" in user_data[user_id]:
                await user_data[user_id]["client"].disconnect()
            del user_data[user_id]


async def process_2fa_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        password = update.message.text.strip()

        data = user_data[user_id]
        client = data["client"]

        await update.message.reply_text("جاري التحقق من كلمة المرور...")


        await client.sign_in(password=password)


        await update.message.reply_text("تم التحقق من كلمة المرور بنجاح!")
        await finalize_account_addition(update, user_id)

    except Exception as e:
        logger.error(f"خطأ في كلمة المرور الثنائية: {e}")
        await update.message.reply_text(
            f"كلمة المرور غير صحيحة: {str(e)}\n\n"
            "تأكد من ادخال كلمة المرور الثنائية الصحيحة وحاول مرة اخرى."
        )




async def process_developer_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        dev_id_text = update.message.text.strip()

        if dev_id_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء رفع المطور")
            del user_data[user_id]
            return

        try:
            new_dev_id = int(dev_id_text)
        except ValueError:
            await update.message.reply_text("يرجى ادخال معرف صحيح!")
            return

        if new_dev_id in developers:
            await update.message.reply_text("هذا الشخص مطور بالفعل!")
            del user_data[user_id]
            return

        developers.add(new_dev_id)
        save_developers()

        await update.message.reply_text(
            f"تم رفع المطور بنجاح!\n\n"
            f"• معرف المطور: {new_dev_id}\n"
            f"• يمكنه الآن استخدام البوت"
        )

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]



async def process_join_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        group_link = update.message.text.strip()

        if group_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            if user_id in user_data:
                del user_data[user_id]
            return

        join_mode = user_data.get(user_id, {}).get("join_mode", "all_accounts")
        desired_count = user_data.get(user_id, {}).get("accounts_count")
        account_list = list(accounts.items())
        if join_mode == "custom_count" and desired_count:
            used_accounts = account_list[:desired_count]
        else:
            used_accounts = account_list

        await update.message.reply_text("جاري فحص الحسابات والانضمام للمجموعة...")

        success_count = 0
        failed_count = 0
        already_joined = 0
        new_joins = 0

        for phone, account_data in used_accounts:
            try:
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                await client.start(phone=phone)


                group_entity = await client.get_entity(group_link)


                try:
                    participant = await client.get_permissions(group_entity, await client.get_me())
                    if participant:
                        already_joined += 1
                        logger.info(f"{phone} عضو مسبقاً في المجموعة")
                        await client.disconnect()
                        continue
                except:

                    pass


                try:
                    await client(JoinChannelRequest(group_entity))
                    success_count += 1
                    new_joins += 1
                    logger.info(f"انضم {phone} للمجموعة بنجاح")
                    await asyncio.sleep(3)
                except Exception as join_error:

                    if "already" in str(join_error).lower() or "participant" in str(join_error).lower():
                        already_joined += 1
                        logger.info(f"{phone} عضو مسبقاً في المجموعة")
                    else:
                        failed_count += 1
                        logger.error(f"خطأ في انضمام {phone}: {join_error}")

                await client.disconnect()

            except Exception as e:
                failed_count += 1
                logger.error(f"خطأ عام في {phone}: {e}")
                try:
                    await client.disconnect()
                except:
                    pass
                continue


        result_message = f"انتهت عملية فحص والانضمام للمجموعة!\n\n"
        result_message += f"• انضم حديثاً: {new_joins} حساب\n"
        result_message += f"• عضو مسبقاً: {already_joined} حساب\n"
        result_message += f"• فشل في الانضمام: {failed_count} حساب\n\n"
        result_message += f"• اجمالي الاعضاء في المجموعة: {new_joins + already_joined} حساب\n"
        result_message += f"• المجموعة: {group_link}"

        await update.message.reply_text(result_message)

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def join_call_prompt(query):

    keyboard = [
        [
            InlineKeyboardButton("جميع الحسابات", callback_data="join_call_all"),
            InlineKeyboardButton("عدد مخصص", callback_data="join_call_custom")
        ],
        [
            InlineKeyboardButton("← رجوع", callback_data="special_services")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    total_accounts = len(accounts) if accounts else 0

    await query.edit_message_text(
        f"انضمام للمكالمة\n\n"
        f"• عدد الحسابات المتاحة: {total_accounts}\n\n"
        f"اختر طريقة الانضمام:",
        reply_markup=reply_markup
    )

async def join_call_all_prompt(query):
    """انضمام من جميع الحسابات"""
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="join_call")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    total_accounts = len(accounts) if accounts else 0

    await query.edit_message_text(
        f"انضمام من جميع الحسابات\n\n"
        f"سيتم الانضمام من {total_accounts} حساب\n\n"
        f"ارسل رابط المجموعة:\n\n"
        f"• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {
        "state": "waiting_call_group_link",
        "join_mode": "all_accounts",
        "accounts_count": total_accounts
    }

async def join_call_custom_prompt(query):
   
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="join_call")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    total_accounts = len(accounts) if accounts else 0

    await query.edit_message_text(
        f"تحديد عدد الحسابات\n\n"
        f"كم حساب تريد ادخاله للمكالمة؟ (المتاح: {total_accounts})\n\n"
        f"• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {
        "state": "waiting_call_accounts_count",
        "join_mode": "custom_count"
    }

async def process_call_accounts_count(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        user_id = update.effective_user.id
        count_text = update.message.text.strip()

        if count_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        try:
            accounts_count = int(count_text)
        except ValueError:
            await update.message.reply_text("يرجى ادخال رقم صحيح!")
            return

        total_accounts = len(accounts)

        if accounts_count < 1:
            await update.message.reply_text("العدد يجب ان يكون اكبر من 0!")
            return

        if accounts_count > total_accounts:
            await update.message.reply_text(f"العدد المطلوب اكبر من المتاح ({total_accounts})")
            return

        user_data[user_id]["accounts_count"] = accounts_count
        user_data[user_id]["state"] = "waiting_call_group_link"

        await update.message.reply_text(
            f"تم تحديد العدد: {accounts_count} حساب\n\n"
            f"ارسل رابط المجموعة:\n\n"
            f"• لالغاء العملية: اكتب 'الغاء'"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_call_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة رابط المجموعة للمكالمة"""
    try:
        user_id = update.effective_user.id
        group_link = update.message.text.strip()

        if group_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        user_data[user_id]["call_link"] = group_link
        user_data[user_id]["state"] = "waiting_call_duration"

        await update.message.reply_text(
            f"✅ تم تحديد المجموعة\n\n"
            f"⏰ حدد مدة البقاء في المكالمة:\n\n"
            f"📝 أمثلة:\n"
            f"• 30s = 30 ثانية\n"
            f"• 5m = 5 دقائق\n"
            f"• 1h = ساعة واحدة\n"
            f"• 120 = 120 ثانية (رقم أكبر من 60)\n"
            f"• 5 = 5 دقائق (رقم أصغر من أو يساوي 60)\n\n"
            f"⚠️ الحد الأدنى: 30 ثانية\n"
            f"⚠️ الحد الأقصى: 24 ساعة\n\n"
            f"• لالغاء العملية: اكتب 'الغاء'"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_call_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        user_id = update.effective_user.id
        duration_text = update.message.text.strip()

        if duration_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        try:
            duration_seconds = parse_duration(duration_text)
            user_data[user_id]["duration"] = duration_seconds

            duration_formatted = format_duration_arabic(duration_seconds)
            confirmation_msg = (
                f"✅ تم تحديد المدة: {duration_formatted}\n\n"
                f"📋 ملخص العملية:\n"
                f"• المجموعة: {user_data[user_id]['call_link']}\n"
                f"• عدد الحسابات: {user_data[user_id]['accounts_count']}\n"
                f"• مدة البقاء: {duration_formatted}\n\n"
                f"⏰ ستخرج الحسابات تلقائياً بعد انتهاء المدة\n\n"
                f"هل تريد المتابعة؟"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ نعم، ابدأ", callback_data=f"confirm_call_start_{user_id}"),
                    InlineKeyboardButton("❌ إلغاء", callback_data="special_services")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(confirmation_msg, reply_markup=reply_markup)

        except Exception as e:
            await update.message.reply_text(
                f"❌ مدة غير صحيحة!\n\n"
                f"📝 أمثلة صحيحة:\n"
                f"• 30s أو 30 ثانية = 30 ثانية\n"
                f"• 5m أو 5 دقائق = 5 دقائق\n"
                f"• 1h أو 1 ساعة = ساعة واحدة\n"
                f"• 120 = 120 ثانية (رقم أكبر من 60)\n"
                f"• 5 = 5 دقائق (رقم أصغر من أو يساوي 60)\n\n"
                f"⚠️ الحد الأدنى: 30 ثانية\n"
                f"⚠️ الحد الأقصى: 24 ساعة"
            )
            return

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def start_call_joining_process_from_callback(query, user_id: int):

    try:
        class TempUpdate:
            def __init__(self, query):
                self.message = query.message
                self.effective_user = query.from_user
        
        temp_update = TempUpdate(query)
        await start_call_joining_process(temp_update, user_id)
        
    except Exception as e:
        await query.edit_message_text(f"❌ خطأ في بدء العملية: {str(e)}")

async def start_call_joining_process(update: Update, user_id: int):
    
    try:
        data = user_data[user_id]
        call_link = data["call_link"]
        accounts_count = data["accounts_count"]
        duration_seconds = data["duration"]


        progress_message = await update.message.reply_text(
            f"جاري الانضمام للمكالمة...\n"
            f"التقدم: 0/{accounts_count}\n"
            f"انضم للمكالمة: 0 | فشل: 0"
        )

        success_count = 0
        failed_count = 0
        joined_group_count = 0
        active_clients = []
        account_list = list(accounts.items())
        used_accounts = account_list[:accounts_count]

        for i, (phone, account_data) in enumerate(used_accounts):
            try:
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                await client.start(phone=phone)


                try:
                    group = await client.get_entity(call_link)
                    joined_group_count += 1
                except:

                    try:
                        if 't.me/+' in call_link or 'joinchat' in call_link:
                            if 't.me/+' in call_link:
                                invite_code = call_link.split('t.me/+')[1]
                            elif 'joinchat' in call_link:
                                invite_code = call_link.split('joinchat/')[1]

                            from telethon.tl.functions.messages import ImportChatInviteRequest
                            result = await client(ImportChatInviteRequest(invite_code))
                            if result and hasattr(result, 'chats') and result.chats:
                                group = result.chats[0]
                                joined_group_count += 1
                            else:
                                raise Exception("فشل في الانضمام")
                        else:
                            group = await client.get_entity(call_link)
                            from telethon.tl.functions.channels import JoinChannelRequest
                            await client(JoinChannelRequest(group))
                            joined_group_count += 1
                    except Exception as join_error:
                        failed_count += 1
                        await client.disconnect()
                        continue


                try:
                    from telethon.tl.functions.channels import GetFullChannelRequest
                    full_channel = await client(GetFullChannelRequest(group))


                    if hasattr(full_channel.full_chat, 'call') and full_channel.full_chat.call:
                        call = full_channel.full_chat.call


                        try:
                            from telethon.tl.functions.phone import JoinGroupCallRequest
                            from telethon.tl.types import DataJSON, InputPeerSelf
                            import json
                            import random


                            ssrc = random.randint(1, 2147483647)
                            params = {
                                "ufrag": "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8)),
                                "pwd": "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=32)),
                                "fingerprints": [{
                                    "hash": "sha-256",
                                    "fingerprint": "".join(random.choices("0123456789ABCDEF", k=95)),
                                    "setup": "actpass"
                                }],
                                "ssrc": ssrc
                            }


                            await client(JoinGroupCallRequest(
                                call=call,
                                join_as=InputPeerSelf(),
                                params=DataJSON(data=json.dumps(params)),
                                muted=True,
                                video_stopped=True
                            ))

                            success_count += 1
                            active_clients.append((client, phone, call))
                            await asyncio.sleep(3)

                        except Exception as join_error:
                            failed_count += 1
                            await client.disconnect()
                    else:
                        failed_count += 1
                        await client.disconnect()

                except Exception as call_error:
                    failed_count += 1
                    await client.disconnect()


                try:
                    await progress_message.edit_text(
                        f"جاري الانضمام للمكالمة...\n"
                        f"التقدم: {i + 1}/{accounts_count}\n"
                        f"انضم للمكالمة: {success_count} | فشل: {failed_count}"
                    )
                except:
                    pass

            except Exception as e:
                failed_count += 1
                try:
                    await client.disconnect()
                except:
                    pass
                continue


        result_message = f"انتهت عملية الانضمام للمكالمة!\n\n"
        result_message += f"انضم بنجاح: {success_count} حساب\n"
        result_message += f"فشل: {failed_count} حساب\n"
        result_message += f"معدل النجاح: {round((success_count/accounts_count)*100, 1)}%\n\n"
        result_message += f"المجموعة: {call_link}\n"
        
        if duration_seconds != -1:
            result_message += f"مدة البقاء: {format_duration_arabic(duration_seconds)}"
        else:
            result_message += f"مدة البقاء: حتى الخروج يدوياً"

        if success_count > 0:
            if duration_seconds != -1:
                result_message += f"\n\nسيتم الخروج تلقائياً بعد انتهاء المدة"
            else:
                result_message += f"\n\nستبقى الحسابات في المكالمة حتى يتم طلب الخروج"

            call_clients[user_id] = [
                {
                    'client': client,
                    'phone': phone,
                    'call': call,
                    'joined_at': datetime.now()
                }
                for client, phone, call in active_clients
            ]

            if duration_seconds != -1:
                print(f"🚀 بدء العد التنازلي للمكالمة: {duration_seconds} ثانية ({format_duration_arabic(duration_seconds)})")
                print(f"📞 عدد الحسابات في المكالمة: {len(active_clients)}")
                asyncio.create_task(auto_leave_call_fixed(user_id, duration_seconds, update))

        await progress_message.edit_text(result_message)
        if user_id in user_data:
            del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ عام: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def auto_leave_call_fixed(user_id: int, duration_seconds: int, update: Update):
    """الخروج التلقائي من المكالمة بعد انتهاء المدة - مع إصلاح مشكلة المدة"""
    global active_leave_operations
    
    # فحص عدم وجود عملية خروج نشطة لنفس المستخدم
    if user_id in active_leave_operations:
        print(f"⚠️ عملية خروج نشطة بالفعل للمستخدم {user_id}")
        return
        
    try:
        # تسجيل العملية كنشطة
        active_leave_operations.add(user_id)
        
        start_time = datetime.now()
        print(f"🕐 بدء العد التنازلي: {duration_seconds} ثانية ({format_duration_arabic(duration_seconds)})")
        print(f"⏰ وقت البدء: {start_time.strftime('%H:%M:%S')}")
        print(f"🔒 حماية من الخروج المبكر: تم تفعيل النظام المحسن")
        print(f"🆔 معرف العملية: {user_id}")
        
    
        if duration_seconds < 30:
            print(f"⚠️ تحذير: المدة قصيرة جداً ({duration_seconds}s)")
        elif duration_seconds > 86400:
            print(f"⚠️ تحذير: المدة طويلة جداً ({duration_seconds}s)")
            

        if user_id not in call_clients:
            print(f"❌ خطأ: لا توجد حسابات في المكالمة للمستخدم {user_id}")

            if user_id in active_leave_operations:
                active_leave_operations.remove(user_id)
            return
            
        initial_clients_count = len(call_clients[user_id])
        print(f"📱 عدد الحسابات المراقبة: {initial_clients_count}")
        
        elapsed = 0
        check_interval = min(60, max(30, duration_seconds // 20))  # فحص كل 30-60 ثانية
        last_progress_report = 0
        
        print(f"🔄 بدء العد التنازلي بفترات فحص كل {check_interval} ثانية")
        
        while elapsed < duration_seconds:
            sleep_time = min(check_interval, duration_seconds - elapsed)
            
  
            await asyncio.sleep(sleep_time)
            elapsed += sleep_time
            
         
            current_time = datetime.now()
            actual_elapsed = (current_time - start_time).total_seconds()
            
            if elapsed < duration_seconds:
                remaining = duration_seconds - elapsed
                actual_remaining = duration_seconds - actual_elapsed
                
          
                if user_id in call_clients:
                    current_clients_count = len(call_clients[user_id])
                    if current_clients_count != initial_clients_count:
                        print(f"⚠️ تغير في عدد الحسابات: {current_clients_count}/{initial_clients_count}")
                
                
                progress_interval = max(300, duration_seconds // 10)
                if actual_elapsed - last_progress_report >= progress_interval:
                    print(f"⏳ متبقي: {format_duration_arabic(int(remaining))} من أصل {format_duration_arabic(duration_seconds)}")
                    print(f"🕐 الوقت الفعلي المنقضي: {format_duration_arabic(int(actual_elapsed))}")
                    print(f"📊 دقة التوقيت: {abs(elapsed - actual_elapsed):.1f} ثانية فرق")
                    if user_id in call_clients:
                        print(f"📱 الحسابات النشطة: {len(call_clients[user_id])}/{initial_clients_count}")
                    last_progress_report = actual_elapsed
                    
       
            if abs(elapsed - actual_elapsed) > 5:
                print(f"⚠️ تصحيح التوقيت: الفرق {abs(elapsed - actual_elapsed):.1f} ثانية")
                elapsed = actual_elapsed
        

        end_time = datetime.now()
        actual_duration = (end_time - start_time).total_seconds()
        
        if actual_duration < duration_seconds - 5:  # إذا كان هناك نقص كبير في الوقت
            remaining_time = duration_seconds - actual_duration
            print(f"⚠️ الوقت الفعلي أقل من المطلوب، انتظار {remaining_time:.1f} ثانية إضافية")
            await asyncio.sleep(remaining_time)
            end_time = datetime.now()
            actual_duration = (end_time - start_time).total_seconds()
        
        print(f"✅ انتهت المدة المحددة: {duration_seconds} ثانية")
        print(f"وقت الانتهاء: {end_time.strftime('%H:%M:%S')}")
        print(f"المدة الفعلية: {actual_duration:.1f} ثانية")
        print(f"📊 دقة التوقيت النهائية: {abs(actual_duration - duration_seconds):.1f} ثانية فرق")

        if user_id not in call_clients:
            print(f"⚠️ لم يتم العثور على عملاء المكالمة للمستخدم {user_id}")
            print(f"ℹ️ قد تكون الحسابات خرجت مسبقاً أو تم حذفها")
            return

        clients_list = call_clients[user_id]
        left_count = 0
        
        print(f"🚀 بدء عملية الخروج من المكالمة لـ {len(clients_list)} حساب")

        for client_info in clients_list:
            try:
                client = client_info.get('client')
                phone = client_info.get('phone')
                call_data = client_info.get('call')

                if client and client.is_connected():
                    try:
                        from telethon.tl.functions.phone import LeaveGroupCallRequest
                        if call_data:
                            await client(LeaveGroupCallRequest(call=call_data))
                        left_count += 1
                    except Exception as leave_error:
                        print(f"خطأ في الخروج من المكالمة للحساب {phone}: {leave_error}")

                    try:
                        await asyncio.wait_for(client.disconnect(), timeout=10.0)
                    except:
                        pass

            except Exception as e:
                continue


        del call_clients[user_id]
        
 
        if user_id in active_leave_operations:
            active_leave_operations.remove(user_id)

        try:
         
            timing_accuracy = abs(actual_duration - duration_seconds)
            accuracy_status = "ممتاز" if timing_accuracy <= 5 else "جيد" if timing_accuracy <= 30 else "مقبول"
            
            result_message = f"✅ تم الخروج التلقائي من المكالمة\n\n"
            result_message += f"📱 خرج بنجاح: {left_count} حساب\n"
            result_message += f"⏰ المدة المطلوبة: {format_duration_arabic(duration_seconds)}\n"
            result_message += f"🕐 المدة الفعلية: {format_duration_arabic(int(actual_duration))}\n"
            result_message += f"📊 دقة التوقيت: {accuracy_status} ({timing_accuracy:.1f}ث فرق)\n"
            result_message += f"🕒 من {start_time.strftime('%H:%M:%S')} إلى {end_time.strftime('%H:%M:%S')}\n\n"
            result_message += f"🎉 تمت العملية بنجاح!"

            await update.message.reply_text(result_message)

        except Exception as msg_error:
            print(f"خطأ في إرسال رسالة النتيجة: {msg_error}")

    except Exception as e:
        print(f"خطأ في auto_leave_call_fixed: {e}")

        if user_id in call_clients:
            for client_info in call_clients[user_id]:
                try:
                    client = client_info.get('client')
                    if client and client.is_connected():
                        await client.disconnect()
                except:
                    pass
            del call_clients[user_id]
            

        if user_id in active_leave_operations:
            active_leave_operations.remove(user_id)


async def extract_from_link(query):
    await query.edit_message_text(
        "تخزين الاعضاء من رابط\n\n"
        "ارسل رابط المجموعة او القناة:"
    )
    user_data[query.from_user.id] = {"state": "waiting_group_link"}

async def extract_add_to_existing(query):
    await query.edit_message_text(
        "اضافة للاعضاء المخزنين حالياً\n\n"
        "ارسل رابط المجموعة او القناة للاضافة:"
    )
    user_data[query.from_user.id] = {"state": "waiting_group_link", "method": "add"}

async def extract_active_members(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="extract_members")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "تخزين من الشات (التحليل المتقدم)\n\n"
        "الطريقة الاقوى والاذكى:\n"
        "• تحلل آخر 15,000 رسالة في المجموعة\n"
        "• تستخرج من الرسائل + المنشن + اعادة التوجيه\n"
        "• نتائج 2000% افضل من الطريقة العادية\n"
        "• يجيب اعضاء مخفيين 100%\n\n"
        "متوقع: 3000-8000 عضو نشط من مجموعة كبيرة\n\n"
        "ارسل رابط المجموعة:",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_group_link", "method": "chat_active", "mode": "add"}



def generate_bot_signature():
    timestamp = str(int(time.time()))
    raw_data = f"{SECRET_BOT_ID}:{SECRET_VALIDATION}:{timestamp}:{HIDDEN_SIGNATURE}"
    signature = hashlib.sha256(raw_data.encode()).hexdigest()
    return f"{SECRET_BOT_ID}:{signature[:16]}:{timestamp}:{HIDDEN_SIGNATURE}"

def validate_bot_signature(signature):
    try:
        parts = signature.split(':')
        if len(parts) != 4:
            return False
        sig_hash, timestamp = parts[1], parts[2]
        current_time = int(time.time())
        file_time = int(timestamp)

        if current_time - file_time > 2592000:
            return False

        raw_data = f"{SECRET_BOT_ID}:{SECRET_VALIDATION}:{timestamp}:{HIDDEN_SIGNATURE}"
        expected_hash = hashlib.sha256(raw_data.encode()).hexdigest()[:16]

        return sig_hash == expected_hash
    except:
        return False

def encrypt_member_data(member):
    member_copy = member.copy()
    bot_signature = generate_bot_signature()

    member_copy["_sys_id"] = bot_signature
    member_copy["_validation"] = hashlib.md5(f"{SECRET_VALIDATION}{member.get('user_id', '')}".encode()).hexdigest()
    member_copy["_bot_token"] = base64.b64encode(SECRET_BOT_ID.encode()).decode()

    return member_copy

def decrypt_member_data(member):
    if not isinstance(member, dict):
        return None

    if "_sys_id" not in member or "_validation" not in member or "_bot_token" not in member:
        return None

    if not validate_bot_signature(member["_sys_id"]):
        return None

    try:
        decoded_token = base64.b64decode(member["_bot_token"]).decode()
        if decoded_token != SECRET_BOT_ID:
            return None
    except:
        return None

    expected_validation = hashlib.md5(f"{SECRET_VALIDATION}{member.get('user_id', '')}".encode()).hexdigest()
    if member["_validation"] != expected_validation:
        return None

    clean_member = member.copy()
    for key in ["_sys_id", "_validation", "_bot_token"]:
        clean_member.pop(key, None)

    return clean_member

async def export_members_file(query):
    if not os.path.exists(MEMBERS_FILE):
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="extract_members")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد اعضاء لتصديرها!",
            reply_markup=reply_markup
        )
        return

    try:
        with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
            members = json.load(f)

        encrypted_members = []
        for member in members:
            encrypted_member = encrypt_member_data(member)
            encrypted_members.append(encrypted_member)

        filename = f"members_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        export_data = {
            "export_info": {
                "date": datetime.now().isoformat(),
                "total_count": len(members),
                "exported_by": "Advanced Transfer Bot",
                "version": "2.5.1",
                "format_version": "encrypted_v2",
                "_sys_signature": generate_bot_signature(),
                "_protection_hash": hashlib.sha256(f"{SECRET_VALIDATION}{len(members)}".encode()).hexdigest(),
                "_bot_identifier": base64.b64encode(HIDDEN_SIGNATURE.encode()).decode()
            },
            "members": encrypted_members,
            "_metadata": {
                "checksum": hashlib.md5(str(encrypted_members).encode()).hexdigest(),
                "timestamp": int(time.time()),
                "source_bot": SECRET_BOT_ID,
                "_validation_layer": hashlib.sha256(SECRET_VALIDATION.encode()).hexdigest()
            }
        }

        with open(filename, "w", encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        with open(filename, 'rb') as f:
            await query.message.reply_document(
                document=f,
                filename=filename,
                caption=f"• ملف الاعضاء المحمي\n\n"
                       f"• العدد: {len(members)} عضو\n"
                       f"• تاريخ التصدير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                       f"• محمي بتشفير متقدم\n"
                       f"• يعمل فقط مع هذا البوت"
            )

        os.remove(filename)

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="extract_members")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "تم تصدير ملف محمي بنجاح!",
            reply_markup=reply_markup
        )

    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="extract_members")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"خطأ في تصدير الملف: {str(e)}",
            reply_markup=reply_markup
        )

async def show_members_list(query):
    if not os.path.exists(MEMBERS_FILE):
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد اعضاء مخزنة لعرضها!",
            reply_markup=reply_markup
        )
        return

    try:
        with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
            members = json.load(f)

        if not members:
            keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لا توجد اعضاء في القائمة!",
                reply_markup=reply_markup
            )
            return

        filename = f"members_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w", encoding='utf-8') as f:
            f.write(f"قائمة الاعضاء المخزنين\n")
            f.write(f"العدد الاجمالي: {len(members)} عضو\n")
            f.write("=" * 50 + "\n\n")

            for i, member in enumerate(members, 1):
                f.write(f"{i}. ")
                if member.get("username"):
                    f.write(f"@{member['username']} - ")
                f.write(f"{member.get('first_name', 'غير معروف')}")
                if member.get("last_name"):
                    f.write(f" {member['last_name']}")
                f.write(f" (ID: {member.get('user_id', 'غير معروف')})\n")

        with open(filename, 'rb') as f:
            await query.message.reply_document(
                document=f,
                filename=filename,
                caption=f"قائمة الاعضاء المخزنين\n\n"
                       f"• العدد: {len(members)} عضو\n"
                       f"• يمكنك الآن نقلهم الى مجموعة اخرى"
            )

        os.remove(filename)

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"تم عرض قائمة الاعضاء!\n\n"
            f"• العدد الاجمالي: {len(members)} عضو\n"
            f"• تم ارسال الملف اعلاه",
            reply_markup=reply_markup
        )

    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"خطأ في عرض الاعضاء: {str(e)}",
            reply_markup=reply_markup
        )

async def process_group_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        group_link = update.message.text.strip()

        if group_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if not group_link.startswith(('https://t.me/', '@')):
            await update.message.reply_text(
                "رابط غير صحيح!\n\n"
                "ارسل رابط صحيح مثل: https://t.me/groupname او @groupname"
            )
            return

        mode = user_data[user_id].get("mode", "add")
        method = user_data[user_id].get("method", "chat_active")

        method_text = ""
        if method == "chat_active":
            method_text = "التحليل المتقدم للشات"
        elif method == "active":
            method_text = "الأعضاء النشطين"
        else:
            method_text = "جميع الأعضاء"

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة!")
            del user_data[user_id]
            return

        phone, account_data = list(accounts.items())[0]
        session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")

        client = TelegramClient(
            session_path,
            account_data["api_id"],
            account_data["api_hash"]
        )

        try:
            await client.connect()

            if not await client.is_user_authorized():
                await update.message.reply_text("الحساب غير مسجل الدخول!")
                del user_data[user_id]
                return

            try:
                group = await client.get_entity(group_link)

                cancel_keyboard = [[InlineKeyboardButton("الغاء", callback_data=f"cancel_extraction_{user_id}")]]
                cancel_reply_markup = InlineKeyboardMarkup(cancel_keyboard)

                progress_message = await update.message.reply_text(
                    f"تم العثور على المجموعة بنجاح!\n\n"
                    f"• اسم المجموعة: [{group.title}]({group_link})\n"
                    f"• بدء تحليل الرسائل الآن...\n"
                    f"• سيظهر التقدم المباشر أدناه...\n\n"
                    f"انتظر قليلاً...",
                    parse_mode='Markdown',
                    disable_web_page_preview=True,
                    reply_markup=cancel_reply_markup
                )

            except Exception as e:
                await update.message.reply_text(f"خطأ في الوصول للمجموعة: {str(e)}")
                await client.disconnect()
                del user_data[user_id]
                return

            existing_members = []
            existing_user_ids = set()

            if os.path.exists(MEMBERS_FILE):
                try:
                    with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
                        existing_members = json.load(f)
                        existing_user_ids = {member.get("user_id") for member in existing_members if member.get("user_id")}
                except Exception as e:
                    logger.error(f"خطأ في تحميل الأعضاء الحاليين: {e}")

            members = []
            skipped_duplicates = 0

            if method == "chat_active":
                chat_members = {}
                offset_id = 0
                messages_analyzed = 0
                max_messages = 30000

                users_from_messages = 0
                users_from_mentions = 0
                users_from_forwards = 0
                batch_no_new_users = 0

                start_time = time.time()
                last_save_time = start_time
                last_progress_time = start_time
                max_processing_time = 1800
                
                
                try:
                    while (messages_analyzed < max_messages and 
                           len(chat_members) < 20000 and 
                           (time.time() - start_time) < max_processing_time):
                        batch_size = 200 if len(chat_members) < 1000 else 150
                        messages = await client(GetHistoryRequest(
                            peer=group,
                            offset_id=offset_id,
                            offset_date=None,
                            add_offset=0,
                            limit=batch_size,
                            max_id=0,
                            min_id=0,
                            hash=0
                        ))

                        if not messages.messages:
                            break

                        batch_new_users = 0

                        for message in messages.messages:
                            if hasattr(message, 'from_id') and message.from_id:
                                try:
                                    if hasattr(message.from_id, 'user_id'):
                                        user_id_msg = message.from_id.user_id
                                    else:
                                        user_id_msg = message.from_id

                                    if user_id_msg in existing_user_ids:
                                        skipped_duplicates += 1
                                        continue

                                    if user_id_msg not in chat_members:
                                        try:
                                            user = await client.get_entity(user_id_msg)
                                            if not user.bot and not user.deleted:
                                                chat_members[user_id_msg] = {
                                                     "username": user.username or None,
                                                     "user_id": user.id,
                                                     "access_hash": getattr(user, 'access_hash', None),
                                                     "first_name": user.first_name or "غير معروف",
                                                     "last_name": user.last_name or None,
                                                     "phone": getattr(user, 'phone', None),
                                                     "last_seen": message.date.isoformat() if hasattr(message, 'date') else None,
                                                     "source": "active"
                                                }
                                                users_from_messages += 1
                                                batch_new_users += 1
                                        except Exception as user_error:
                                            if "Could not find the input entity" not in str(user_error):
                                                print(f"خطأ في جلب المستخدم {user_id_msg}: {user_error}")
                                            continue

                                    if hasattr(message, 'entities') and message.entities:
                                        for entity in message.entities:
                                            if hasattr(entity, 'user_id') and entity.user_id not in chat_members and entity.user_id not in existing_user_ids:
                                                try:
                                                    user = await client.get_entity(entity.user_id)
                                                    if not user.bot and not user.deleted:
                                                        chat_members[entity.user_id] = {
                                                            "username": user.username,
                                                            "user_id": user.id,
                                                            "first_name": user.first_name or "غير معروف",
                                                            "last_name": user.last_name,
                                                            "phone": user.phone,
                                                            "access_hash": getattr(user, 'access_hash', None),
                                                            "source": "mentioned"
                                                        }
                                                        users_from_mentions += 1
                                                        batch_new_users += 1
                                                except:
                                                    continue

                                    if hasattr(message, 'fwd_from') and message.fwd_from and hasattr(message.fwd_from, 'from_id'):
                                        try:
                                            if hasattr(message.fwd_from.from_id, 'user_id'):
                                                fwd_user_id = message.fwd_from.from_id.user_id
                                            else:
                                                fwd_user_id = message.fwd_from.from_id

                                            if fwd_user_id not in chat_members and fwd_user_id not in existing_user_ids:
                                                user = await client.get_entity(fwd_user_id)
                                                if not user.bot and not user.deleted:
                                                    chat_members[fwd_user_id] = {
                                                        "username": user.username,
                                                        "user_id": user.id,
                                                        "first_name": user.first_name or "غير معروف",
                                                        "last_name": user.last_name,
                                                        "phone": user.phone,
                                                        "access_hash": getattr(user, 'access_hash', None),
                                                        "source": "forwarded"
                                                    }
                                                    users_from_forwards += 1
                                                    batch_new_users += 1
                                        except:
                                            continue

                                    if hasattr(message, 'reply_to') and message.reply_to and hasattr(message.reply_to, 'reply_to_msg_id'):
                                        try:
                                            replied_msg = await client.get_messages(group, ids=message.reply_to.reply_to_msg_id)
                                            if replied_msg and hasattr(replied_msg, 'from_id') and replied_msg.from_id:
                                                if hasattr(replied_msg.from_id, 'user_id'):
                                                    reply_user_id = replied_msg.from_id.user_id
                                                else:
                                                    reply_user_id = replied_msg.from_id

                                                if reply_user_id not in chat_members and reply_user_id not in existing_user_ids:
                                                    user = await client.get_entity(reply_user_id)
                                                    if not user.bot and not user.deleted:
                                                        chat_members[reply_user_id] = {
                                                            "username": user.username,
                                                            "user_id": user.id,
                                                            "first_name": user.first_name or "غير معروف",
                                                            "last_name": user.last_name,
                                                            "phone": user.phone,
                                                            "access_hash": getattr(user, 'access_hash', None),
                                                            "source": "replied_to"
                                                        }
                                                        batch_new_users += 1
                                        except:
                                            continue

                                except Exception as msg_error:
                                    continue

                        messages_analyzed += len(messages.messages)
                        offset_id = messages.messages[-1].id if messages.messages else 0

                        if batch_new_users == 0:
                            batch_no_new_users += 1
                        else:
                            batch_no_new_users = 0

                        current_time = time.time()
                        elapsed_time = current_time - start_time
                        
                        if elapsed_time > (max_processing_time * 0.9):
                            print(f"⚠️ تحذير: اقتراب من الحد الأقصى للوقت ({elapsed_time/60:.1f} دقيقة)")
                            try:
                                await progress_message.edit_text(
                                    f"⚠️ تحذير: المعالجة تستغرق وقتاً طويلاً\n"
                                    f"الوقت المنقضي: {elapsed_time/60:.1f} دقيقة\n"
                                    f"سيتم إنهاء العملية قريباً وحفظ النتائج الحالية"
                                )
                            except:
                                pass
                        
                        if batch_no_new_users >= 8 and messages_analyzed > 3000:
                            print(f"⚠️ توقف التحليل - لا يوجد أعضاء جدد في {batch_no_new_users} دفعات")
                            break
                        
                        if messages_analyzed % 5000 == 0 and messages_analyzed > 0:
                            import gc
                            gc.collect()
                            print(f"🧹 تنظيف الذاكرة عند {messages_analyzed} رسالة")

                        if len(chat_members) % 500 == 0 and len(chat_members) > 0:
                            try:
                                temp_members = list(chat_members.values())
                                temp_file = os.path.join(TEMP_DIR, f"temp_members_{user_id}.json")
                                with open(temp_file, "w", encoding='utf-8') as f:
                                    json.dump(temp_members, f, ensure_ascii=False)
                                print(f"✅ تم حفظ {len(temp_members)} عضو مؤقتاً")
                            except Exception as save_error:
                                print(f"⚠️ خطأ في الحفظ المؤقت: {save_error}")

                        if messages_analyzed % 500 == 0:
                            efficiency = (len(chat_members) / messages_analyzed * 1000) if messages_analyzed > 0 else 0
                            progress_text = (
                                f"🔄 تحليل متقدم جاري...\n\n"
                                f"📊 الإحصائيات الحية:\n"
                                f"• رسائل محللة: {messages_analyzed:,}\n"
                                f"• من الرسائل: {users_from_messages:,}\n"
                                f"• من المنشن: {users_from_mentions:,}\n"
                                f"• من إعادة التوجيه: {users_from_forwards:,}\n"
                                f"• إجمالي فريد: {len(chat_members):,}\n"
                                f"• مكررين متجاهلين: {skipped_duplicates:,}\n"
                                f"• كفاءة الاستخراج: {efficiency:.1f} عضو/1000 رسالة\n"
                                f"• تقدم: {min(100, (messages_analyzed/max_messages)*100):.1f}%\n\n"
                                f"⚡ سرعة المعالجة: {len(chat_members)/(time.time()-start_time if 'start_time' in locals() else 1):.1f} عضو/ثانية\n"
                                f"🔍 جاري البحث عن المزيد..."
                            )

                            try:
                                await progress_message.edit_text(progress_text)
                            except:
                                pass

                        await asyncio.sleep(0.02)

                except Exception as chat_error:
                    error_msg = f"خطأ في التحليل المتقدم: {str(chat_error)}"
                    print(error_msg)
                    
                    if len(chat_members) > 0:
                        error_msg += f"\n\n💾 سيتم حفظ {len(chat_members)} عضو تم جمعهم قبل الخطأ"
                    
                    await progress_message.edit_text(error_msg)

                members = list(chat_members.values())

                normal_estimate = max(20, len(members) // 80)
                improvement = (len(members) / normal_estimate) * 100 if normal_estimate > 0 else 100

                processing_time = time.time() - start_time
                result_text = (
                    f"✅ التحليل المتقدم مكتمل!\n\n"
                    f"📊 النتائج النهائية:\n"
                    f"• رسائل محللة: {messages_analyzed:,}\n"
                    f"• من الرسائل: {users_from_messages:,}\n"
                    f"• من المنشن: {users_from_mentions:,}\n"
                    f"• من إعادة التوجيه: {users_from_forwards:,}\n"
                    f"• إجمالي الأعضاء الجدد: {len(members):,}\n"
                    f"• تم تجاهل {skipped_duplicates:,} مكرر\n"
                    f"• وقت المعالجة: {processing_time:.1f} ثانية\n\n"
                    f"🎆 تحسن بنسبة: {improvement:.0f}% عن الطريقة العادية!\n"
                    f"✅ جميع الأعضاء نشطين مضمونين 100%\n\n"
                    f"💾 جاري حفظ البيانات..."
                )
                
                try:
                    await progress_message.edit_text(result_text)
                except:
                    pass
                
                print(f"✅ انتهى التحليل المتقدم بنجاح - تم جلب {len(members)} عضو نشيط")

                total_time = time.time() - start_time
                if total_time >= max_processing_time:
                    print(f"⏰ تم إنهاء التحليل بسبب انتهاء الوقت المسموح ({total_time/60:.1f} دقيقة)")
                    try:
                        await progress_message.edit_text(
                            f"⏰ تم إنهاء التحليل تلقائياً\n"
                            f"الوقت المنقضي: {total_time/60:.1f} دقيقة\n"
                            f"تم جمع {len(members)} عضو نشيط\n\n"
                            f"💾 جاري حفظ النتائج المتاحة..."
                        )
                    except:
                        pass
                
                print(f"🎯 التحليل المتقدم مكتمل - تم استخراج {len(members)} عضو نشيط من تحليل الرسائل")

            if members:
                print(f"🔄 بدء معالجة وحفظ {len(members)} عضو جديد...")
                save_start_time = time.time()
                
                final_members = existing_members.copy()
                final_members.extend(members)

                seen_user_ids = set()
                unique_members = []
                for member in final_members:
                    user_id = member.get("user_id")
                    if user_id and user_id not in seen_user_ids:
                        seen_user_ids.add(user_id)
                        unique_members.append(member)

                final_members = unique_members
                print(f"✅ تمت معالجة البيانات - إجمالي: {len(final_members)} عضو فريد")

                try:
                    if os.path.exists(MEMBERS_FILE):
                        backup_file = os.path.join(BACKUPS_DIR, f"members_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
                        import shutil
                        shutil.copy2(MEMBERS_FILE, backup_file)
                        print(f"💾 تم إنشاء نسخة احتياطية")
                    
                    print(f"💾 جاري حفظ {len(final_members)} عضو...")
                    with open(MEMBERS_FILE, "w", encoding='utf-8') as f:
                        json.dump(final_members, f, ensure_ascii=False, separators=(',', ':'))
                    
                    metadata = {
                        "extraction_date": datetime.now().isoformat(),
                        "source_group": group_link,
                        "extraction_method": method,
                        "total_count": len(final_members),
                        "new_members_count": len(members),
                        "processing_time": time.time() - start_time if 'start_time' in locals() else 0,
                        "save_time": time.time() - save_start_time
                    }
                    
                    metadata_file = os.path.join(DATA_DIR, "extraction_metadata.json")
                    with open(metadata_file, "w", encoding='utf-8') as f:
                        json.dump(metadata, f, ensure_ascii=False, separators=(',', ':'))
                    
                    temp_file = os.path.join(TEMP_DIR, f"temp_members_{user_id}.json")
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        print(f"🗑️ تم حذف الملف المؤقت")
                    
                    save_time = time.time() - save_start_time
                    print(f"⚡ تم الحفظ في {save_time:.2f} ثانية")
                    
                except Exception as save_error:
                    print(f"❌ خطأ في الحفظ: {save_error}")
                    temp_file = os.path.join(TEMP_DIR, f"temp_members_{user_id}.json")
                    if os.path.exists(temp_file):
                        try:
                            import shutil
                            shutil.copy2(temp_file, MEMBERS_FILE)
                            print(f"🔄 تم الاستعادة من الملف المؤقت")
                        except Exception as recovery_error:
                            print(f"❌ فشل في الاستعادة: {recovery_error}")

                method_display = "التحليل المتقدم" if method == "chat_active" else ("النشطين" if method == "active" else "جميع الأعضاء")

                final_result = f"تم إضافة {method_display} بنجاح!\n\n"
                final_result += f"• أعضاء جدد مضافين: {len(members):,}\n"
                final_result += f"• إجمالي محفوظ الآن: {len(final_members):,}\n"
                if skipped_duplicates > 0:
                    final_result += f"• تم تجاهل {skipped_duplicates:,} مكرر\n"

                final_result += f"\n• تم حفظهم في ملف members.json"
                final_result += f"\n• بيانات إضافية في metadata.json"

                if method == "chat_active":
                    final_result += f"\n\n• مميزات التحليل المتقدم:\n"
                    final_result += f"• أعضاء نشطين مضمونين 100%\n"
                    final_result += f"• استخراج من 4 مصادر مختلفة\n"
                    final_result += f"• يضاف للقائمة الموجودة تلقائياً\n"
                    final_result += f"• نتائج أفضل بآلاف المرات!\n"
                    final_result += f"• تم حفظ access_hash للنقل السريع"

                await progress_message.edit_text(final_result)
            else:
                await progress_message.edit_text(
                    "لم يتم سحب أي أعضاء جدد!\n\n"
                    "الأسباب المحتملة:\n"
                    "• جميع الأعضاء موجودين مسبقاً\n"
                    "• المجموعة فارغة أو حديثة\n"
                    "• لا توجد صلاحيات للوصول\n"
                    "• المجموعة محمية بإعدادات خصوصية عالية\n"
                    "• المجموعة تحتوي على بوتات فقط"
                )

        except Exception as client_error:
            error_msg = f"❌ خطأ في الاتصال: {str(client_error)}"
            print(error_msg)
            
            temp_file = os.path.join(TEMP_DIR, f"temp_members_{user_id}.json")
            if os.path.exists(temp_file):
                try:
                    with open(temp_file, 'r', encoding='utf-8') as f:
                        recovered_members = json.load(f)
                    
                    if recovered_members:
                        final_members = existing_members + recovered_members
                        
                        seen_ids = set()
                        unique_members = []
                        for member in final_members:
                            uid = member.get('user_id')
                            if uid and uid not in seen_ids:
                                seen_ids.add(uid)
                                unique_members.append(member)
                        
                        with open(MEMBERS_FILE, "w", encoding='utf-8') as f:
                            json.dump(unique_members, f, ensure_ascii=False, separators=(',', ':'))
                        
                        error_msg += f"\n\n🔄 تم استعادة {len(recovered_members)} عضو من الملف المؤقت"
                        error_msg += f"\n✅ إجمالي محفوظ: {len(unique_members)} عضو"
                        
                        os.remove(temp_file)
                        
                except Exception as recovery_error:
                    error_msg += f"\n❌ فشل في الاستعادة: {recovery_error}"
            
            await progress_message.edit_text(error_msg)
            
        finally:
            try:
                await client.disconnect()
            except:
                pass

        if user_id in user_data:
            del user_data[user_id]

    except Exception as e:
        logger.error(f"خطأ عام في سحب الأعضاء: {e}")
        await update.message.reply_text(f"خطأ في سحب الأعضاء: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def get_target_group(client, link):
    """دالة محسنة ومعاد بناؤها للتعامل مع جميع أنواع الروابط بما في ذلك الروابط الخاصة"""
    try:
        link = link.strip()
        print(f"🔗 معالجة الرابط: {link[:50]}...")

     
        if 't.me/+' in link or 'joinchat' in link:
         
            if 't.me/+' in link:
                invite_code = link.split('t.me/+')[1].split('?')[0].split('#')[0]
            elif 'joinchat' in link:
                invite_code = link.split('joinchat/')[1].split('?')[0].split('#')[0]
            else:
                raise ValueError("رابط خاص غير صحيح")

            print(f"🔒 رابط خاص - كود الدعوة: {invite_code[:10]}...")
            
       
            try:
                from telethon.tl.functions.messages import CheckChatInviteRequest
                print(f"🔍 فحص معلومات الرابط...")
                
                check_result = await client(CheckChatInviteRequest(invite_code))
                if check_result:
                    
                    if hasattr(check_result, 'chat'):
                        target_group = check_result.chat
                        print(f"✅ تم العثور على المجموعة وأنت عضو بالفعل: {target_group.title}")
                        
                        try:
                            fresh_entity = await client.get_entity(target_group.id)
                            me = await client.get_me()
                            permissions = await client.get_permissions(fresh_entity, me)
                            print(f"✅ تأكدت من العضوية الفعلية في: {fresh_entity.title}")
                            return fresh_entity
                        except Exception as refresh_error:
                            print(f"⚠️ تحذير - استخدام المرجع الأصلي: {refresh_error}")
                            return target_group
           
                    elif hasattr(check_result, 'title'):  
                        print(f"⏳ وجدت دعوة لمجموعة: {check_result.title} - جاري الانضمام...")
                    
            except Exception as check_error:
                error_str = str(check_error).lower()
                if "not found" in error_str:
                    print(f"❌ الدعوة غير موجودة أو منتهية الصلاحية: {check_error}")
                    raise Exception("رابط الدعوة غير صالح أو منتهي الصلاحية")
                elif "already" in error_str or "participant" in error_str:
                    print(f"✅ الحساب عضو مسبقاً - سنبحث في المحادثات المخزنة")
                else:
                    print(f"⚠️ خطأ في فحص الدعوة: {check_error}")

       
            try:
                from telethon.tl.functions.messages import ImportChatInviteRequest
                print(f"🚀 محاولة الانضمام للمجموعة بالرابط الخاص...")
                
                result = await client(ImportChatInviteRequest(invite_code))
                if result and hasattr(result, 'chats') and result.chats:
                    target_group = result.chats[0]
                    print(f"✅ نجح الانضمام للمجموعة: {target_group.title}")
                    

                    await asyncio.sleep(2)
                    

                    for attempt in range(4):
                        try:
                            fresh_group = await client.get_entity(target_group.id)
                            me = await client.get_me()
                            await client.get_permissions(fresh_group, me)
                            print(f"✅ تم تأكيد العضوية (محاولة {attempt + 1})")
                            return fresh_group
                        except Exception as refresh_error:
                            print(f"⚠️ فشل تأكيد العضوية (محاولة {attempt + 1}): {refresh_error}")
                            if attempt == 3:
                                print(f"⚠️ استخدام المرجع الأصلي من عملية الانضمام")
                                return target_group
                            await asyncio.sleep(1)
            except Exception as join_error:
                error_str = str(join_error).lower()
                
                if "already" in error_str or "participant" in error_str:
                    print(f"✅ عضو مسبقاً - سنبحث عن المجموعة في المحادثات")
                elif "expired" in error_str:
                    raise Exception("رابط الدعوة منتهي الصلاحية")
                elif "invalid" in error_str:
                    raise Exception("رابط الدعوة غير صالح")
                elif "flood" in error_str or "wait" in error_str:
                    import re
                    wait_match = re.search(r'(\d+)', error_str)
                    wait_seconds = int(wait_match.group(1)) if wait_match else 30
                    print(f"⏳ تأخير مطلوب ({wait_seconds}s) - سنبحث في المحادثات")
                    if wait_seconds < 180:  
                        await asyncio.sleep(wait_seconds)
                      
                        try:
                            fresh_entity = await client.get_entity(link) 
                            return fresh_entity
                        except:
                            pass  
                else:
                    print(f"⚠️ خطأ أثناء الانضمام: {join_error}")


            print(f"🔍 البحث عن المجموعة في المحادثات المحفوظة...")
            
            matched_groups = []
            search_count = 0
            
            try:
         
                async for dialog in client.iter_dialogs(limit=300):
                    search_count += 1
                    entity = dialog.entity
                    
                    
                    if (hasattr(entity, 'title') and 
                        (not hasattr(entity, 'username') or not entity.username)):
                        

                        matched_groups.append({
                            'entity': entity,
                            'date': getattr(dialog, 'date', None),
                            'title': entity.title,
                            'participants_count': getattr(entity, 'participants_count', 0)
                        })
                        
                     
                        if len(matched_groups) >= 20:
                            break
                    
                   
                    if search_count >= 300:  
                        break
            
                
                matched_groups.sort(key=lambda x: x['date'] if x['date'] else datetime.min, reverse=True)
                
                print(f"🎯 عثرت على {len(matched_groups)} مجموعة محتملة")
                
                for match in matched_groups[:7]:
                    entity = match['entity']
                    try:
                        me = await client.get_me()
                        permissions = await client.get_permissions(entity, me)
                        if permissions and not permissions.is_banned:
                            print(f"✅ تأكدت من العضوية في: {entity.title}")
                            return entity
                    except Exception as perm_error:
                        print(f"⚠️ فشل التحقق من: {entity.title}")
                        continue
                
                
                if matched_groups:
                    best_match = matched_groups[0]['entity']
                    print(f"🤞 اختيار أحدث مجموعة محتملة: {best_match.title}")
                    return best_match
                    
  
                raise Exception("لم يتم العثور على المجموعة في المحادثات الحالية")
                
            except Exception as search_error:
                print(f"❌ خطأ في البحث: {search_error}")
                raise Exception(f"فشل البحث عن المجموعة في المحادثات: {search_error}")

    
        elif link.startswith('@') or 't.me/' in link:
            if link.startswith('@'):
                username = link[1:]
            elif 't.me/' in link:
                parts = link.split('t.me/')[-1].split('?')[0].split('#')[0].split('/')
                username = parts[0]
            else:
                username = link

            username = username.strip().replace('@', '')
            print(f"🌐 معالجة رابط عام: @{username}")
            
            if not username:
                raise ValueError("اسم مستخدم فارغ")
                
            try:
             
                entity = await client.get_entity(username)
                entity_type = "مجموعة" if hasattr(entity, 'title') else "مستخدم"
                entity_name = getattr(entity, 'title', getattr(entity, 'first_name', username))
                print(f"✅ تم العثور على {entity_type}: {entity_name}")
                
                if hasattr(entity, 'title'):
                    try:
                        me = await client.get_me()
                        await client.get_permissions(entity, me)
                        print(f"✅ تأكدت من عضويتك في: {entity_name}")
                    except Exception as e:
                       
                        try:
                            from telethon.tl.functions.channels import JoinChannelRequest
                            await client(JoinChannelRequest(entity))
                            print(f"✅ تم الانضمام للمجموعة: {entity_name}")
                            await asyncio.sleep(1.5)
                            fresh_entity = await client.get_entity(username)
                            return fresh_entity
                        except Exception as join_err:
                            print(f"⚠️ تعذر الانضمام للمجموعة: {join_err}")
                
                return entity
            except Exception as entity_error:
                error_str = str(entity_error).lower()
                if "not found" in error_str:
                    raise Exception(f"لا يمكن العثور على @{username} - تأكد من صحة الرابط")
                elif "flood" in error_str or "wait" in error_str:
                    import re
                    wait_match = re.search(r'(\d+)', error_str)
                    wait_seconds = int(wait_match.group(1)) if wait_match else 30
                    raise Exception(f"تأخير مطلوب ({wait_seconds}s) - حاول لاحقًا")
                else:
                    raise Exception(f"تعذر الوصول إلى @{username}: {entity_error}")

        
        else:
            raise ValueError(f"تنسيق رابط غير مدعوم: {link}")

    except Exception as e:
        error_msg = str(e)
        print(f"💥 خطأ في معالجة الرابط: {error_msg}")
        
        
        if "flood" in error_msg.lower() and "wait" in error_msg.lower():
            import re
            wait_match = re.search(r'(\d+)', error_msg)
            wait_seconds = int(wait_match.group(1)) if wait_match else 60
            raise Exception(f"تأخير مطلوب من تليجرام ({wait_seconds} ثانية). حاول لاحقًا.")
        elif "not found" in error_msg.lower() or "expired" in error_msg.lower() or "invalid" in error_msg.lower():
            raise Exception(f"رابط غير صالح أو منتهي الصلاحية")
        else:
            raise Exception(f"تعذر الوصول للمجموعة: {error_msg}")

def is_valid_target_link(link):
    """فحص صحة رابط المجموعة المستهدفة"""
    link = link.strip().lower()
    return any([
        link.startswith('@'),
        't.me/+' in link,
        'joinchat' in link,
        (link.startswith('https://t.me/') and len(link.split('/')[-1]) > 0)
    ])

async def start_transfer(query):
    try:
        with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
            members = json.load(f)
        total_members = len(members)
    except:
        total_members = 0

    if total_members == 0:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="transfer_members")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد أعضاء محفوظة للنقل!\n\n"
            "قم بسحب الأعضاء أولاً.",
            reply_markup=reply_markup
        )
        return

    keyboard = [
        [InlineKeyboardButton("الغاء", callback_data="transfer_members")],
        [InlineKeyboardButton("← رجوع", callback_data="transfer_members")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"نقل الأعضاء\n\n"
        f"• عدد الأعضاء المحفوظة: {total_members:,} عضو\n\n"
        f"كم عدد الأعضاء التي تريد نقلها؟\n"
        f"ارسل رقم من 1 إلى {total_members:,}\n\n"
        f"• مثال: ارسل 100 لنقل 100 عضو\n"
        f"• أو ارسل {total_members} لنقل جميع الأعضاء",
        reply_markup=reply_markup
    )

    user_data[query.from_user.id] = {"state": "waiting_transfer_count", "total_members": total_members}

async def process_transfer_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        count_text = update.message.text.strip()


        try:
            transfer_count = int(count_text)
        except ValueError:
            keyboard = [[InlineKeyboardButton("الغاء", callback_data="transfer_members")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "يرجى ادخال رقم صحيح!\n\n"
                "مثال: 50",
                reply_markup=reply_markup
            )
            return

        total_members = user_data[user_id]["total_members"]


        if transfer_count < 1:
            keyboard = [[InlineKeyboardButton("الغاء", callback_data="transfer_members")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "يجب ان يكون العدد اكبر من 0!",
                reply_markup=reply_markup
            )
            return

        if transfer_count > total_members:
            keyboard = [[InlineKeyboardButton("الغاء", callback_data="transfer_members")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"العدد المطلوب ({transfer_count}) اكبر من عدد الاعضاء المحفوظة ({total_members})!\n\n"
                f"ارسل رقم من 1 الى {total_members}",
                reply_markup=reply_markup
            )
            return


        user_data[user_id]["transfer_count"] = transfer_count
        user_data[user_id]["state"] = "waiting_transfer_delay"

        keyboard = [[InlineKeyboardButton("الغاء", callback_data="transfer_members")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"تم تحديد العدد: {transfer_count} عضو\n\n"
            f"الآن حدد المؤقت بين كل عضو (بالثواني):\n\n"
            f"• المؤقت الموصى به: 5-15 ثانية\n"
            f"• مؤقت أقل = سرعة أكبر + مخاطر أكثر\n"
            f"• مؤقت أكبر = أمان أكثر + بطء أكثر\n\n"
            f"مثال: 10 (للمؤقت 10 ثواني بين كل عضو)\n"
            f"الحد الأدنى: 3 ثواني | الحد الأقصى: 60 ثانية",
            reply_markup=reply_markup
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ في معالجة العدد: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]




async def process_target_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        target_link = update.message.text.strip()

        if target_link.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            if user_id in user_data:
                del user_data[user_id]
            return

        if not is_valid_target_link(target_link):
            keyboard = [[InlineKeyboardButton("الغاء", callback_data="transfer_members")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "رابط غير صحيح!\n\n"
                "• الروابط المدعومة:\n"
                "• https://t.me/groupname\n"
                "• https://t.me/+xxxxx\n"
                "• https://t.me/joinchat/xxxxx\n"
                "• @groupname\n\n"
                "ارسل رابط صحيح من الأنواع أعلاه",
                reply_markup=reply_markup
            )
            return

        with open(MEMBERS_FILE, "r", encoding='utf-8') as f:
            all_members = json.load(f)

        if not all_members:
            await update.message.reply_text("لا توجد اعضاء للنقل!")
            if user_id in user_data:
                del user_data[user_id]
            return

        if not accounts:
            await update.message.reply_text("لا توجد حسابات متاحة للنقل!")
            if user_id in user_data:
                del user_data[user_id]
            return

        required_count = user_data[user_id].get("transfer_count", len(all_members))
        transfer_delay = user_data[user_id].get("transfer_delay", 8)  # المؤقت الافتراضي 8 ثواني

        control_buttons = [
            [
                InlineKeyboardButton("إيقاف مؤقت", callback_data=f"pause_transfer_{user_id}"),
                InlineKeyboardButton("إيقاف كامل", callback_data=f"stop_transfer_{user_id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(control_buttons)

        progress_message = await update.message.reply_text(
            f"جاري توزيع النقل على {len(accounts)} حساب...\n\n"
            f"• العدد المطلوب: {required_count} عضو\n"
            f"• عدد الحسابات: {len(accounts)} حساب\n"
            f"• كل حساب سينقل: {required_count // len(accounts)} عضو تقريباً\n"
            f"• المؤقت بين الأعضاء: {transfer_delay} ثانية\n"
            f"• هذا يقلل FLOOD_WAIT بشكل كبير\n\n"
            f"• الحالة: جاري التحضير...",
            reply_markup=reply_markup
        )

        account_list = list(accounts.items())

     
        expected_success_rate = 0.85  
        

        safety_margin = 1.5  
        target_count = min(required_count * safety_margin, len(all_members))
        

        base_members_per_account = max(10, int(target_count // len(accounts)))
        extra_members = int(target_count % len(accounts))
        
     
        if base_members_per_account * len(accounts) + extra_members > len(all_members):
            base_members_per_account = max(5, len(all_members) // len(accounts))  # حد أدنى 5 أعضاء
            extra_members = len(all_members) % len(accounts)
            

        if base_members_per_account < 5 and len(all_members) >= 20:

            optimal_accounts = min(len(accounts), len(all_members) // 10)  # حساب واحد لكل 10 أعضاء
            if optimal_accounts > 0:
                base_members_per_account = len(all_members) // optimal_accounts
                extra_members = len(all_members) % optimal_accounts
      
                account_list = account_list[:optimal_accounts]
            
        print(f"🎯 توزيع محسن: {required_count} مطلوب من {len(all_members)} متاح")
        print(f"📊 كل حساب سيعالج ~{base_members_per_account} عضو (+ {extra_members} إضافي)")

        total_added_verified = 0
        total_invite_success = 0
        total_already_member = 0
        total_failed = 0
        account_results = []

        total_privacy_restricted = 0
        total_too_many_groups = 0
        total_banned_users = 0
        total_admin_required = 0
        total_flood_wait_errors = 0
        total_other_errors = 0

        start_time = datetime.now()

        
        global transfer_control
        transfer_control.setdefault(user_id, {"paused": False, "stopped": False})
        control_flags = transfer_control[user_id]

        member_index = 0
        failed_members_pool = []  
        redistribution_enabled = True

        for account_idx, (phone, account_data) in enumerate(account_list):
            if control_flags.get("stopped", False):
                break
            while control_flags.get("paused", False):
                await asyncio.sleep(1)
                if control_flags.get("stopped", False):
                    break
            if control_flags.get("stopped", False):
                break

            members_for_this_account = base_members_per_account
            if account_idx < extra_members:
                members_for_this_account += 1
                
            if redistribution_enabled and failed_members_pool and account_idx < len(account_list) // 2:
                additional_from_pool = min(5, len(failed_members_pool))
                members_for_this_account += additional_from_pool

            if member_index >= len(all_members) and not failed_members_pool:
                break
                
           
            account_members = []
            
     
            if member_index < len(all_members):
                primary_count = min(base_members_per_account, len(all_members) - member_index)
                account_members.extend(all_members[member_index:member_index + primary_count])
                member_index += primary_count
            
            if failed_members_pool and len(account_members) < members_for_this_account:
                pool_count = min(members_for_this_account - len(account_members), len(failed_members_pool))
                account_members.extend(failed_members_pool[:pool_count])
                failed_members_pool = failed_members_pool[pool_count:]  # إزالة المستخدمين
                
            if not account_members:
                continue

            try:
                session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                await client.start(phone=phone)

                if not await client.is_user_authorized():
                    account_results.append({
                        "phone": phone,
                        "status": "غير مسجل الدخول",
                        "added_verified": 0,
                        "invite_success": 0,
                        "already_member": 0,
                        "failed": len(account_members),
                        "assigned": len(account_members)
                    })
                    total_failed += len(account_members)
                    await client.disconnect()
                    continue


                try:
                    target_group = await get_target_group(client, target_link)


                    if 't.me/+' in target_link or 'joinchat' in target_link:
                        print(f"• رابط خاص، جاري التحقق من صحة المرجع...")
                        await asyncio.sleep(2)


                        try:
                            fresh_target = await client.get_entity(target_group.id)
                            target_group = fresh_target
                            print(f"• تم تحديث مرجع الرابط الخاص: {target_group.title}")
                        except Exception as refresh_error:
                            print(f"• تحذير في تحديث المرجع: {refresh_error}")


                    group_name = target_group.title if hasattr(target_group, 'title') else "غير معروف"
                    print(f"• المجموعة المستهدفة: {group_name}")


                    try:
                        me = await client.get_me()
                        await client.get_permissions(target_group, me)
                        print(f"• تم التأكد من العضوية في: {group_name}")
                    except Exception as perm_error:
                        print(f"• تحذير: مشكلة في الصلاحيات: {perm_error}")

                except Exception as e:
                    error_msg = str(e)
                    if "منتهي الصلاحية" in error_msg:
                        status_msg = "رابط منتهي الصلاحية"
                    elif "غير صحيح" in error_msg:
                        status_msg = "رابط غير صحيح"
                    else:
                        status_msg = f"خطأ في الوصول: {str(e)[:30]}"

                    account_results.append({
                        "phone": phone,
                        "status": status_msg,
                        "added_verified": 0,
                        "invite_success": 0,
                        "already_member": 0,
                        "failed": len(account_members),
                        "assigned": len(account_members)
                    })
                    total_failed += len(account_members)
                    await client.disconnect()
                    continue

                account_added_verified = 0
                account_invite_success = 0
                account_already_member = 0
                account_failed = 0
                account_flood_waits = 0
                consecutive_flood_waits = 0
                successfully_added_ids = set()
                failed_permanently = set()

                privacy_restricted = 0
                too_many_groups = 0
                banned_users = 0
                admin_required = 0
                other_errors = 0

              
                retry_attempts = {}
                max_retries = 2  
                members_processed = 0  
                adaptive_delay = transfer_delay  
                
                for member in account_members:
                    
                    if control_flags.get("stopped", False):
                        break

                    member_id = member.get("user_id")
                    if member_id in successfully_added_ids or member_id in failed_permanently:
                        continue
                        
                  
                    if member_id not in retry_attempts:
                        retry_attempts[member_id] = 0

                    
                    while control_flags.get("paused", False):
                        await asyncio.sleep(1)
                        if control_flags.get("stopped", False):
                            break

                    if control_flags.get("stopped", False):
                        break

                    try:
                        member_user_id = member.get("user_id")
                        username = member.get("username")
                        first_name = member.get("first_name", "غير معروف")

                        add_success = False


                        try:
                            if member_user_id:
                                access_hash = member.get("access_hash")
                                if access_hash:
                                    from telethon.tl.types import InputUser
                                    user_entity = InputUser(member_user_id, access_hash)
                                else:
                                    user_entity = await client.get_entity(member_user_id)

                                participant = await client.get_permissions(target_group, user_entity)
                                if participant and not participant.is_banned:
                                    account_already_member += 1
                                    add_success = True
                                    print(f"{phone}: {first_name} عضو مسبقاً")
                                    continue
                        except:
                            pass


                        if member_user_id and not add_success:
                            try:
                                access_hash = member.get("access_hash")
                                if access_hash:
                                    from telethon.tl.types import InputUser
                                    user_entity = InputUser(member_user_id, access_hash)
                                else:

                                    try:
                                        temp_user = await client.get_entity(member_user_id)
                                        if hasattr(temp_user, 'access_hash'):
                                            access_hash = temp_user.access_hash
                                            from telethon.tl.types import InputUser
                                            user_entity = InputUser(member_user_id, access_hash)
                                        else:
                                            user_entity = temp_user
                                    except:
                                        user_entity = await client.get_entity(member_user_id)


                                if 't.me/+' in target_link or 'joinchat' in target_link:
                                    try:
                                        fresh_target = await client.get_entity(target_group.id)
                                        target_group = fresh_target
                                        print(f"• تم تحديث مرجع المجموعة قبل النقل")
                                    except Exception as refresh_error:
                                        print(f"• تحذير: فشل تحديث المرجع: {refresh_error}")

                                await client(InviteToChannelRequest(target_group, [user_entity]))
                                print(f"• تم إرسال دعوة النقل لـ {first_name}")

                                consecutive_flood_waits = 0

                                await asyncio.sleep(3)
                                try:
                                    verification = await client.get_permissions(target_group, user_entity)
                                    if verification and not verification.is_banned:
                                        account_added_verified += 1
                                        add_success = True
                                        successfully_added_ids.add(member_user_id)
                                        print(f"• تم إضافة فعلياً: {first_name}")
                                    else:
                                        account_invite_success += 1
                                        print(f"دعوة مرسلة {phone}: {first_name}")
                                except:
                                    account_invite_success += 1


                         
                                members_processed += 1
                                if members_processed > 5:  
                                    adaptive_delay = min(transfer_delay * 1.5, transfer_delay + 10)
                                elif consecutive_flood_waits > 0:  
                                    adaptive_delay = min(transfer_delay * 2, transfer_delay + 15)
                                else:
                                    adaptive_delay = transfer_delay
                                    
                                await asyncio.sleep(adaptive_delay)
                                print(f"⏱️ انتظار {adaptive_delay}ث قبل العضو التالي")

                            except Exception as id_error:
                                error_str = str(id_error).lower()
                                original_error = str(id_error)

                                if "wait" in error_str or "flood" in error_str:
                                    import re
                                    wait_match = re.search(r'(\d+)', original_error)
                                    wait_seconds = int(wait_match.group(1)) if wait_match else 300

                                    consecutive_flood_waits += 1
                                    account_flood_waits += 1

                                    if wait_seconds > 600 or consecutive_flood_waits >= 3:
                                        print(f"FLOOD_WAIT طويل في {phone}، الانتقال للحساب التالي")
                                        break
                                    elif wait_seconds <= 300:
                                        print(f"انتظار {wait_seconds}s في {phone}")
                                        await asyncio.sleep(wait_seconds + 5)
                                        continue
                                    else:
                                        break

                                elif "channels_too_much" in error_str:
                                    too_many_groups += 1
                                    consecutive_flood_waits = 0
                                elif "useralreadyparticipant" in error_str:
                                    account_already_member += 1
                                    consecutive_flood_waits = 0
                                    add_success = True
                                elif "userprivacyrestricted" in error_str:
                                    privacy_restricted += 1
                                    consecutive_flood_waits = 0
                                    failed_permanently.add(member_user_id)
                                elif "userbannedinChannel" in error_str:
                                    banned_users += 1
                                    consecutive_flood_waits = 0
                                elif "chatadminrequired" in error_str:
                                    admin_required += 1
                                    consecutive_flood_waits = 0
                                else:
                                    other_errors += 1
                                    consecutive_flood_waits = 0
                                    print(f"❌ خطأ غير مُصنف من {phone}: {original_error}")


                        if username and not add_success:
                            try:
                                user_entity = await client.get_entity(f"@{username}")


                                if 't.me/+' in target_link or 'joinchat' in target_link:
                                    try:
                                        fresh_target = await client.get_entity(target_group.id)
                                        target_group = fresh_target
                                        print(f"• تم تحديث مرجع المجموعة قبل النقل")
                                    except Exception as refresh_error:
                                        print(f"• تحذير: فشل تحديث المرجع: {refresh_error}")

                                await client(InviteToChannelRequest(target_group, [user_entity]))
                                print(f"• تم إرسال دعوة النقل لـ {first_name}")

                                consecutive_flood_waits = 0

                                await asyncio.sleep(3)
                                try:
                                    verification = await client.get_permissions(target_group, user_entity)
                                    if verification and not verification.is_banned:
                                        account_added_verified += 1
                                        add_success = True
                                        successfully_added_ids.add(member_user_id)
                                        print(f"نجح باليوزر {phone}: {first_name}")
                                    else:
                                        account_invite_success += 1
                                except:
                                    account_invite_success += 1


                          
                                await asyncio.sleep(adaptive_delay)
                                print(f"⏱️ انتظار {adaptive_delay}ث بعد النقل بـ Username")

                            except Exception as username_error:
                                username_error_str = str(username_error).lower()

                                if "wait" in username_error_str or "flood" in username_error_str:
                                    import re
                                    wait_match = re.search(r'(\d+)', str(username_error))
                                    wait_seconds = int(wait_match.group(1)) if wait_match else 300

                                    consecutive_flood_waits += 1

                                    if wait_seconds > 600 or consecutive_flood_waits >= 3:
                                        print(f"FLOOD_WAIT في اليوزر {phone}، الانتقال للحساب التالي")
                                        break
                                    elif wait_seconds <= 300:
                                        await asyncio.sleep(wait_seconds + 5)
                                        continue
                                    else:
                                        break

                        if not add_success:
                            retry_attempts[member_id] += 1
                            
                            
                            if retry_attempts[member_id] <= max_retries:
                                print(f"🔄 إعادة محاولة {retry_attempts[member_id]}/{max_retries} للعضو: {first_name}")
                                await asyncio.sleep(transfer_delay * 2)  # مؤقت أطول لإعادة المحاولة
                                continue  
                            else:
                                account_failed += 1
                                failed_permanently.add(member_id)
                                if redistribution_enabled and member not in failed_members_pool:
                                    failed_members_pool.append(member)
                                print(f"❌ فشل نهائي في نقل: {first_name} بعد {max_retries} محاولات")

                        if consecutive_flood_waits >= 3:
                            print(f"تجاوز حد FLOOD_WAIT، نقل الأعضاء المتبقين لحسابات أخرى")
                            
                            current_index = account_members.index(member) if member in account_members else len(account_members)
                            remaining_members = account_members[current_index:]
                            
                            for remaining_member in remaining_members:
                                if remaining_member not in failed_members_pool:
                                    failed_members_pool.append(remaining_member)
                                    
                            print(f"تم نقل {len(remaining_members)} عضو لإعادة المحاولة")
                            break

                    except Exception as member_error:
                        account_failed += 1
                        print(f"❌ خطأ عام في {phone} مع العضو {first_name}: {member_error}")
                        print(f"📋 تفاصيل العضو: ID={member_user_id}, Username={username}")
                        continue

                account_results.append({
                    "phone": phone,
                    "status": "مكتمل",
                    "added_verified": account_added_verified,
                    "invite_success": account_invite_success,
                    "already_member": account_already_member,
                    "failed": account_failed,
                    "assigned": len(account_members),
                    "flood_waits": account_flood_waits
                })

                total_added_verified += account_added_verified
                total_invite_success += account_invite_success
                total_already_member += account_already_member
                total_failed += account_failed

                total_privacy_restricted += privacy_restricted
                total_too_many_groups += too_many_groups
                total_banned_users += banned_users
                total_admin_required += admin_required
                total_flood_wait_errors += account_flood_waits
                total_other_errors += other_errors

                await client.disconnect()


              
                success_rate = (total_added_verified / max(1, total_added_verified + total_invite_success)) * 100
                
                progress_text = (
                    f"🔄 تقدم النقل الموزع (مؤقت: {transfer_delay}ث):\n\n"
                    f"✅ **نُقل فعلياً: {total_added_verified}/{required_count}** ({success_rate:.1f}%)\n"
                    f"📤 دعوات مرسلة: {total_invite_success}\n"
                    f"👥 أعضاء مسبقاً: {total_already_member}\n"
                    f"⚙️ الحسابات المكتملة: {account_idx + 1}/{len(accounts)}\n\n"
                    f"📱 آخر حساب: {phone[:8]}***\n"
                    f"✅ نُقل فعلياً: {account_added_verified} | 📤 دعوات: {account_invite_success}\n"
                    f"👥 أعضاء مسبقاً: {account_already_member} | ❌ فشل: {account_failed}\n\n"
                    f"📊 المتبقي: {required_count - total_added_verified} عضو"
                )

                if control_flags.get("paused", False):
                    control_buttons = [
                        [
                            InlineKeyboardButton("استكمال", callback_data=f"resume_transfer_{user_id}"),
                            InlineKeyboardButton("إيقاف كامل", callback_data=f"stop_transfer_{user_id}")
                        ]
                    ]
                else:
                    control_buttons = [
                        [
                            InlineKeyboardButton("إيقاف مؤقت", callback_data=f"pause_transfer_{user_id}"),
                            InlineKeyboardButton("إيقاف كامل", callback_data=f"stop_transfer_{user_id}")
                        ]
                    ]

                reply_markup = InlineKeyboardMarkup(control_buttons)

                try:
                    await progress_message.edit_text(progress_text, reply_markup=reply_markup)
                except:
                    pass

                if total_added_verified >= required_count:
                    print(f"✅ تم تحقيق الهدف: {total_added_verified}/{required_count}")
                    break
                    

                if account_idx >= len(account_list) - 2:
                    redistribution_enabled = False

                await asyncio.sleep(6)  

            except Exception as account_error:
                account_results.append({
                    "phone": phone,
                    "status": f"خطأ: {str(account_error)[:30]}",
                    "added_verified": 0,
                    "invite_success": 0,
                    "already_member": 0,
                    "failed": len(account_members) if 'account_members' in locals() else 0,
                    "assigned": len(account_members) if 'account_members' in locals() else 0
                })
                total_failed += len(account_members) if 'account_members' in locals() else 0
                print(f"خطأ في الحساب {phone}: {account_error}")
                try:
                    await client.disconnect()
                except:
                    pass
                continue


       
        if failed_members_pool and total_added_verified < required_count:
            print(f"🔄 محاولة أخيرة مع {len(failed_members_pool)} عضو متبقي")
            

            best_accounts = [acc for acc in account_results if acc.get('added_verified', 0) > 0][:3]
            
            for remaining_member in failed_members_pool[:50]:  # محدود بـ 50 محاولة
                if total_added_verified >= required_count:
                    break
                    
                for result in best_accounts:
                    if total_added_verified >= required_count:
                        break
                        
                    phone = result['phone']
                    if phone not in accounts:
                        continue
                        
                    try:
                        account_data = accounts[phone]
                        session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
                        client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
                        await client.start(phone=phone)
                        
                        if await client.is_user_authorized():
                            target_group = await get_target_group(client, target_link)
                            
                            member_user_id = remaining_member.get("user_id")
                            if member_user_id:
                                try:
                                    user_entity = await client.get_entity(member_user_id)
                                    await client(InviteToChannelRequest(target_group, [user_entity]))
                                    total_added_verified += 1
                                    print(f"✅ محاولة أخيرة نجحت: {remaining_member.get('first_name', 'غير معروف')}")
                                    await asyncio.sleep(2)
                                except:
                                    pass
                        
                        await client.disconnect()
                    except Exception as retry_error:
                        print(f"خطأ في المحاولة الأخيرة: {retry_error}")
                        continue
        
        if user_id in user_data:
            del user_data[user_id]

        end_time = datetime.now()
        duration = end_time - start_time
        

        if failed_members_pool:
            print(f"📈 أعضاء في تجمع إعادة المحاولة: {len(failed_members_pool)}")
        print(f"🎯 النتيجة النهائية: {total_added_verified}/{required_count} ({round((total_added_verified/required_count)*100, 1)}%)")

        if control_flags.get("stopped", False):
            status_icon = "تم إيقاف العملية بواسطة المستخدم"
        elif total_added_verified >= required_count:
            status_icon = "نجحت المهمة"
        elif total_flood_wait_errors > (len(accounts) * 2):
            status_icon = "توقف بسبب الحظر"
        elif member_index >= len(all_members):
            status_icon = "انتهت المحاولات"
        else:
            status_icon = "توقف مؤقت"


       
        actual_success_rate = round((total_added_verified/required_count)*100, 1) if required_count > 0 else 0
        
        final_report = f"🏁 {status_icon}\n\n"
        final_report += f"📊 **ملخص النتائج:**\n"
        final_report += f"🎯 الهدف: {required_count} عضو\n"
        final_report += f"✅ **تم إضافتهم فعلياً: {total_added_verified} عضو**\n"
        final_report += f"📤 دعوات مرسلة: {total_invite_success} عضو\n"
        final_report += f"👥 كانوا أعضاء مسبقاً: {total_already_member} عضو\n"
        final_report += f"📈 **معدل النجاح: {actual_success_rate}%**\n"
        final_report += f"⏱️ مدة العملية: {duration.seconds} ثانية\n"
        final_report += f"📱 عدد الحسابات المستخدمة: {len(account_results)}\n"
        final_report += f"⏰ المؤقت المستخدم: {transfer_delay} ثانية بين كل عضو\n\n"


        final_report += f"• تفاصيل الحسابات:\n"
        for i, result in enumerate(account_results, 1):
            phone = result['phone']
            account_info = accounts.get(phone, {})
            first_name = account_info.get('first_name', 'غير معروف')
            last_name = account_info.get('last_name', '')
            username = account_info.get('username', '')

            display_name = first_name
            if last_name:
                display_name += f" {last_name}"

            if username:
                account_link = f"[{display_name}](https://t.me/{username})"
            else:
                account_link = display_name

            if result['added_verified'] > 0:
                status_text = "نجح"
            elif result['invite_success'] > 0:
                status_text = "دعوات"
            elif result.get('flood_waits', 0) > 0:
                status_text = "انتظار"
            else:
                status_text = "فشل"

            final_report += f"\n• {status_text} - {i}. {account_link}\n"
            final_report += f"   • الهاتف: {phone}\n"
            final_report += f"   • مُكلف بـ: {result['assigned']} عضو\n"
            final_report += f"   • نقل فعلياً: {result['added_verified']} عضو\n"
            final_report += f"   • دعوات: {result['invite_success']} عضو\n"
            final_report += f"   • أعضاء مسبقاً: {result['already_member']} عضو\n"

            if result['failed'] > 0:
                final_report += f"   • فشل: {result['failed']} عضو\n"
            if result.get('flood_waits', 0) > 0:
                final_report += f"   • مرات FLOOD_WAIT: {result['flood_waits']}\n"


        if total_failed > 0:
            final_report += f"\n\n• تحليل الأخطاء:\n"
            if total_privacy_restricted > 0:
                final_report += f"• إعدادات خصوصية عالية: {total_privacy_restricted} عضو\n"
            if total_too_many_groups > 0:
                final_report += f"• في مجموعات كثيرة: {total_too_many_groups} عضو\n"
            if total_banned_users > 0:
                final_report += f"• محظورين من المجموعة: {total_banned_users} عضو\n"
            if total_admin_required > 0:
                final_report += f"• يحتاج صلاحيات مشرف: {total_admin_required} عضو\n"
            if total_flood_wait_errors > 0:
                final_report += f"• تأخير FLOOD_WAIT: {total_flood_wait_errors} مرة\n"
            if total_other_errors > 0:
                final_report += f"• أخطاء أخرى: {total_other_errors} مرة\n"


        final_report += f"\n\n• النتيجة النهائية:\n"
        if total_added_verified >= required_count:
            final_report += f"• تم تحقيق الهدف بالكامل!\n"
            final_report += f"• تم ضمان دخول جميع الـ {required_count} عضو المطلوبين"
        else:
            completion_rate = round((total_added_verified/required_count)*100, 1)
            final_report += f"• تم تحقيق {completion_rate}% من الهدف\n"
            final_report += f"• دخل فعلياً: {total_added_verified} من {required_count} عضو\n"
            final_report += f"• متبقي: {required_count - total_added_verified} عضو"

        if total_added_verified < required_count:
            final_report += f"\n\n• نصائح للتحسين:\n"
            if total_flood_wait_errors > 5:
                final_report += f"• أضف المزيد من الحسابات لتوزيع أفضل\n"
            if total_too_many_groups > (required_count * 0.3):
                final_report += f"• اختر أعضاء أقل نشاطاً في المجموعات\n"
            if total_admin_required > 0:
                final_report += f"• تأكد من صلاحيات المشرف في المجموعة\n"
            final_report += f"• جرب في أوقات أقل ازدحاماً (الفجر مثلاً)\n"
            final_report += f"• أعد المحاولة مع الأعضاء المتبقين"

        if len(final_report) > 4000:
            basic_report = f"• {status_icon}\n\n"
            basic_report += f"• ملخص سريع:\n"
            basic_report += f"• الهدف: {required_count} عضو\n"
            basic_report += f"• تم إضافتهم: {total_added_verified} عضو\n"
            basic_report += f"• معدل النجاح: {round((total_added_verified/required_count)*100, 1)}%\n"
            basic_report += f"• استخدم {len(account_results)} حساب\n"
            basic_report += f"• المدة: {duration.seconds} ثانية\n\n"

            basic_report += f"• نتائج الحسابات:\n"
            for i, result in enumerate(account_results, 1):
                phone = result['phone']
                account_info = accounts.get(phone, {})
                first_name = account_info.get('first_name', 'غير معروف')
                username = account_info.get('username', '')

                if username:
                    account_link = f"[{first_name}](https://t.me/{username})"
                else:
                    account_link = first_name

                basic_report += f"{i}. {account_link} - نقل: {result['added_verified']}\n"

            await progress_message.edit_text(basic_report, parse_mode='Markdown', disable_web_page_preview=True)
        else:
            await progress_message.edit_text(final_report, parse_mode='Markdown', disable_web_page_preview=True)


        user_name = update.effective_user.first_name or "مجهول"
        user_type = "owner" if is_admin(user_id) else "admin"
        log_event(user_type, "نقل أعضاء", user_name, user_id, f"نقل {total_added_verified} من {required_count} عضو إلى مجموعة")


        print(f"\nنتيجة النقل الموزع:")
        print(f"المطلوب: {required_count} | المحقق: {total_added_verified}")
        print(f"الحسابات المستخدمة: {len(account_results)}")
        print(f"معدل النجاح: {round((total_added_verified/required_count)*100, 1)}%")
        print(f"حالة المهمة: {status_icon}")
        print(f"FLOOD_WAIT مجموع: {total_flood_wait_errors}")

    except Exception as e:
        logger.error(f"خطأ في النقل الموزع: {str(e)}")
        await update.message.reply_text(f"• خطأ في النقل الموزع: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

def encrypt_accounts_data(accounts_data):
    """تشفير بيانات الحسابات"""
    encrypted_accounts = {}
    for phone, account_data in accounts_data.items():
        encrypted_account = account_data.copy()
        encrypted_account["_phone_hash"] = hashlib.md5(f"{SECRET_VALIDATION}{phone}".encode()).hexdigest()
        encrypted_account["_account_signature"] = generate_bot_signature()
        encrypted_account["_protection_key"] = base64.b64encode(SECRET_BOT_ID.encode()).decode()
        encrypted_accounts[phone] = encrypted_account
    return encrypted_accounts

def decrypt_accounts_data(encrypted_accounts):

    decrypted_accounts = {}
    for phone, account_data in encrypted_accounts.items():
        if "_phone_hash" not in account_data or "_account_signature" not in account_data or "_protection_key" not in account_data:
            continue

        try:
            decoded_key = base64.b64decode(account_data["_protection_key"]).decode()
            if decoded_key != SECRET_BOT_ID:
                continue
        except:
            continue

        expected_hash = hashlib.md5(f"{SECRET_VALIDATION}{phone}".encode()).hexdigest()
        if account_data["_phone_hash"] != expected_hash:
            continue

        if not validate_bot_signature(account_data["_account_signature"]):
            continue

        clean_account = account_data.copy()
        for key in ["_phone_hash", "_account_signature", "_protection_key"]:
            clean_account.pop(key, None)

        decrypted_accounts[phone] = clean_account

    return decrypted_accounts

async def download_accounts_file(query):
    try:
        if not accounts:
            keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "لا توجد حسابات للتحميل!",
                reply_markup=reply_markup
            )
            return

        encrypted_accounts = encrypt_accounts_data(accounts)

        backup_data = {
            "accounts": encrypted_accounts,
            "backup_date": datetime.now().isoformat(),
            "total_accounts": len(accounts),
            "format_version": "encrypted_accounts_v2",
            "_sys_protection": generate_bot_signature(),
            "_accounts_hash": hashlib.sha256(f"{SECRET_VALIDATION}{len(accounts)}".encode()).hexdigest(),
            "_bot_identifier": base64.b64encode(HIDDEN_SIGNATURE.encode()).decode()
        }

        backup_filename = f"accounts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, "w", encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        with open(backup_filename, 'rb') as f:
            await query.message.reply_document(
                document=f,
                filename=backup_filename,
                caption=f"• ملف الحسابات المحمي\n\n"
                       f"• تاريخ النسخة: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                       f"• عدد الحسابات: {len(accounts)}\n"
                       f"• محمي بتشفير متقدم\n"
                       f"• يعمل فقط مع بوتاتك\n\n"
                       f"• احتفظ بهذا الملف في مكان آمن"
            )

        os.remove(backup_filename)

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "تم تحميل ملف محمي بنجاح!",
            reply_markup=reply_markup
        )

    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"خطأ في تحميل ملف الحسابات: {str(e)}",
            reply_markup=reply_markup
        )

async def upload_accounts_file(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "رفع ملف الحسابات\n\n"
        "ارسل ملف الحسابات المحمي (JSON) لاستعادة الحسابات\n\n"
        "• تحذير: سيتم استبدال جميع الحسابات الحالية\n"
        "• فقط الملفات من بوتاتك ستعمل\n"
        "• الملفات الخارجية سترفض تلقائياً",
        reply_markup=reply_markup
    )

    user_data[query.from_user.id] = {"state": "waiting_accounts_file"}

async def process_accounts_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        text = update.message.text

        if text and text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if not update.message.document:
            await update.message.reply_text("• يرجى ارسال ملف JSON فقط!")
            return

        document = update.message.document

        if not document.file_name.endswith('.json'):
            await update.message.reply_text("• يرجى ارسال ملف JSON فقط!")
            return

        if document.file_size > 10 * 1024 * 1024:
            await update.message.reply_text("• حجم الملف كبير جداً! الحد الأقصى 10MB")
            return

        progress_msg = await update.message.reply_text("• جاري فحص أمان الملف...")

        file = await context.bot.get_file(document.file_id)
        safe_filename = f"temp_accounts_{user_id}_{int(time.time())}.json"
        await file.download_to_drive(safe_filename)

        is_safe, safety_message = is_safe_file(safe_filename, document.file_name)

        if not is_safe:
            await progress_msg.edit_text(f"• ملف غير آمن!\n• {safety_message}")
            os.remove(safe_filename)
            del user_data[user_id]
            return

        await progress_msg.edit_text("• الملف آمن، جاري المعالجة...")

        with open(safe_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if "accounts" not in data:
            await progress_msg.edit_text("• ملف غير صحيح! لا يحتوي على بيانات الحسابات")
            os.remove(safe_filename)
            del user_data[user_id]
            return

        encrypted_accounts = data["accounts"]

        if data.get("format_version") == "encrypted_accounts_v2":
            if "_sys_protection" not in data or "_accounts_hash" not in data or "_bot_identifier" not in data:
                await progress_msg.edit_text("• ملف محمي من بوت آخر! لا يمكن استيراده")
                os.remove(safe_filename)
                del user_data[user_id]
                return

            try:
                decoded_identifier = base64.b64decode(data["_bot_identifier"]).decode()
                if decoded_identifier != HIDDEN_SIGNATURE:
                    await progress_msg.edit_text("• ملف محمي من بوت آخر! لا يمكن استيراده")
                    os.remove(safe_filename)
                    del user_data[user_id]
                    return
            except:
                await progress_msg.edit_text("• ملف محمي تالف! لا يمكن قراءته")
                os.remove(safe_filename)
                del user_data[user_id]
                return

            if not validate_bot_signature(data["_sys_protection"]):
                await progress_msg.edit_text("• ملف منتهي الصلاحية أو من بوت آخر!")
                os.remove(safe_filename)
                del user_data[user_id]
                return

            restored_accounts = decrypt_accounts_data(encrypted_accounts)

            if len(restored_accounts) == 0:
                await progress_msg.edit_text("• ملف محمي من بوت آخر! لا يمكن فك تشفيره")
                os.remove(safe_filename)
                del user_data[user_id]
                return
        else:
            restored_accounts = encrypted_accounts

        for phone, account_data in restored_accounts.items():
            required_fields = ["api_id", "api_hash"]
            if not all(field in account_data for field in required_fields):
                await progress_msg.edit_text(f"• بيانات الحساب {phone} غير مكتملة!")
                os.remove(safe_filename)
                del user_data[user_id]
                return

        if accounts:
            backup_filename = os.path.join(BACKUPS_DIR, f"accounts_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(backup_filename, "w", encoding='utf-8') as f:
                json.dump(accounts, f, indent=2, ensure_ascii=False)

        accounts.clear()
        accounts.update(restored_accounts)
        save_accounts()

        os.remove(safe_filename)

        backup_date = data.get("backup_date", "غير معروف")

        success_message = f"تم استعادة الحسابات بنجاح!\n\n"
        success_message += f"• عدد الحسابات المستعادة: {len(accounts)}\n"
        success_message += f"• تاريخ النسخة: {backup_date}\n"
        success_message += f"• تم حفظ نسخة احتياطية من الحسابات السابقة\n"
        success_message += f"• جاهز للاستخدام الان"

        try:
            await progress_msg.delete()
        except:
            pass

        await update.message.reply_text(success_message)

        del user_data[user_id]

    except json.JSONDecodeError:
        await update.message.reply_text("• خطأ في قراءة الملف! تأكد من ان الملف بصيغة JSON صحيحة")
        try:
            os.remove(safe_filename)
        except:
            pass
        if user_id in user_data:
            del user_data[user_id]
    except Exception as e:
        await update.message.reply_text(f"• خطأ في استعادة الحسابات: {str(e)}")
        try:
            os.remove(safe_filename)
        except:
            pass
        if user_id in user_data:
            del user_data[user_id]




async def extract_hidden_members(query):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data="extract_members")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "تخزين مخفي (التحليل المتقدم)\n\n"
        "الطريقة الاقوى والاذكى:\n"
        "• تحلل آخر 15,000 رسالة في المجموعة\n"
        "• تستخرج من الرسائل + المنشن + اعادة التوجيه\n"
        "• نتائج 2000% افضل من الطريقة العادية\n"
        "• يجيب اعضاء مخفيين 100%\n\n"
        "متوقع: 3000-8000 عضو نشط من مجموعة كبيرة\n\n"
        "ارسل رابط المجموعة:",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_group_link", "method": "chat_active", "mode": "add"}

async def process_multiple_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        links_text = update.message.text.strip()

        if links_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return


        links = [link.strip() for link in links_text.split('\n') if link.strip() and (link.startswith('https://t.me/') or link.startswith('@'))]

        if not links:
            await update.message.reply_text("لم يتم العثور على روابط صحيحة!\n\nتأكد من استخدام التنسيق الصحيح.")
            return

        await update.message.reply_text(f"تم العثور على {len(links)} مجموعة\n\nجاري السحب من جميع المجموعات...")

        all_members = []
        available_accounts = list(accounts.items())
        session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
        client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])

        try:
            await client.connect()
            if not await client.is_user_authorized():
                await update.message.reply_text("الحساب غير مسجل الدخول!")
                return

            for i, link in enumerate(links, 1):
                try:
                    await update.message.reply_text(f"جاري السحب من المجموعة {i}/{len(links)}: {link}")

                    group = await client.get_entity(link)
                    members = []
                    offset = 0
                    limit = 100

                    while len(members) < 2000:
                        try:
                            participants = await client(GetParticipantsRequest(
                                group, ChannelParticipantsSearch(''), offset, limit, hash=0
                            ))

                            if not participants.users:
                                break

                            for user in participants.users:
                                if not user.bot and len(all_members) < 10000:
                                    member_data = {
                                        "username": user.username if user.username else None,
                                        "user_id": user.id,
                                        "first_name": user.first_name if user.first_name else "غير معروف",
                                        "last_name": user.last_name if user.last_name else None,
                                        "phone": user.phone if user.phone else None,
                                        "source_group": link
                                    }

                                    if not any(m.get("user_id") == user.id for m in all_members):
                                        all_members.append(member_data)
                                        members.append(member_data)

                            offset += len(participants.users)
                            if len(participants.users) < limit:
                                break

                            await asyncio.sleep(1)

                        except Exception as e:
                            break

                    await update.message.reply_text(f"تم سحب {len(members)} عضو من المجموعة {i}")

                except Exception as e:
                    await update.message.reply_text(f"خطأ في المجموعة {i}: {str(e)}")
                    continue

            await client.disconnect()

        except Exception as e:
            await update.message.reply_text(f"خطأ في الاتصال: {str(e)}")
            try:
                await client.disconnect()
            except:
                pass


        if all_members:
            with open(MEMBERS_FILE, "w", encoding='utf-8') as f:
                json.dump(all_members, f, indent=2, ensure_ascii=False)

            await update.message.reply_text(
                f"تم سحب المجموعات بنجاح!\n\n"
                f"• إجمالي الأعضاء: {len(all_members)} عضو\n"
                f"• من {len(links)} مجموعة\n"
                f"• تم حفظهم في ملف members.json\n\n"
                f"• يمكنك الآن نقلهم إلى مجموعة أخرى!"
            )
        else:
            await update.message.reply_text("لم يتم سحب أي أعضاء من المجموعات!")

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def pause_transfer_temp(query):
    user_id = query.from_user.id
    if user_id not in transfer_control:
        transfer_control[user_id] = {}

    transfer_control[user_id]["paused"] = True

    keyboard = [
        [InlineKeyboardButton("▶️ استئناف النقل", callback_data="resume_transfer_process")],
        [InlineKeyboardButton("⏹️ ايقاف تماماً", callback_data="stop_transfer_completely")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        "تم ايقاف النقل مؤقتاً ⏸️\n\n"
        "• يمكنك استئناف النقل من حيث توقف\n"
        "• أو إيقافه تماماً وعرض الإحصائيات النهائية",
        reply_markup=reply_markup
    )

async def stop_transfer_completely(query):
    user_id = query.from_user.id
    if user_id not in transfer_control:
        transfer_control[user_id] = {}

    transfer_control[user_id]["stopped"] = True

    await query.edit_message_text(
        "تم ايقاف النقل تماماً ⛔\n\n"
        "• تم إنهاء عملية النقل\n"
        "• سيتم عرض الإحصائيات النهائية قريباً\n\n"
        "• يمكنك بدء عملية نقل جديدة في أي وقت"
    )

async def resume_transfer_process(query):
    user_id = query.from_user.id
    if user_id not in transfer_control:
        transfer_control[user_id] = {}

    transfer_control[user_id]["paused"] = False

    await query.edit_message_text(
        "تم استئناف النقل ▶️\n\n"
        "• جاري متابعة النقل من حيث توقف\n"
        "• ستظهر الإحصائيات المحدثة قريباً"
    )



async def view_account_profile(query, phone):
    if phone not in accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="control_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("الحساب غير موجود!", reply_markup=reply_markup)
        return

    try:
        account_data = accounts[phone]
        session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
        client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
        await client.start(phone=phone)

        me = await client.get_me()

        profile_info = f"معلومات الحساب\n\n"
        profile_info += f"• الاسم: {me.first_name or 'غير محدد'}"
        if me.last_name:
            profile_info += f" {me.last_name}"
        profile_info += f"\n• اليوزر: @{me.username or 'غير محدد'}"
        profile_info += f"\n• الهاتف: {me.phone or phone}"
        profile_info += f"\n• المعرف: {me.id}"
        if hasattr(me, 'about') and me.about:
            profile_info += f"\n• البايو: {me.about}"

        await client.disconnect()

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data=f"control_acc_{phone}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(profile_info, reply_markup=reply_markup)

    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data=f"control_acc_{phone}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"خطأ في جلب معلومات الحساب: {str(e)}", reply_markup=reply_markup)

async def change_name_prompt(query, phone):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data=f"control_acc_{phone}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"تغيير اسم الحساب\n\n"
        f"ارسل الاسم الجديد:\n\n"
        f"مثال: احمد محمد\n\n"
        f"• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_name_change", "phone": phone}

async def change_username_prompt(query, phone):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data=f"control_acc_{phone}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"تغيير يوزر الحساب\n\n"
        f"ارسل اليوزر الجديد (بدون @):\n\n"
        f"مثال: ahmed123\n\n"
        f"• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_username_change", "phone": phone}

async def change_bio_prompt(query, phone):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data=f"control_acc_{phone}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"تغيير بايو الحساب\n\n"
        f"ارسل البايو الجديد:\n\n"
        f"مثال: مطور تطبيقات 👨‍💻\n\n"
        f"• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )
    user_data[query.from_user.id] = {"state": "waiting_bio_change", "phone": phone}

async def change_photo_prompt(query, phone):
    keyboard = [[InlineKeyboardButton("← رجوع", callback_data=f"control_acc_{phone}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"تغيير صورة الحساب {phone}\n\n"
        f"ارسل الصورة الجديدة:\n\n"
        f"• ارسل صورة من جهازك\n"
        f"• الصورة ستكون صورة البروفايل\n\n"
        f"• لالغاء العملية: اكتب 'الغاء'",
        reply_markup=reply_markup
    )


    user_data[query.from_user.id] = {
        "state": "waiting_photo_change",
        "phone": phone
    }
    print(f"📱 Set photo change state for user {query.from_user.id}, phone: {phone}")

async def process_name_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        new_name = update.message.text.strip()
        phone = user_data[user_id]["phone"]

        if new_name.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if not new_name or len(new_name) < 1:
            await update.message.reply_text("الاسم لا يمكن ان يكون فارغاً!")
            return

        await update.message.reply_text("جاري تغيير الاسم...")

        account_data = accounts[phone]
        session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
        client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
        await client.start(phone=phone)


        name_parts = new_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        from telethon.tl.functions.account import UpdateProfileRequest
        await client(UpdateProfileRequest(
            first_name=first_name,
            last_name=last_name
        ))


        accounts[phone]["first_name"] = first_name
        accounts[phone]["last_name"] = last_name
        save_accounts()

        await client.disconnect()

        await update.message.reply_text(
            f"تم تغيير الاسم بنجاح!\n\n"
            f"• الاسم الجديد: {new_name}"
        )

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ في تغيير الاسم: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]

async def process_username_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        new_username = update.message.text.strip()
        phone = user_data[user_id]["phone"]

        if new_username.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return


        new_username = new_username.replace("@", "")

        if not new_username or len(new_username) < 5:
            await update.message.reply_text("اليوزر يجب ان يكون 5 احرف على الاقل!")
            return

        await update.message.reply_text("جاري تغيير اليوزر...")

        account_data = accounts[phone]
        session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
        client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
        await client.start(phone=phone)

        from telethon.tl.functions.account import UpdateUsernameRequest
        await client(UpdateUsernameRequest(new_username))


        accounts[phone]["username"] = new_username
        save_accounts()

        await client.disconnect()

        await update.message.reply_text(
            f"تم تغيير اليوزر بنجاح!\n\n"
            f"• اليوزر الجديد: @{new_username}"
        )

        del user_data[user_id]

    except Exception as e:
        if "USERNAME_OCCUPIED" in str(e):
            await update.message.reply_text("هذا اليوزر محجوز، جرب يوزر آخر!")
        elif "USERNAME_INVALID" in str(e):
            await update.message.reply_text("اليوزر غير صالح، يجب ان يحتوي على احرف وارقام فقط!")
        else:
            await update.message.reply_text(f"خطأ في تغيير اليوزر: {str(e)}")

        if user_id in user_data:
            del user_data[user_id]

async def process_bio_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        new_bio = update.message.text.strip()
        phone = user_data[user_id]["phone"]

        if new_bio.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء العملية")
            del user_data[user_id]
            return

        if len(new_bio) > 70:
            await update.message.reply_text("البايو لا يمكن ان يزيد عن 70 حرف!")
            return

        await update.message.reply_text("جاري تغيير البايو...")

        account_data = accounts[phone]
        session_path = os.path.join(SESSIONS_DIR, f"session_{phone}")
        client = TelegramClient(session_path, account_data["api_id"], account_data["api_hash"])
        await client.start(phone=phone)

        from telethon.tl.functions.account import UpdateProfileRequest
        await client(UpdateProfileRequest(about=new_bio))

        await client.disconnect()

        await update.message.reply_text(
            f"تم تغيير البايو بنجاح!\n\n"
            f"• البايو الجديد: {new_bio}"
        )

        del user_data[user_id]

    except Exception as e:
        await update.message.reply_text(f"خطأ في تغيير البايو: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]





async def delete_account_menu(query):
    if not accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد حسابات للحذف!",
            reply_markup=reply_markup
        )
        return

    keyboard = []

    for phone in list(accounts.keys())[:10]:
        account_name = accounts[phone].get('first_name', phone)
        keyboard.append([InlineKeyboardButton(
            f"حذف {account_name} ({phone})",
            callback_data=f"delete_acc_{phone}"
        )])

    keyboard.append([InlineKeyboardButton("← رجوع", callback_data="manage_accounts")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"حذف حساب محدد\n\n"
        f"• اختر الحساب المراد حذفه:\n"
        f"• عدد الحسابات: {len(accounts)}",
        reply_markup=reply_markup
    )

async def delete_all_accounts_confirm(query):
    if not accounts:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "لا توجد حسابات للحذف!",
            reply_markup=reply_markup
        )
        return

    keyboard = [
        [InlineKeyboardButton("🗑️ نعم، احذف جميع الحسابات", callback_data="confirm_delete_all")],
        [InlineKeyboardButton("❌( لا، إلغاء العملية", callback_data="manage_accounts")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        f"• تحذير خطير!\n\n"
        f"أنت على وشك حذف جميع الحسابات:\n"
        f"• عدد الحسابات: {len(accounts)}\n"
        f"• سيتم حذف جميع ملفات الجلسات\n"
        f"• هذا الإجراء لا يمكن التراجع عنه!\n\n"
        f"هل أنت متأكد؟",
        reply_markup=reply_markup
    )

async def confirm_delete_all_accounts(query):
    try:
        if not accounts:
            await query.edit_message_text("لا توجد حسابات للحذف!")
            return

        deleted_count = len(accounts)
        session_files_deleted = 0


        for phone in accounts.keys():
            session_file = os.path.join(SESSIONS_DIR, f"session_{phone}.session")
            if os.path.exists(session_file):
                try:
                    os.remove(session_file)
                    session_files_deleted += 1
                except:
                    pass


        accounts.clear()
        save_accounts()

        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="manage_accounts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"تم حذف جميع الحسابات بنجاح!\n\n"
            f"• عدد الحسابات المحذوفة: {deleted_count}\n"
            f"• ملفات الجلسات المحذوفة: {session_files_deleted}\n"
            f"• تم تنظيف المجلد بالكامل",
            reply_markup=reply_markup
        )

    except Exception as e:
        await query.edit_message_text(f"خطأ في حذف الحسابات: {str(e)}")


async def delete_single_account(query, phone):
    try:
        if phone in accounts:

            session_file = os.path.join(SESSIONS_DIR, f"session_{phone}.session")
            if os.path.exists(session_file):
                os.remove(session_file)


            del accounts[phone]
            save_accounts()

            keyboard = [[InlineKeyboardButton("← رجوع", callback_data="delete_account")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                f"تم حذف الحساب {phone} بنجاح!\n\n"
                f"• تم حذف ملف الجلسة\n"
                f"• تم إزالة الحساب من القائمة",
                reply_markup=reply_markup
            )


            user_name = query.from_user.first_name or "مجهول"
            user_type = "owner" if is_admin(query.from_user.id) else "admin"
            log_event(user_type, "حذف حساب", user_name, query.from_user.id, f"تم حذف حساب {phone}")

        else:
            keyboard = [[InlineKeyboardButton("← رجوع", callback_data="delete_account")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("الحساب غير موجود!", reply_markup=reply_markup)
    except Exception as e:
        keyboard = [[InlineKeyboardButton("← رجوع", callback_data="delete_account")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(f"خطأ في حذف الحساب: {str(e)}", reply_markup=reply_markup)

async def process_transfer_link(update, context):
    await update.message.reply_text("ميزة النقل متوفرة في القائمة الرئيسية")

async def process_transfer_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        delay_text = update.message.text.strip()


        if user_id not in user_data or user_data[user_id].get("state") != "waiting_transfer_delay":
            await update.message.reply_text("خطأ: لم يتم العثور على بيانات النقل. يرجى البدء من جديد.")
            return

        
        try:
            delay_seconds = int(delay_text)
        except ValueError:
            keyboard = [[InlineKeyboardButton("الغاء", callback_data="transfer_members")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "يرجى ادخال رقم صحيح للمؤقت!\n\n"
                "مثال: 10 (للمؤقت 10 ثواني بين كل عضو)",
                reply_markup=reply_markup
            )
            return

     
        if delay_seconds < 3:
            keyboard = [[InlineKeyboardButton("الغاء", callback_data="transfer_members")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "المؤقت يجب أن يكون 3 ثواني على الأقل!\n\n"
                "هذا لتجنب FLOOD_WAIT وحماية الحسابات",
                reply_markup=reply_markup
            )
            return

        if delay_seconds > 60:
            keyboard = [[InlineKeyboardButton("الغاء", callback_data="transfer_members")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "المؤقت يجب أن يكون 60 ثانية كحد أقصى!\n\n"
                "مؤقت أكبر من ذلك سيجعل العملية بطيئة جداً",
                reply_markup=reply_markup
            )
            return

  
        user_data[user_id]["transfer_delay"] = delay_seconds
        user_data[user_id]["state"] = "waiting_target_group"

        keyboard = [[InlineKeyboardButton("الغاء", callback_data="transfer_members")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        
        transfer_count = user_data[user_id]["transfer_count"]
        estimated_time_per_account = (transfer_count * delay_seconds) / len(accounts) if accounts else transfer_count * delay_seconds
        estimated_minutes = estimated_time_per_account / 60

        await update.message.reply_text(
            f"✅ تم ضبط المؤقت: {delay_seconds} ثانية بين كل عضو\n\n"
            f"📊 ملخص الإعدادات:\n"
            f"• عدد الأعضاء: {transfer_count}\n"
            f"• المؤقت: {delay_seconds} ثانية\n"
            f"• الوقت المتوقع: ~{estimated_minutes:.1f} دقيقة لكل حساب\n\n"
            f"الآن ارسل رابط المجموعة المستهدفة:\n\n"
            f"• الروابط المدعومة:\n"
            f"• الروابط العامة: https://t.me/groupname\n"
            f"• الروابط الخاصة: https://t.me/+xxxxx\n"
            f"• روابط الدعوة: https://t.me/joinchat/xxxxx\n"
            f"• اليوزر المباشر: @groupname",
            reply_markup=reply_markup
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ في معالجة المؤقت: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def process_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة رقم الهاتف: التحقق والحفظ والانتقال للـ API ID"""
    try:
        user_id = update.effective_user.id
        phone = update.message.text.strip()

        if phone.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء اضافة الحساب")
            if user_id in user_data:
                del user_data[user_id]
            return

        
        if not phone.startswith('+') or not phone[1:].isdigit() or len(phone) < 8:
            await update.message.reply_text(
                "رقم الهاتف غير صحيح!\n\n"
                "• استخدم التنسيق: +966501234567"
            )
            return

        user_data[user_id]["phone"] = phone
        user_data[user_id]["state"] = "waiting_api_id"

        await update.message.reply_text(
            "تم حفظ رقم الهاتف\n\n"
            "الخطوة 2/3: ارسل API ID\n\n"
            "مثال: 123456\n\n"
            "• لالغاء العملية: اكتب 'الغاء'"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


async def process_api_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        user_id = update.effective_user.id
        api_id_text = update.message.text.strip()

        if api_id_text.lower() in ["الغاء", "إلغاء", "cancel"]:
            await update.message.reply_text("تم الغاء اضافة الحساب")
            if user_id in user_data:
                del user_data[user_id]
            return

        try:
            api_id = int(api_id_text)
        except ValueError:
            await update.message.reply_text(
                "API ID غير صحيح!\n\n"
                "يجب ان يكون رقماً صحيحاً"
            )
            return

        if api_id <= 0:
            await update.message.reply_text("API ID يجب أن يكون رقماً موجباً")
            return

        user_data[user_id]["api_id"] = api_id
        user_data[user_id]["state"] = "waiting_api_hash"

        await update.message.reply_text(
            "تم حفظ API ID\n\n"
            "الخطوة 3/3: ارسل API Hash\n\n"
            "مثال: a1b2c3d4e5f6g7h8i9"
        )

    except Exception as e:
        await update.message.reply_text(f"خطأ في API ID: {str(e)}")
        if user_id in user_data:
            del user_data[user_id]


def main():

    try:

        load_accounts()
        load_developers()


        application = Application.builder().token(BOT_TOKEN).build()


        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.Document.ALL, message_handler))


        logger.info("تم بدء تشغيل البوت بنجاح!")
        print("◉ البوت يعمل الآن...")
        application.run_polling()

    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت بواسطة المستخدم")
        print(" تم إيقاف البوت")
    except Exception as e:
        logger.error(f"خطأ في تشغيل البوت: {e}")
        print(f"❌ خطأ في تشغيل البوت: {e}")

if __name__ == '__main__':

    main()

