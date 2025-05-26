import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, Message, ReplyKeyboardRemove

from db import DBHandler
from anki import AnkiHandler
from reverso import ReversoHandler


class Bot:
    def __init__(self,  token, reversoHandler: ReversoHandler, ankiHandler: AnkiHandler, dbhandler: DBHandler):
        self.bot = telebot.TeleBot(token)
        self.reversoHandler = reversoHandler
        self.ankiHandler = ankiHandler
        self.dbhandler = dbhandler
        print("Bot up and running!")


        @self.bot.message_handler(commands=["start"])
        def start(message: Message):
            print("Got start")
            if message.from_user:
                id = message.from_user.id
                user_ids = [i[0] for i in self.dbhandler.get_user_list()]
                if id in user_ids:
                    print("User found, just setting state")
                else:
                    print(f"New user {id}")
                    self.dbhandler.init_user(id, message.from_user.username)

                self.dbhandler.reset_user_query(id)
                self.dbhandler.reset_user_context_options(id)
                self.dbhandler.set_user_state(message.from_user.id, "idle")
                self.bot.send_message(message.chat.id, f"Hi {message.from_user.username}! Send me a word in hebrew to get started")


        @self.bot.message_handler(commands=["export"])
        def export(message: Message):
            if message.from_user:
                id = message.from_user.id

                user_flashcards = self.dbhandler.get_flashcards(id)
                deck = self.ankiHandler.new_deck(id, "new deck")
                deck = self.ankiHandler.add_flashcards(deck, user_flashcards)
                self.ankiHandler.export_deck(deck, f"deck_{id}.apkg")
                with open(f"deck_{id}.apkg", 'rb') as f:
                    self.bot.send_document(message.chat.id, f)


        @self.bot.message_handler(func=lambda message: True)
        def main_react(message: Message):
            if message.text is None or not message.from_user:
                return

            id = message.from_user.id
            print(f"got message from {id}")
            if self.dbhandler.get_user_state(id) == "idle":
                self.dbhandler.set_user_query_column(id, "from_tr", message.text)
                print(f"getting translations for {message.text}")
                translations = self.reversoHandler.get_translations(message.text)
                self.bot.send_message(
                    message.chat.id,
                    "Choose a translation:",
                    reply_markup=self.gen_translations_keyboard(translations)
                )
                self.dbhandler.set_user_state(id, "awaiting_translation_choice")

            elif self.dbhandler.get_user_state(id) == "awaiting_translation_choice":
                self.dbhandler.set_user_query_column(id, "to_tr", message.text)
                print(f"getting contexts for {message.text}")
                contexts = self.reversoHandler.get_contexts(self.dbhandler.get_user_query_column(id, "from_tr"), message.text)
                self.bot.send_message(
                    message.chat.id,
                    "\n\n".join(" - ".join(i) for i in contexts),
                    reply_markup=self.gen_contexts_keyboard(contexts)
                )
                print(contexts)
                for i, context in enumerate(contexts):
                    print(f"adding context {i}")
                    self.dbhandler.add_user_context_option(id, i, context[0], context[1])
                self.dbhandler.set_user_state(id, "awaiting_context_choice")


            elif self.dbhandler.get_user_state(id) == "awaiting_context_choice":
                if message.text:
                    contexts = self.dbhandler.get_user_context_option_by_display_num(id, message.text)
                    self.dbhandler.set_user_query_column(id, "from_context", contexts[0])
                    self.dbhandler.set_user_query_column(id, "to_context", contexts[1])

                    resulting_row = self.dbhandler.get_user_query(id)

                    self.bot.send_message(message.chat.id, f"Translated {resulting_row[0]} to {resulting_row[1]}")
                    self.bot.send_message(message.chat.id, f"Example: {resulting_row[2]}\n\n{resulting_row[3]}")

                    self.dbhandler.add_flashcard(id, resulting_row[0], resulting_row[1], resulting_row[2], resulting_row[3])
                    self.bot.send_message(message.chat.id, "Added flashcard.", reply_markup=ReplyKeyboardRemove())

                self.dbhandler.reset_user_query(id)
                self.dbhandler.reset_user_context_options(id)
                self.dbhandler.set_user_state(id, 'idle')

    def gen_translations_keyboard(self, translations):
        markup = ReplyKeyboardMarkup(row_width = 1, one_time_keyboard=True)
        for translation in translations:
            markup.add(KeyboardButton(translation))

        return markup

    def gen_contexts_keyboard(self, contexts):
        markup = ReplyKeyboardMarkup(row_width = 6, one_time_keyboard=True)
        for i in range(len(contexts)):
            markup.add(KeyboardButton(str(i)))

        return markup

    def run(self):
        self.bot.infinity_polling()
