from fastapi import FastAPI
from pydantic import BaseSettings, BaseModel
from functools import lru_cache
from pyChatGPT import ChatGPT


class Settings(BaseSettings):
    EMAIL_OPENAI: str 
    PWD_OPENAI: str
    class Config:
        env_file = "app/.env"

class Text(BaseModel):
    text: str


@lru_cache()
def get_settings():
    return Settings()


def init_chatgpt(settings):      
    chatgpt = ChatGPT(auth_type='openai', email=settings.EMAIL_OPENAI, 
                    password=settings.PWD_OPENAI,
                    login_cookies_path = '.cache_gpt',
                    verbose=True)
    return chatgpt


settings = get_settings()
chatgpt = init_chatgpt(settings)
app = FastAPI()

@app.get("/")
def read_root():
    return {"Welcome": "This API queries ChatGPT"}

@app.post("/query")
async def predict(text: Text):
    """Function to generate predictions"""

    global chatgpt
    try:

        response = chatgpt.send_message(text.text)
        out = response['message']
    except Exception as e:
        print(e)
        out ='Please retry. ChatGPT is facing issues'
        chatgpt.__del__()
        chatgpt = init_chatgpt(settings)

    return {"answer": out}


@app.post('/reset')
async def reset():
    chatgpt.reset_conversation()
 