import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
partakers = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    subscribers.add(user.id)
    
    # Send custom welcome message
    await update.message.reply_text("Phantom’s Bc 〽️\nYou’re in. 👽\nKeep your notifications on.")
    
    # Notify Admin privately
    if ADMIN_ID and user.id != ADMIN_ID:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 New partaker joined:\nName: {user.first_name}\nUsername: @{user.username or 'None'}\nID: {user.id}"
        )

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    
    message_text = " ".join(context.args)
    if not message_text:
        await update.message.reply_text("Usage: /bc Your message here")
        return

    count = 0
    for sub_id in partakers:
        try:
            await context.bot.send_message(chat_id=sub_id, text=message_text)
            count += 1
        except Exception:
            pass
            
    await update.message.reply_text(f"✅ Broadcast sent to {count} partakers.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bc", broadcast))
    app.run_polling()
