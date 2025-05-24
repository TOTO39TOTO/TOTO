from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from datetime import datetime, timedelta
import os

# Ganti dengan token bot kamu atau ambil dari environment variable
TOKEN = os.environ.get("BOT_TOKEN")

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Kirim pengingat
def send_reminder(context: CallbackContext):
    job = context.job
    context.bot.send_message(chat_id=job.context['chat_id'], text=f"⏰ Pengingat: {job.context['message']}")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Halo! Saya bot pengingat. Gunakan: /ingatkan <menit> <pesan>")

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
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ingatkan", ingatkan))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
