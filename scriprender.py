import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Dispatcher
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime, timedelta
from flask import Flask, request
from telegram.ext import Dispatcher, CommandHandler

# Ganti dengan token bot kamu atau ambil dari environment variable
TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # URL untuk webhook

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Kirim pengingat
def send_reminder(context: CallbackContext):
    job = context.job
    context.bot.send_message(chat_id=job.context['chat_id'], text=f"⏰ Pengingat: {job.context['message']}")

# Flask app untuk webhook
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, updater.bot)
    dispatcher.process_update(update)
    return 'ok', 200

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Halo! Saya bot pengingat UPDATE PER 2JAM . Gunakan: /ingatkan <menit> <pesan>")

def ingatkan(update: Update, context: CallbackContext):
    try:
        menit = int(context.args[0])
        pesan = ' '.join(context.args[1:])
        waktu = datetime.now() + timedelta(minutes=menit)

        scheduler.add_job(
            send_reminder,
            trigger='date',
            run_date=waktu,
            context={'chat_id': update.message.chat_id, 'message': pesan}
        )

        update.message.reply_text(f"Pengingat disetel dalam {menit} menit: \"{pesan}\"")
    except (IndexError, ValueError):
        update.message.reply_text("Format salah. Gunakan: /ingatkan <menit> <pesan>")

def main():
    # Set up Updater dan Dispatcher
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Daftarkan handler
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("ingatkan", ingatkan))

    # Set webhook Telegram
    updater.bot.set_webhook(url=WEBHOOK_URL + "/webhook")

    # Mulai Flask server untuk webhook
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    main()
