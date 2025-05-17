from anki import AnkiHandler
from reverso import ReversoHandler
from bot import Bot
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    reversoHandler = ReversoHandler()
    ankiHandler = AnkiHandler()
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if TOKEN:
        bot = Bot(TOKEN, reversoHandler, ankiHandler)
    else:
        raise Exception("No tg token")

    bot.run()
