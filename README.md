# Telegram bot Audio ChatGPT

**ChatGPT** is changing how we perceive technology, and interacting with it in a smooth and clean manner is paramount to further improve user experience. This is why I believe interacting with it using Telegram bots and using speech can help further exploit its potential.

Telegram bot to use ChatGPT with text and vocal messages.
I have updated the repo using Whisper and ChatGPT official APIs from OpenAI. 

The bot has been deployed on [Railway](https://railway.app), and it works amazingly! 🚀
You can deploy your own bot, or try out mine! [@AudioGPT_bot](https://t.me/AudioGPT_bot)

## Features

* Use voice and text messages to interact with the Bot
* Type or speak in many different languages 
* Fast answers (2-3 seconds)
* History tracked for individual user (you can clean it)


## Bot commands

* `/reset` – start new dialog
* `/help` – show help
* `/start` – register to the service


## Setup for deployment

1. Register the new bot with [@BotFather](https://core.telegram.org/bots/tutorial) and retrieve the bot key
2. Register to [OpenAI](https://openai.com)  and retrieve the key
3. Register to [Railway](https://railway.app) and use the template I created to set up your own configuration:

   [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/rxWKuE?referralCode=c9RZUJ)
   
If you want to run locally, you will still need to set up a PostgreSQL database and configure the following env variable in `app/.env` file:
```YAML
    API_TELEGRAM = ""
    OPENAI_TOKEN = ""

    MODE = 'polling'
    PORT = '8443'
    CHATGPT_MODEL = "gpt-3.5-turbo"

    PGDATABASE = ""
    PGHOST = ""
    PGPASSWORD = ""
    PGPORT = ""
    PGUSER = ""

```




