import json
import random
import string
from datetime import datetime
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

CONFIG_PATH = "config.json"
DATA_PATH = "data.json"

# Load config
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
ADMIN_ID = config["ADMIN_ID"]

# Data loading/saving
def load_data():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)

# Generate random key
def generate_key():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Commands
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    update.message.reply_text("Apka Telegram ID: {}".format(user_id))
    update.message.reply_text("Apne admin se key le kar /register <key> type karke register karein.")

def register(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Use: /register <key>")
        return
    key = context.args[0]
    data = load_data()
    if key in data["keys"]:
        data["users"][str(update.effective_user.id)] = key
        save_data(data)
        update.message.reply_text("✅ Registration successful!")
    else:
        update.message.reply_text("❌ Invalid key.")

def genkey(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("❌ You are not allowed to generate keys.")
        return
    new_key = generate_key()
    data = load_data()
    data["keys"].append(new_key)
    save_data(data)
    update.message.reply_text(f"✅ Key generated: {new_key}")

def add(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Use: /add <amount>")
        return
    amount = float(context.args[0])
    user_id = str(update.effective_user.id)
    data = load_data()

    # Authentication
    if user_id not in data["users"]:
        update.message.reply_text("❌ You are not registered. Use /register <key>")
        return

    data["transactions"].append({
        "user_id": user_id,
        "type": "add",
        "amount": amount,
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    save_data(data)
    update.message.reply_text(f"💰 {amount} saving se nikala gaya.")

def west(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Use: /west <amount>")
        return
    amount = float(context.args[0])
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data["users"]:
        update.message.reply_text("❌ You are not registered. Use /register <key>")
        return

    data["transactions"].append({
        "user_id": user_id,
        "type": "west",
        "amount": amount,
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    save_data(data)
    update.message.reply_text(f"💸 {amount} kharch hua.")

def spend(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    data = load_data()
    if user_id not in data["users"]:
        update.message.reply_text("❌ You are not registered.")
        return

    month = datetime.now().strftime("%Y-%m")
    total_spend = sum(t["amount"] for t in data["transactions"]
                      if t["user_id"] == user_id and
                         t["type"] == "west" and
                         t["date"].startswith(month))
    update.message.reply_text(f"📊 Is mahine ka total spend: {total_spend}")

# Flask Server (for Render ping)
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

if __name__ == "__main__":
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("register", register))
    dp.add_handler(CommandHandler("genkey", genkey))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("west", west))
    dp.add_handler(CommandHandler("spend", spend))

    # Start polling in background
    updater.start_polling()

    # Start Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
