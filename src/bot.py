import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import whisper
from dotenv import load_dotenv
import os
import argparse
import requests

load_dotenv("app/.env")
API_TELEGRAM = os.getenv("API_TELEGRAM")
headers = {"accept": "application/json", "Content-Type": "application/json"}
whisper_model = whisper.load_model("base")


parser = argparse.ArgumentParser()
parser.add_argument("-hs", "--host", help="specify a hostname", default='127.0.0.1', type=str)
parser.add_argument("-p", "--port", help="specify a port number", default=5052, type=int)
args = parser.parse_args()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def echo(update, context):
    """Echo the user message."""
    answer = generate_response(update.message.text)
    update.message.reply_text(answer)


def transcribe_voice_message(voice_message):
    # Use the Whisper AI API to transcribe the voice message
    result = whisper_model.transcribe(voice_message)
    return result["text"]


def handle_voice_message(update, context):

    # Get the voice message from the update
    voice_message = context.bot.get_file(update.message.voice.file_id)
    voice_message.download(f"voice.mp3")

    # Transcribe the voice message
    text = transcribe_voice_message("voice.mp3")
    try:
        # Answer
        answer = generate_response(text)

        # Send the transcribed text back to the user
        update.message.reply_text(answer)

    except Exception as e:
        print("error: " + e.message)


def generate_response(transcribed_text: str, retries: int = 3, timeout: int = 40):
    """Generate answer using ChatGPT"""
    for i in range(retries):
        try:
            # Make the POST request
            response = requests.post(
                f"http://{args.host}:{args.port}/query",
                json={"text": transcribed_text},
                headers=headers,
                timeout=timeout,
            )
            # If the request is successful, return the response
            if response.status_code == 200:
                return response.json()["answer"]
        except requests.exceptions.RequestException:
            # If there was a timeout or other error, try again
            print("I keep asking")
            continue
    # If all retries fail, raise an exception
    raise Exception("POST request failed after {} retries".format(retries))


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def reset(update, context):
    """Log Errors caused by Updates."""
    resp = requests.post(f"http://{args.host}:{args.port}/reset")


def main():
    """Start the bot."""

    updater = Updater(API_TELEGRAM, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("reset", reset))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))
    voice_handler = MessageHandler(Filters.voice, handle_voice_message)
    dp.add_handler(voice_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    updater.idle()


if __name__ == "__main__":




    print(args)

    main()
