import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import whisper
from dotenv import load_dotenv
from typing import List
import os
import sys
import argparse
import openai
import sqlite3

DATABASE_FILE = "chatbot_db.sqlite"


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import *

import json


load_dotenv("app/.env")

CHATGPT_MODEL = "gpt-3.5-turbo"
CHATGPT_SYSTEM_ROLE = (
    "You are a Telegram bot, and need to give concise and short answers"
)

CHATGPT_SYSTEM_MESSAGE = {"role": "system", "content": CHATGPT_SYSTEM_ROLE}
messages = [CHATGPT_SYSTEM_MESSAGE]  # GLOBAL VARIABLE

API_TELEGRAM = os.getenv("API_TELEGRAM")
API_OPENAI = os.getenv("OPENAI_TOKEN")
openai.api_key = API_OPENAI


whisper_model = whisper.load_model("base")


parser = argparse.ArgumentParser()
parser.add_argument(
    "-hs", "--host", help="specify a hostname", default="127.0.0.1", type=str
)
parser.add_argument(
    "-p", "--port", help="specify a port number", default=5052, type=int
)
args = parser.parse_args()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Updater, context):
    """Send a message when the command /start is issued."""

    update.message.reply_text("Hi! Please insert your OpenAPI key")


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text("Help!")


def echo(update, context):
    """Echo the user message."""

    print(update)

    telegram_id = update.message.chat.id
    print(telegram_id)

    answer = generate_response(update.message.text, telegram_id)
    update.message.reply_text(answer)


def transcribe_voice_message(voice_message):
    # Use the Whisper AI API to transcribe the voice message
    result = whisper_model.transcribe(voice_message)

    return result["text"]


def handle_voice_message(update, context):
    # Get the voice message from the update
    voice_message = context.bot.get_file(update.message.voice.file_id)
    voice_message.download(f"/tmp/voice.mp3")

    # Transcribe the voice message
    text = transcribe_voice_message("/tmp/voice.mp3")
    print(text)
    try:
        # Answer
        telegram_id = update.message.chat.id

        answer = generate_response(text, telegram_id)

        # Send the transcribed text back to the user
        update.message.reply_text(answer)

    except Exception as e:
        print(e)


def generate_response(transcribed_text: str, telegram_id: str):
    """Generate answer using ChatGPT"""

    try:
        # Retrieve user-specific data from the database
        with sqlite3.connect(DATABASE_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT api_key, history FROM users WHERE telegram_id = ?",
                (telegram_id,),
            )
            row = c.fetchone()
            if row is None:
                raise ValueError(f"No user found with telegram_id '{telegram_id}'")
            api_key, history_json = row
            history = json.loads(history_json) if history_json else []
            c.close()

        # Set the OpenAI API key
        openai.api_key = api_key

        # Add the user's message to the chat history
        history.append({"role": "user", "content": transcribed_text})
        print(history)

        # Generate a response using ChatGPT
        response = openai.Completion.create(
            engine=CHATGPT_MODEL,
            messages=history,
        )

        # Extract the response and add it to the chat history
        answer = response["choices"][0]["text"]
        history.append({"role": "assistant", "content": answer})

        # Update the user's chat history in the database
        with sqlite3.connect(DATABASE_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "UPDATE users SET history = ? WHERE telegram_id = ?",
                (json.dumps(history), telegram_id),
            )
            conn.commit()
            c.close()

        return answer

    except Exception as e:
        print(e)
        # If all retries fail, raise an exception
        raise Exception("POST request failed after")


def reset(update, context):
    with sqlite3.connect(DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE users SET history = ? WHERE telegram_id = ?",
            (json.dumps([]), update.message.chat.id),
        )
        conn.commit()
        c.close()

    update.message.reply_text("History cleaned up successfully")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


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
