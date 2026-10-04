async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_partaker(user.id)
    
    # Custom welcome message to the user
    await update.message.reply_text("Phantom’s Bc 〽️\nYou’re in. 👽\nKeep your notifications on.")
    
    # IMMEDIATELY alert Admin on join (even if they don't send text)
    if ADMIN_ID and user.id != ADMIN_ID:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔔 **New Partaker Joined!**\n\n👤 **Name:** {user.first_name}\n👤 **Username:** @{user.username or 'None'}\n🆔 **User ID:** `{user.id}`\n\n*To message them, send:* `/reply {user.id} Your message`",
            parse_mode="Markdown"
        )
