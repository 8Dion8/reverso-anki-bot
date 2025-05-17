from reverso import ReversoHandler
from bot import Bot
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    reversoHandler = ReversoHandler()
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if TOKEN:
        bot = Bot(TOKEN, reversoHandler)
    else:
        raise Exception("No tg token")

    bot.run()
