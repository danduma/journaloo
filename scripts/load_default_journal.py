from pathlib import Path
from config import SETTINGS
from formats.palin_epub_reader import PalinEPubConverter
from formats.journal_db import JournalDatabase
from journal_index import JournalIndex

current_dir: Path = Path(__file__).parent if "__file__" in locals() else Path.cwd()
db_path: Path = current_dir.parent / SETTINGS['db_path']
vector_path: Path = current_dir.parent / SETTINGS['vector_path']

def main():
    # journal = JournalDatabase(db_path.as_posix())
    # journal.delete_all()
    # converter = PalinEPubConverter("../data/palin_1988-1998_travelling_work.epub")
    # entries, entities = converter.read_epub()
    # journal.add_entries_bulk(entries)
    index = JournalIndex(db_path.as_posix(), vector_path)
    index.create_index()

    # converter.convert_to_jsonl("../data/palin_entities.jsonl", "../data/palin_entries.jsonl")

if __name__ == '__main__':
    main()
