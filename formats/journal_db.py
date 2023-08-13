# from pysqlcipher3 import dbapi2 as sqlite
import sqlite3 as sqlite
import json


class JournalDatabase:
    def __init__(self, db_path, password=None):
        self.conn = sqlite.connect(db_path)
        self.c = self.conn.cursor()

        if password:
            self.c.execute(f"PRAGMA key='{password}'")

        # Create tables if they don't exist
        self.c.execute('''CREATE TABLE IF NOT EXISTS journal 
                          (id INTEGER PRIMARY KEY, date TEXT, title TEXT, body TEXT, metadata TEXT)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS entities
                          (id INTEGER PRIMARY KEY, name TEXT, description TEXT, forms TEXT)''')
        self.conn.commit()

    def add_entry(self, entry: dict):
        date, title, body, metadata = entry['date'], entry['title'], entry['body'], entry['metadata']
        metadata_json = json.dumps(metadata)
        self.c.execute("INSERT INTO journal (date, title, body, metadata) VALUES (?, ?, ?, ?)",
                       (date, title, body, metadata_json))
        self.conn.commit()

    def get_entry(self, entry_id):
        self.c.execute("SELECT * FROM journal WHERE id=?", (entry_id,))
        return self.c.fetchone()

    def delete_entry(self, entry_id):
        self.c.execute("DELETE FROM journal WHERE id=?", (entry_id,))
        self.conn.commit()

    def iterate_entries(self):
        """
        This function iterates over all entries in the journal database.
        It executes a SQL query to select all entries from the journal table.
        Then it fetches all rows from the query result and for each row, it creates a dictionary with the row data.
        The dictionary is then yielded for further processing.
        """

        self.c.execute("SELECT * FROM journal")
        entries = []
        for row in self.c.fetchall():
            entry = {
                "id": row[0],
                "date": row[1],
                "title": row[2],
                "body": row[3],
                "metadata": json.loads(row[4])
            }
            yield entry

    def create_entity(self, name, description, forms):
        self.c.execute("INSERT INTO entities (name, description, forms) VALUES (?, ?, ?)",
                       (name, description, forms))
        self.conn.commit()

    def delete_entity(self, entity_id):
        self.c.execute("DELETE FROM entities WHERE id=?", (entity_id,))
        self.conn.commit()

    def delete_all(self):
        self.c.execute("DELETE FROM journal")
        self.c.execute("DELETE FROM entities")
        self.conn.commit()

    def close(self):
        self.conn.close()

    def count_entries(self):
        """
        Count the number of entries in the journal database.
        """
        self.c.execute("SELECT COUNT(*) FROM journal")
        count = self.c.fetchone()[0]
        return count

    def add_entries_bulk(self, entries):
        """
        Add a list of journal entries in bulk.

        :param entries: List of dictionaries representing journal entries.
                        Each dictionary must contain the keys `date`, `title`, `body`, and `metadata`.
        """
        # Prepare the query
        query = "INSERT INTO journal (date, title, body, metadata) VALUES (?, ?, ?, ?)"

        # Prepare the data
        data_to_insert = [(entry['date'], entry['title'], entry['body'], json.dumps(entry.get('metadata', {}))) for
                          entry in
                          entries]

        # Execute the insert query in bulk
        self.c.executemany(query, data_to_insert)
        self.conn.commit()

# ... rest of the code ...
