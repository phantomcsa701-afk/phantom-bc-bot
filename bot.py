import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Initialize local SQLite database
def init_db():
    conn = sqlite3.connect("partakers.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partakers (
            user_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

def add_partaker(user_id: int):
    try:
        conn = sqlite3.connect("partakers.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO partakers (user_id) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        logging.error(f"Error adding user: {e}")

def get_partakers():
    try:
        conn = sqlite3.connect("partakers.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM partakers")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    except Exception as e:
        logging.error(f"Error getting users: {e}")
        return []

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_partaker(user.id)
    
    await update.message.reply_text("Phantom’s Bc 〽️\nYou’re in. 👽\nKeep your notifications on.")
    
    # Notify Admin immediately when someone joins
    if ADMIN_ID and user.id != ADMIN_ID:
        admin_text = (
            f"🔔 New Partaker Joined!\n\n"
            f"Name: {user.first_name}\n"
            f"Username: @{user.username or 'None'}\n"
            f"User ID: {user.id}\n\n"
            f"To message them, send: /reply {user.id} Your message"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    message_text = " ".join(context.args)
    if not message_text:
        await update.message.reply_text("Usage: /bc Your message here")
        return

    partakers_list = get_partakers()
    count = 0
    for sub_id in partakers_list:
        try:
            await context.bot.send_message(chat_id=sub_id, text=message_text)
            count += 1
        except Exception:
            pass
            
    await update.message.reply_text(f"✅ Broadcast sent to {count} partakers.")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    partakers_list = get_partakers()
    await update.message.reply_text(f"📊 Total active partakers: {len(partakers_list)}")

async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.id == ADMIN_ID:
        return

    user_text = update.message.text
    
    if ADMIN_ID:
        forward_text = (
            f"💬 New Message from {user.first_name} (@{user.username or 'None'}):\n\n"
            f"{user_text}\n\n"
            f"User ID: {user.id}\n\n"
            f"To reply, send: /reply {user.id} Your message"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=forward_text)

async def reply_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /reply <User_ID> <Your message>")
        return

    target_id = context.args[0]
    reply_text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=int(target_id), text=reply_text)
        await update.message.reply_text(f"✅ Reply sent to User ID {target_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send reply: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bc", broadcast))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("reply", reply_user))
    
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), forward_to_admin))
    
    app.run_polling()
