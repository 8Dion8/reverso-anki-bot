import genanki
import logging

class AnkiHandler:

    def __init__(self):
        self.model = genanki.Model(
            model_id=987654321,
            name="Simple Model",
            fields=[
                {"name": "Word"},
                {"name": "Translation"},
                {"name": "Context"},
                {"name": "Context Translation"}
            ],
            templates=[
                {
                    "name": "Card 1",
                    "qfmt": "{{Word}}<br><br><i>{{Context}}</i>",
                    "afmt": "{{FrontSide}}<hr id='answer'>{{Translation}}<br><br><i>{{Context Translation}}</i>"
                },
                {
                    "name": "Card 2",
                    "qfmt": "{{Translation}}<br><br><i>{{Context Translation}}</i>",
                    "afmt": "{{FrontSide}}<hr id='answer'>{{Word}}<br><br><i>{{Context}}</i>"
                }
            ]
        )

    def new_deck(self, id, name):
        logging.info(f"New deck {id} \"{name}\"")
        deck = genanki.Deck(
            deck_id=id,
            name=name
        )

        return deck

    def add_flashcards(self, deck, data):
        logging.info(f"Adding {len(data)} cards to deck {deck.deck_id}")
        for card in data:
            deck.add_note(
                genanki.Note(
                    model = self.model,
                    fields = card
                )
            )

        return deck

    def export_deck(self, deck, file_name):
        logging.info(f"Exporting deck {deck.deck_id} to {file_name}")
        genanki.Package(deck).write_to_file(file_name)
