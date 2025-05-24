import os
import logging
from datetime import datetime, timedelta
from flask import Flask, request
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler

# Mengambil token dari environment variable
TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# Jika TOKEN tidak ada, beri error yang lebih jelas
if not TOKEN:
    raise ValueError("Bot token is missing! Please set the BOT_TOKEN environment variable.")

# Setup Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Flask app untuk webhook
app = Flask(__name__)

# Fungsi untuk mengirim pengingat
def send_reminder(context: CallbackContext):
    job = context.job
    context.bot.send_message(chat_id=job.context['chat_id'], text=f"⏰ Pengingat: {job.context['message']}")

# Start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Halo! Saya bot pengingat. Gunakan: /ingatkan <menit> <pesan>")

# Command untuk mengatur pengingat
def ingatkan(update: Update, context: CallbackContext):
    try:
        menit = int(context.args[0])
        pesan = ' '.join(context.args[1:])
        waktu = datetime.now() + timedelta(minutes=menit)

        # Menjadwalkan pengingat
        scheduler.add_job(
            send_reminder,
            trigger='date',
            run_date=waktu,
            context={'chat_id': update.message.chat_id, 'message': pesan}
        )

        update.message.reply_text(f"Pengingat disetel dalam {menit} menit: \"{pesan}\"")
    except (IndexError, ValueError):
        update.message.reply_text("Format salah. Gunakan: /ingatkan <menit> <pesan>")

# Webhook handler
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = Update.de_json(json_str, updater.bot)
    dispatcher.process_update(update)
    return 'ok', 200

# Setup Updater dan Dispatcher untuk webhook
def main():
    global updater
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Daftarkan handler
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("ingatkan", ingatkan))

    # Set webhook Telegram
    updater.bot.set_webhook(url=WEBHOOK_URL + "/webhook")

    # Mulai Flask untuk menerima request webhook
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    main()
