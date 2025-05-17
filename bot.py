import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, Message


class Bot:
    def __init__(self,  token, reversoHandler):
        self.bot = telebot.TeleBot(token)
        self.POSSIBLE_STATES = {
            "AWAITING_USER": 1,
            "AWAITING_TRANSLATION_CHOICE": 2,
            "AWAITING_CONTEXT_CHOICE": 3,
        }
        self.reset_states()

        @self.bot.message_handler(commands=["start"])
        def start(message: Message):
            self.STATE = self.POSSIBLE_STATES["AWAITING_USER"]
            self.bot.send_message(message.chat.id, "Hi! Send me a word in english to get started")


        @self.bot.message_handler(func=lambda message: True)
        def main_react(message: Message):

            if self.STATE == self.POSSIBLE_STATES["AWAITING_USER"]:
                self.CURRENT_TRANSLATION_SOURCE = message.text
                translations = reversoHandler.get_translations(self.CURRENT_TRANSLATION_SOURCE)
                print(translations)
                self.bot.send_message(
                    message.chat.id,
                    "Choose a translation:",
                    reply_markup=self.gen_translations_keyboard(translations)
                )
                self.STATE = self.POSSIBLE_STATES["AWAITING_TRANSLATION_CHOICE"]

            elif self.STATE == self.POSSIBLE_STATES["AWAITING_TRANSLATION_CHOICE"]:
                self.CURRENT_TRANSLATION_TO = message.text
                contexts = reversoHandler.get_contexts(self.CURRENT_TRANSLATION_SOURCE, self.CURRENT_TRANSLATION_TO)
                self.bot.send_message(
                    message.chat.id,
                    "\n\n".join(" - ".join(i) for i in contexts),
                    reply_markup=self.gen_contexts_keyboard(contexts)
                )
                self.CURRENT_CONTEXT_OPTIONS = contexts
                self.STATE = self.POSSIBLE_STATES["AWAITING_CONTEXT_CHOICE"]

            elif self.STATE == self.POSSIBLE_STATES["AWAITING_CONTEXT_CHOICE"]:
                if message.text:
                    self.CURRENT_CONTEXT = self.CURRENT_CONTEXT_OPTIONS[int(message.text)]
                    self.bot.send_message(message.chat.id, f"Translated {self.CURRENT_TRANSLATION_SOURCE} to {self.CURRENT_TRANSLATION_TO}")
                    self.bot.send_message(message.chat.id, f"Example: {self.CURRENT_CONTEXT[0]}\n\n{self.CURRENT_CONTEXT[1]}")

                self.reset_states()

    def reset_states(self):
        self.STATE = self.POSSIBLE_STATES["AWAITING_USER"]
        self.CURRENT_TRANSLATION_SOURCE = ""
        self.CURRENT_TRANSLATION_TO = ""
        self.CURRENT_CONTEXT = []
        self.CURRENT_CONTEXT_OPTIONS = []

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
