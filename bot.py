import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, Message, ReplyKeyboardRemove

from db import DBHandler
from anki import AnkiHandler
from reverso import ReversoHandler
import reverso

import logging

class Bot:
    def __init__(self,  token, reversoHandler: ReversoHandler, ankiHandler: AnkiHandler, dbhandler: DBHandler):
        self.bot = telebot.TeleBot(token, parse_mode='Markdown')
        self.reversoHandler = reversoHandler
        self.ankiHandler = ankiHandler
        self.dbhandler = dbhandler
        self.VALID_LANGUAGES_DISPLAY = ", ".join(f'`{i.capitalize()}`' for i in sorted(reverso.VALID_LANGUAGES))
        
        logging.info("Bot up and running!")


        def _help(user_id, chat_id):
            language_from = self.dbhandler.get_user_setting(user_id, "language_from")
            self.bot.send_message(chat_id, f'''
Just send me a message in {language_from} to add a flashcard, or use the following commands:\n
/help - display this message
/cancel - cancel current operation/menu
/language_set - set languages to translate from/to
/export - export flashcards to an Anki deck file (`.apkg`)
/list - list all of your flashcards
/delete - delete a flashcard
            ''', parse_mode="HTML")

        @self.bot.message_handler(commands=["help"])
        def help(message: Message):
            if message.from_user:
                logging.info(f"Command /help from {message.from_user.id}")
                _help(message.from_user.id, message.chat.id)

        @self.bot.message_handler(commands=["start"])
        def start(message: Message):
            if message.from_user:
                logging.info(f"Command /start from {message.from_user.id}")
                id = message.from_user.id
                user_ids = [i[0] for i in self.dbhandler.get_user_list()]
                if id in user_ids:
                    logging.info(f"User {id} exists")
                else:
                    logging.info(f"New user {id}")
                    self.dbhandler.init_user(id, message.from_user.username)

                logging.info("Resetting user state")
                self.dbhandler.reset_user_query(id)
                self.dbhandler.reset_user_context_options(id)
                self.dbhandler.set_user_state(id, "idle")
                _help(id, message.chat.id)


        @self.bot.message_handler(commands=["export"])
        def export(message: Message):
            if message.from_user:
                logging.info(f"Command /export from {message.from_user.id}")
                id = message.from_user.id

                user_flashcards = self.dbhandler.get_flashcards(id)
                deck = self.ankiHandler.new_deck(id, "new deck")
                deck = self.ankiHandler.add_flashcards(deck, user_flashcards)
                self.ankiHandler.export_deck(deck, f"deck_{id}.apkg")
                with open(f"deck_{id}.apkg", 'rb') as f:
                    self.bot.send_document(message.chat.id, f)

        @self.bot.message_handler(commands=["list"])
        def list(message: Message):
            logging.info(f"Command /list from {message.from_user.id}")
            flashcards = self.dbhandler.get_flashcards(message.from_user.id)
            flashcard_display = self.flashcard_display(flashcards, include_context=True) 
            if flashcard_display:
                self.bot.send_message(message.chat.id, flashcard_display)
            else:
                self.bot.send_message(message.chat.id, "You have no flashcards at the moment.")

        @self.bot.message_handler(commands=["cancel"])
        def cancel(message: Message):
            if message.from_user:
                logging.info(f"Command /cancel from {message.from_user.id}")
                id = message.from_user.id
                self.dbhandler.reset_user_query(id)
                self.dbhandler.reset_user_context_options(id)
                self.dbhandler.set_user_state(id, 'idle')
                self.bot.send_message(message.chat.id, "Operation cancelled.")

        @self.bot.message_handler(commands=["delete", "remove"])
        def delete(message: Message):
            if message.from_user:
                id = message.from_user.id
                logging.info(f"Command /delete from {message.from_user.id}")
                self.bot.send_message(message.chat.id, "Please send the number of flashcard you want to delete:")
                flashcards = self.dbhandler.get_flashcards(id)
                flashcard_display = self.flashcard_display(flashcards) 
                self.bot.send_message(message.chat.id, flashcard_display)

                self.dbhandler.set_user_state(id, 'awaiting_deletion_choice')

        @self.bot.message_handler(commands=["language_set"])
        def language_set(message: Message):
            if message.from_user:
                logging.info(f"Command /language_set from {message.from_user.id}")
                id = message.from_user.id
                self.dbhandler.set_user_state(id, 'language_set_from')
                self.bot.send_message(message.chat.id, "Please enter the language you want to translate **from**:\n"+self.VALID_LANGUAGES_DISPLAY)

        @self.bot.message_handler(func=lambda message: True)
        def main_react(message: Message):
            if message.text is None or not message.from_user:
                return

            id = message.from_user.id
            logging.info(f"Generic message from {id}")
            if self.dbhandler.get_user_state(id) == "idle":
                self.dbhandler.set_user_query_column(id, "from_tr", message.text)
                translations = self.reversoHandler.get_translations(
                    message.text,
                    lang_to = self.dbhandler.get_user_setting(id, "language_to"),
                    lang_from = self.dbhandler.get_user_setting(id, "language_from")
                )
                logging.info(f"Sending translation options to {id}")
                self.bot.send_message(
                    message.chat.id,
                    "Choose a translation:",
                    reply_markup=self.gen_translations_keyboard(translations)
                )
                self.dbhandler.set_user_state(id, "awaiting_translation_choice")

            elif self.dbhandler.get_user_state(id) == "awaiting_translation_choice":
                self.dbhandler.set_user_query_column(id, "to_tr", message.text) 
                lang_to = self.dbhandler.get_user_setting(id, "language_to")
                lang_from = self.dbhandler.get_user_setting(id, "language_from")
                contexts = self.reversoHandler.get_contexts(
                    self.dbhandler.get_user_query_column(id, "from_tr"),
                    message.text,
                    lang_to = lang_to,
                    lang_from = lang_from
                )
                formatted = []
                for context in contexts:
                    formatted_context = f'{self.bold_occurrences(context[0], lang_to)} - {self.bold_occurrences(context[1], lang_from)}'
                    formatted.append(formatted_context)
                logging.info(f"Sending context options to {id}") 
                self.bot.send_message(
                    message.chat.id,
                    "\n\n".join(formatted),
                    reply_markup=self.gen_contexts_keyboard(contexts)
                )
                for i, context in enumerate(contexts):
                    self.dbhandler.add_user_context_option(id, i, context[0], context[1])
                self.dbhandler.set_user_state(id, "awaiting_context_choice")

            elif self.dbhandler.get_user_state(id) == "awaiting_context_choice":
                if message.text:
                    contexts = self.dbhandler.get_user_context_option_by_display_num(id, message.text)
                    self.dbhandler.set_user_query_column(id, "from_context", contexts[0])
                    self.dbhandler.set_user_query_column(id, "to_context", contexts[1])

                    resulting_row = self.dbhandler.get_user_query(id)

                    logging.info(f"Confirming flashcard for {id}")
                    self.bot.send_message(message.chat.id, f"Translated **{resulting_row[0]}** to **{resulting_row[1]}**")
                    self.bot.send_message(message.chat.id, f"Example: {resulting_row[2]}\n\n{resulting_row[3]}")

                    self.dbhandler.add_flashcard(id, resulting_row[0], resulting_row[1], resulting_row[2], resulting_row[3])
                    self.bot.send_message(message.chat.id, "Added flashcard.", reply_markup=ReplyKeyboardRemove())

                self.dbhandler.reset_user_query(id)
                self.dbhandler.reset_user_context_options(id)
                self.dbhandler.set_user_state(id, 'idle')

            elif self.dbhandler.get_user_state(id) == "language_set_from":
                language_set_from = message.text.lower()
                if language_set_from not in reverso.VALID_LANGUAGES:
                    self.bot.send_message(message.chat.id, "Invalid choice.\nHint: you can just press on a language from the provided list to copy it to your clipboard.")
                    return
                else:
                    self.dbhandler.set_user_setting(id, "language_from", language_set_from)
                    self.bot.send_message(message.chat.id, f"Language set to {language_set_from}")
                    self.bot.send_message(message.chat.id, "Please enter the language you want to translate TO:\n"+self.VALID_LANGUAGES_DISPLAY)
                    self.dbhandler.set_user_state(id, 'language_set_to')

            elif self.dbhandler.get_user_state(id) == "language_set_to":
                language_set_to = message.text.lower()
                if language_set_to not in reverso.VALID_LANGUAGES or language_set_to == self.dbhandler.get_user_setting(id, "language_from"):
                    self.bot.send_message(message.chat.id, "Invalid choice.\nHint: you can just press on a language from the provided list to copy it to your clipboard.")
                    return
                else:
                    self.dbhandler.set_user_setting(id, "language_to", language_set_to)
                    self.bot.send_message(message.chat.id, f"Language set to {language_set_to}. Done!")
                    self.dbhandler.set_user_state(id, 'idle')

            elif self.dbhandler.get_user_state(id) == "awaiting_deletion_choice":
                choice = message.text
                flashcards = self.dbhandler.get_flashcards(id)
                if not choice.isnumeric() or int(choice) < 0 or int(choice) > len(flashcards):
                    self.bot.send_message(message.chat.id, "Please choose a valid flashcard number.")
                    return

                self.dbhandler.delete_flashcard(id, flashcards[int(choice)])          
                self.bot.send_message(message.chat.id, "Flashcard successfully deleted.")
                self.dbhandler.set_user_state(id, "idle")

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

    def flashcard_display(self, flashcards, include_context = False):
        if include_context:
            flashcard_display = "\n".join(f'{i}. {card[0]} - {card[1]}\n__{card[2]}__\n__{card[3]}__\n' for i, card in enumerate(flashcards)) 
        else: 
            flashcard_display = "\n".join(f'{i}. {card[0]} - {card[1]}' for i, card in enumerate(flashcards)) 

        return flashcard_display
            
    def bold_occurrences(self, text, word):
        return text.replace(word, f"**{word}**")
    

    def run(self):
        self.bot.infinity_polling()
