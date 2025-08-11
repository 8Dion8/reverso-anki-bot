from anki import AnkiHandler
from reverso import ReversoHandler
from db import DBHandler
from bot import Bot
import os
from dotenv import load_dotenv

import logging

logging.basicConfig(level=logging.INFO)
logging.info("Application startup.")


load_dotenv()


if __name__ == "__main__":
    logging.info("Module reverso startup...")
    reversoHandler = ReversoHandler()
    logging.info("Module anki startup...")
    ankiHandler = AnkiHandler()
    logging.info("Module db startup...")
    dbHandler = DBHandler()
    logging.info("Module bot startup...")
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if TOKEN:
        logging.debug("Token found!")
        bot = Bot(TOKEN, reversoHandler, ankiHandler, dbHandler)
    else:
        logging.error("No token found! Exiting.")
        raise Exception("No tg token")

    bot.run()
