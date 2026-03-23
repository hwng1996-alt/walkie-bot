import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "walkies.json"


def default_walkies():
    return {
        f"W{i:02}": {"status": "available", "holder": None}
        for i in range(1, 26)
    }


def load_walkies():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    data = default_walkies()
    save_walkies(data)
    return data


def save_walkies(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


walkies = load_walkies()


def get_user_name(update: Update) -> str:
    user = update.effective_user
    if user.username:
        return f"@{user.username}"
    return user.first_name or "Unknown"


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/available\n"
        "/take W01\n"
        "/return W01\n"
        "/status W01\n"
        "/listout"
    )


async def available(update: Update, context: ContextTypes.DEFAULT_TYPE):
    available_walkies = [w for w, i in walkies.items() if i["status"] == "available"]
    await update.message.reply_text(
        "Available:\n" + ", ".join(available_walkies) if available_walkies else "None available"
    )


async def take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /take W01")
        return

    wid = context.args[0].upper()

    if wid not in walkies:
        await update.message.reply_text("Invalid walkie")
        return

    if walkies[wid]["status"] != "available":
        await update.message.reply_text(f"{wid} already taken")
        return

    user = get_user_name(update)
    walkies[wid]["status"] = "out"
    walkies[wid]["holder"] = user
    save_walkies(walkies)

    await update.message.reply_text(f"{wid} checked out to {user}")


async def return_walkie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /return W01")
        return

    wid = context.args[0].upper()

    if wid not in walkies:
        await update.message.reply_text("Invalid walkie")
        return

    walkies[wid]["status"] = "available"
    walkies[wid]["holder"] = None
    save_walkies(walkies)

    await update.message.reply_text(f"{wid} returned")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /status W01")
        return

    wid = context.args[0].upper()

    if wid not in walkies:
        await update.message.reply_text("Invalid walkie")
        return

    info = walkies[wid]
    msg = f"{wid}: {info['status']}"
    if info["holder"]:
        msg += f" ({info['holder']})"

    await update.message.reply_text(msg)


async def listout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    out_list = [
        f"{w} - {i['holder']}"
        for w, i in walkies.items()
        if i["status"] == "out"
    ]

    if not out_list:
        await update.message.reply_text("All available ✅")
        return

    await update.message.reply_text("OUT:\n" + "\n".join(out_list))


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("available", available))
    app.add_handler(CommandHandler("take", take))
    app.add_handler(CommandHandler("return", return_walkie))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("listout", listout))

    print("Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()