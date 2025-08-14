import asyncio
import json
import os
import random
import string
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask

# Flask app for Render ping
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot running!"

DATA_FILE = "data.json"
CONFIG = {
    "BOT_TOKEN": os.getenv("BOT_TOKEN", "8209067688:AAG89WS4BzGhVznDeO5ClWtGEQsyiEbTVCs"),
    "ADMIN_ID": int(os.getenv("ADMIN_ID", "6788809365"))
}

# Utility functions
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Apka Telegram ID: {update.effective_user.id}\nAdmin se key lekar /register <key> use karein.")

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Use: /register <key>")
        return
    key = context.args[0]
    data = load_data()
    if key in data['keys']:
        data['users'][str(update.effective_user.id)] = key
        save_data(data)
        await update.message.reply_text("✅ Registration successful!")
    else:
        await update.message.reply_text("❌ Invalid key.")

async def genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != CONFIG['ADMIN_ID']:
        await update.message.reply_text("❌ Only admin can generate keys.")
        return
    key = generate_key()
    data = load_data()
    data['keys'].append(key)
    save_data(data)
    await update.message.reply_text(f"✅ Key generated: {key}")

async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Use: /add <amount>")
        return
    user_id = str(update.effective_user.id)
    data = load_data()
    if user_id not in data['users']:
        await update.message.reply_text("❌ Register first.")
        return
    amount = float(context.args[0])
    data['transactions'].append({
        "user_id": user_id,
        "type": "add",
        "amount": amount,
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    save_data(data)
    await update.message.reply_text(f"💰 {amount} saving se nikala.")

async def west(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Use: /west <amount>")
        return
    user_id = str(update.effective_user.id)
    data = load_data()
    if user_id not in data['users']:
        await update.message.reply_text("❌ Register first.")
        return
    amount = float(context.args[0])
    data['transactions'].append({
        "user_id": user_id,
        "type": "west",
        "amount": amount,
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    save_data(data)
    await update.message.reply_text(f"💸 {amount} kharch hua.")

async def spend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    if user_id not in data['users']:
        await update.message.reply_text("❌ Register first.")
        return
    month = datetime.now().strftime("%Y-%m")
    total = sum(t['amount'] for t in data['transactions']
                if t['user_id'] == user_id and t['type'] == "west" and t['date'].startswith(month))
    await update.message.reply_text(f"📊 Is mahine ka total spend: {total}")

# Main async launcher
async def main():
    app_bot = ApplicationBuilder().token(CONFIG["BOT_TOKEN"]).build()

    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("register", register))
    app_bot.add_handler(CommandHandler("genkey", genkey))
    app_bot.add_handler(CommandHandler("add", add))
    app_bot.add_handler(CommandHandler("west", west))
    app_bot.add_handler(CommandHandler("spend", spend))

    # Run Flask on background thread
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000))))

    # Run Telegram bot polling
    await app_bot.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
