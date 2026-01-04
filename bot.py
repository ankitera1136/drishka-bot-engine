import os
import sqlite3
import datetime
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from apscheduler.schedulers.background import BackgroundScheduler

# ───────────── ENV ─────────────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ───────────── DATABASE ─────────────
conn = sqlite3.connect("library.db", check_same_thread=False)
cursor = conn.cursor()

# ───────────── MENU ─────────────
main_menu = ReplyKeyboardMarkup(
    [
        ["🪪 My Membership"],
        ["⏰ Timings & Rules"],
        ["📢 Announcements", "🆘 Help"]
    ],
    resize_keyboard=True
)

# ───────────── START ─────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    cursor.execute(
        "INSERT OR IGNORE INTO users VALUES (?, ?, ?)",
        (user.id, user.first_name, str(datetime.date.today()))
    )
    conn.commit()

    await update.message.reply_text(
        f"👋 Welcome to Drishka Self Study Library, {user.first_name}!\n\n"
        "Use the menu below 👇",
        reply_markup=main_menu
    )

# ───────────── USER HANDLER ─────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "🪪 My Membership":
        cursor.execute(
            "SELECT seat_no, fee, due_date FROM members WHERE user_id=?",
            (user_id,)
        )
        data = cursor.fetchone()

        if data:
            seat, fee, due = data
            reply = (
                "🪪 Membership Details\n\n"
                f"🪑 Seat No: {seat}\n"
                f"💰 Monthly Fee: ₹{fee}\n"
                f"📅 Next Due Date: {due}"
            )
        else:
            reply = (
                "❌ No active membership found.\n"
                "Please contact admin."
            )

        await update.message.reply_text(reply)

    elif text == "⏰ Timings & Rules":
        await update.message.reply_text(
            "⏰ *Library Timings*\n"
            "• Morning: 6:00 AM – 12:00 PM\n"
            "• Afternoon: 12:00 PM – 6:00 PM\n"
            "• Night: 6:00 PM – 11:00 PM\n\n"
            "📜 *Rules*\n"
            "• Maintain silence 🤫\n"
            "• Mobile on silent 📵\n"
            "• No food inside 🍔❌\n"
            "• Fee must be paid before due date\n"
            "• Seat change only with permission",
            parse_mode="Markdown"
        )

    elif text == "📢 Announcements":
        await update.message.reply_text(
            "📢 Important announcements will be sent here."
        )

    elif text == "🆘 Help":
        await update.message.reply_text(
            "🆘 Help Desk\n\n"
            "📞 Contact: +91XXXXXXXXXX\n"
            "📍 Drishka Self Study Library"
        )

    else:
        await update.message.reply_text(
            "❗ Please use the menu buttons below."
        )

# ───────────── ADMIN: ADD MEMBER (LAST USER) ─────────────
async def addmember_last(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        seat_no = context.args[0]
        fee = int(context.args[1])
        due_date = context.args[2]

        cursor.execute(
            "SELECT user_id FROM users ORDER BY joined_on DESC LIMIT 1"
        )
        result = cursor.fetchone()

        if not result:
            await update.message.reply_text("❌ No users found")
            return

        user_id = result[0]

        cursor.execute(
            "INSERT OR REPLACE INTO members VALUES (?, ?, ?, ?)",
            (user_id, seat_no, fee, due_date)
        )
        conn.commit()

        await context.bot.send_message(
            user_id,
            "✅ Membership Activated\n\n"
            f"🪑 Seat No: {seat_no}\n"
            f"💰 Monthly Fee: ₹{fee}\n"
            f"📅 Due Date: {due_date}"
        )

        await update.message.reply_text(
            "✅ Member added (last joined student)"
        )

    except:
        await update.message.reply_text(
            "❌ Usage:\n/addmember_last <seat_no> <fee> <YYYY-MM-DD>"
        )

# ───────────── ADMIN: BROADCAST ─────────────
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("❌ Usage:\n/broadcast <message>")
        return

    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()

    for (uid,) in users:
        try:
            await context.bot.send_message(uid, f"📢 {message}")
        except:
            pass

    await update.message.reply_text("✅ Announcement sent")

# ───────────── UNKNOWN ─────────────
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Unknown command")

def send_fee_reminders(bot):
    today = datetime.date.today()

    cursor.execute(
        "SELECT user_id, seat_no, fee, due_date FROM members"
    )
    members = cursor.fetchall()

    for user_id, seat, fee, due_date in members:
        due = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()
        days_left = (due - today).days

        try:
            if days_left == 2:
                bot.send_message(
                    user_id,
                    f"⏰ Fee Reminder\n\n"
                    f"🪑 Seat: {seat}\n"
                    f"💰 Amount: ₹{fee}\n"
                    f"📅 Due in 2 days ({due})"
                )

            elif days_left == 0:
                bot.send_message(
                    user_id,
                    f"📅 Fee Due Today\n\n"
                    f"🪑 Seat: {seat}\n"
                    f"💰 Amount: ₹{fee}\n"
                    f"⚠ Please pay today"
                )

            elif days_left < 0:
                bot.send_message(
                    user_id,
                    f"❗ Fee Overdue\n\n"
                    f"🪑 Seat: {seat}\n"
                    f"💰 Amount: ₹{fee}\n"
                    f"📅 Due date was {due}\n"
                    f"⚠ Please clear dues immediately"
                )
        except:
            pass


# ───────────── APP ─────────────
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addmember_last", addmember_last))
app.add_handler(CommandHandler("broadcast", broadcast))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(MessageHandler(filters.COMMAND, unknown))

scheduler = BackgroundScheduler()
scheduler.add_job(
    send_fee_reminders,
    "cron",
    hour=9,
    minute=0,
    args=[app.bot]
)
scheduler.start()

print("🤖 Drishka Library Bot is running...")
app.run_polling()
