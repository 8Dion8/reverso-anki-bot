import sqlite3 as sql

class DBHandler:
    def __init__(self):
        self.DB_PATH = "master.db"
        self.init_db()

    def init_db(self):
        self.conn = sql.connect(self.DB_PATH, check_same_thread=False)
        cur = self.conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY,
                username TEXT
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS UserSettings (
                user_id   INTEGER,
                key       TEXT,
                value     TEXT,
                PRIMARY KEY (user_id, key),
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS UserState (
                user_id   INTEGER PRIMARY KEY,
                state     TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS UserQuery (
                user_id   INTEGER PRIMARY KEY,
                from_tr   TEXT,
                to_tr     TEXT,
                from_context TEXT,
                to_context TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS UserContexts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id   INTEGER,
                user_display_num INTEGER,
                from_context   TEXT,
                to_context TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS Words (
                word_id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id              INTEGER,
                word                 TEXT,
                from_tr              TEXT,
                to_tr                TEXT,
                from_context         TEXT,
                to_context           TEXT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id)
            );
        ''')

        self.conn.commit()

    def reset_user_query(self, user_id):
        cur = self.conn.cursor()

        cur.execute('''
            UPDATE UserQuery
            SET from_tr = '', to_tr = '', from_context = '', to_context = ''
            WHERE user_id = ?;
        ''', (user_id,))

        self.conn.commit()

    def set_user_query_column(self, user_id, column_name, value):
        cur = self.conn.cursor()

        cur.execute(f'''
            UPDATE UserQuery
            SET {column_name} = ?
            WHERE user_id = ?;
        ''', (value, user_id))

        self.conn.commit()

    def get_user_query_column(self, user_id, column_name):
        cur = self.conn.cursor()

        cur.execute(f'''
            SELECT {column_name}
            FROM UserQuery
            WHERE user_id = ?;
        ''', (user_id,))

        return cur.fetchone()[0]

    def get_user_query(self, user_id):
        cur = self.conn.cursor()

        cur.execute('''
            SELECT from_tr, to_tr, from_context, to_context
            FROM UserQuery
            WHERE user_id = ?;
        ''', (user_id,))

        return cur.fetchone()

    def add_user_context_option(self, user_id, display_num, from_context, to_context):
        cur = self.conn.cursor()

        cur.execute('''
            INSERT INTO UserContexts (user_id, user_display_num, from_context, to_context)
            VALUES (?, ?, ?, ?);
        ''', (user_id, display_num, from_context, to_context))

        self.conn.commit()

    def get_user_context_option_by_display_num(self, user_id, display_num):
        cur = self.conn.cursor()

        cur.execute('''
            SELECT from_context, to_context
            FROM UserContexts
            WHERE user_id = ? AND user_display_num = ?;
        ''', (user_id, display_num))

        return cur.fetchone()

    def reset_user_context_options(self, user_id):
        cur = self.conn.cursor()

        cur.execute('''
            DELETE FROM UserContexts
            WHERE user_id = ?;
        ''', (user_id,))

        self.conn.commit()

    def get_user_list(self):
        cur = self.conn.cursor()

        cur.execute('''
            SELECT user_id, username
            FROM Users;
        ''')

        return cur.fetchall()

    def init_user(self, user_id, username):
        cur = self.conn.cursor()

        cur.execute('''
            INSERT INTO Users (user_id, username)
            VALUES (?, ?);
        ''', (user_id, username))

        cur.execute('''
            INSERT INTO UserState (user_id, state)
            VALUES (?, ?);
        ''', (user_id, 'idle'))

        cur.execute('''
            INSERT INTO UserSettings (user_id, key, value)
            VALUES (?, ?, ?);
        ''', (user_id, 'language_from', 'hebrew'))

        cur.execute('''
            INSERT INTO UserSettings (user_id, key, value)
            VALUES (?, ?, ?);
        ''', (user_id, 'language_to', 'english'))

        cur.execute('''
            INSERT INTO UserQuery (user_id, from_tr, to_tr, from_context, to_context)
            VALUES (?, '', '', '', '');
        ''', (user_id,))

        self.conn.commit()

    def set_user_state(self, user_id, state):
        cur = self.conn.cursor()

        cur.execute('''
            UPDATE UserState
            SET state = ?
            WHERE user_id = ?;
        ''', (state, user_id))

        self.conn.commit()

    def get_user_state(self, user_id):
        cur = self.conn.cursor()

        cur.execute('''
            SELECT state
            FROM UserState
            WHERE user_id = ?;
        ''', (user_id,))

        return cur.fetchone()[0]

    def add_flashcard(self, user_id, from_tr, to_tr, from_context, to_context):
        cur = self.conn.cursor()

        cur.execute('''
            INSERT INTO Words (user_id, from_tr, to_tr, from_context, to_context)
            VALUES (?, ?, ?, ?, ?);
        ''', (user_id, from_tr, to_tr, from_context, to_context))

        self.conn.commit()

    def get_flashcards(self, user_id):
        cur = self.conn.cursor()

        cur.execute('''
            SELECT from_tr, to_tr, from_context, to_context
            FROM Words
            WHERE user_id = ?;
            ''', (user_id,))

        return cur.fetchall()

    def set_user_setting(self, user_id, key, value):
        cur = self.conn.cursor()

        cur.execute('''
            UPDATE UserSettings
            SET value = ?
            WHERE user_id = ? AND key = ?;
        ''', (value, user_id, key))

        self.conn.commit()

    def get_user_setting(self, user_id, key):
        cur = self.conn.cursor()

        cur.execute('''
            SELECT value
            FROM UserSettings
            WHERE user_id = ? AND key = ?;
            ''', (user_id, key))

        return cur.fetchone()[0]
