import os
import logging
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Initialize SQLite database
DB_NAME = "partakers.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partakers (
            user_id INTEGER PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()

def add_partaker(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO partakers (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def get_partakers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM partakers")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_partaker(user.id)
    
    # Send custom welcome message
    await update.message.reply_text("Phantom’s Bc 〽️\nYou’re in. 👽\nKeep your notifications on.")
    
    # Notify Admin privately when a new user joins
    if ADMIN_ID and user.id != ADMIN_ID:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 New partaker joined:\nName: {user.first_name}\nUsername: @{user.username or 'None'}\nID: `{user.id}`",
            parse_mode="Markdown"
        )

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

# Forward any normal text message from a user to Admin
async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Do not forward admin's own text messages
    if user.id == ADMIN_ID:
        return

    user_text = update.message.text
    
    if ADMIN_ID:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"💬 **New Message from {user.first_name}** (@{user.username or 'None'}):\n\n{user_text}\n\n🆔 **User ID:** `{user.id}`\n\n*To reply, send:* `/reply {user.id} Your message`",
            parse_mode="Markdown"
        )

# Direct reply from Admin to a specific user via the bot
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
        await update.message.reply_text(f"✅ Reply sent to User ID `{target_id}`.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send reply: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bc", broadcast))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("reply", reply_user))
    
    # Message handler for regular text messages
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), forward_to_admin))
    
    app.run_polling()
