from formats.journal_db import JournalDatabase


def import_journal_from(path, format):
    jdb = JournalDatabase("db/journal.db")
    num_entries = 0
    if format == "dayone_json":
        raise NotImplementedError
    elif format == "dayone_xml":
        from formats.dayone_xml_reader import DayOneXMLReader
        converter = DayOneXMLReader()
        if "." not in path:
            for entry in converter.read_directory(path, '*.doentry'):
                jdb.add_entry(entry)
                num_entries += 1
        else:
            for entry in converter.read(path):
                jdb.add_entry(entry)
    else:
        raise ValueError(f"Unknown format {format}")
    return num_entries


def main():
    # import_journal_from("data/", "dayone_xml")
    from journal_index import JournalIndex
    index = JournalIndex('db/journal.db', 'index/')
    # index.create_index()

if __name__ == '__main__':
    main()
