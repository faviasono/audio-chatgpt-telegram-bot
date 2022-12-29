# Telegram bot Audio ChatGPT

**ChatGPT** is changing how we perceive technology, and interacting with it in a smooth and clean manner is paramount to further improve user experience. This is why I believe interacting with it using Telegram bots and using speech can help further exploit its potential.

Telegram bot to use ChatGPT with text and vocal messages.
Currently, there is no APIs available for using ChatGPT, hence I relied on external projects that use Selenium to interact with ChatGPT.

Once the APIs will be available, the bot will be officialy released on a production server.
At the moment, it's usage is limited to one thread and one process and is deployed on my local machine.

Any recommendations or suggestions is welcome in the issue tracker.

## Implementation

I used `pyChatGPT` and deployed it as API using `FastAPI` framework.
Then, I use `python-telegram-bot` to send post requests to the API and return the text back to the user.
Voice messages are first transcribed using opened-source OpenAI `Wishper` model and then sent to ChatGPT API.


## Usage

1. Telegram BOT

When the bot is running on my local host, you can text to the audio-chatgpt bot on Telegram.

2. Repository

You first need to run the fast api service using 

    uvicorn app.main:app --port PORT_NAME`

Then, you can run  

    python src/bot.pt -hs HOST_NAME  -p PORT_NAME

n.b. at the moment, everything is set up to work on localhost.

You might need to create your own Telegram Bot using `BotFather` service to create your own audio-chatgpt bot.


## Examples
I sent to Telegram bot the voice message 

    Please list three activities I can do on a rainy day

Below you can see the output on Telegram:
    
![](static/example.png)




