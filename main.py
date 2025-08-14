import json
import random
import string
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask
import os
import asyncio

CONFIG = {
    "BOT_TOKEN": os.getenv("BOT_TOKEN", "8209067688:AAG89WS4BzGhVznDeO5ClWtGEQsyiEbTVCs"),
    "ADMIN_ID": int(os.getenv("ADMIN_ID", "6788809365"))
}

DATA_FILE = "data.json"

# Flask for Render ping
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot running!"

# Load / Save Data
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Commands
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

async def main():
    application = ApplicationBuilder().token(CONFIG["BOT_TOKEN"]).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("genkey", genkey))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("west", west))
    application.add_handler(CommandHandler("spend", spend))

    # Telegram Polling ko async me chalana
    loop = asyncio.get_event_loop()
    loop.create_task(application.run_polling())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    asyncio.run(main())
