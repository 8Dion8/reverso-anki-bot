import genanki
class AnkiHandler:

    def __init__(self):
        self.deck = genanki.Deck(
            deck_id=1234567890,
            name="Hebrew Deck"
        )
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

    def add_flashcard(self, word, translation, context, context_translation):
        note = genanki.Note(
            model=self.model,
            fields=[word, translation, context, context_translation]
        )
        self.deck.add_note(note)

    def export_deck(self, file_name):
        genanki.Package(self.deck).write_to_file(file_name)
