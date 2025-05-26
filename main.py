from anki import AnkiHandler
from reverso import ReversoHandler
from db import DBHandler
from bot import Bot
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    print("Loading reverso... ", end="")
    reversoHandler = ReversoHandler()
    print("Done.\nLoading anki... ", end="")
    ankiHandler = AnkiHandler()
    print("Done.\nLoading db... ", end="")
    dbHandler = DBHandler()
    print("Done. Starting bot...")
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if TOKEN:
        bot = Bot(TOKEN, reversoHandler, ankiHandler, dbHandler)
    else:
        raise Exception("No tg token")

    bot.run()
