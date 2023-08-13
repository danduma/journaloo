from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.parser import parse
import json
import re


# Read the EPUB file
def read_epub(file_path):
    return epub.read_epub(file_path)


# Get chapter by ID
def get_chapter_by_id(book, chapter_id):
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT and chapter_id in item.get_id():
            return item.get_body_content().decode('utf-8')
    return None


def get_all_chapters(book):
    chapters = []
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            chapters.append(item.get_body_content().decode('utf-8'))
    return chapters


# Parse a date string and return it in ISO format
def parse_date(date_str, current_year):
    try:
        parsed_date = parse(date_str, fuzzy=True).date()
        if parsed_date.year > 1998:
            parsed_date = parsed_date.replace(year=current_year)
        return parsed_date.isoformat()
    except:
        return date_str


def is_date(string):
    pattern = r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), (January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}(st|nd|rd|th)"
    return bool(re.match(pattern, string))


# Extract journal entries from the chapter content
def extract_entries_from_chapter(chapter_content, current_year):
    entries = []
    soup = BeautifulSoup(chapter_content, 'html.parser')
    current_date = None
    current_body = ""
    for p_tag in soup.find_all('p'):
        date_tag = p_tag.find('em')
        if date_tag and is_date(date_tag.get_text().strip()):
            date_text = date_tag.get_text().strip()
            if current_date and current_body.strip():
                current_body = current_body.strip()

                pattern = r"(?P<date>[A-Za-z]+, [A-Za-z]+ \d+[a-z]*)\s?(: ?(?P<title>.+?))?\n(?:\s|\n)*(?P<body>.+)"
                match = re.search(pattern, current_body, re.DOTALL)

                if match:
                    entries.append({
                        "date": parse_date(current_date, current_year),
                        "title": match.group("title").strip() if match.group("title") else "",
                        "body": match.group("body").strip()
                    })
                else:
                    entries.append({
                        "date": parse_date(current_date, current_year),
                        "title": "",
                        "body": current_body.strip()
                    })

            current_date = date_text
            current_body = ""
        current_body += p_tag.get_text() + "\n"

    if current_date and current_body.strip():
        entries.append({
            "date": parse_date(current_date, current_year),
            "title": "",
            "body": current_body.strip(),
            "metadata": {}

        })
    return entries


# Extract journal entries from all chapters
def extract_entries(chapters, book):
    all_entries = []
    current_year = 1988
    for chapter_id in range(1, 12):
        chapter_content = get_chapter_by_id(book, f"c{chapter_id:02d}")
        entries = extract_entries_from_chapter(chapter_content, current_year)
        all_entries += entries
        current_year += 1
    return all_entries


class PalinEPubConverter:
    """
    A class that converts the Palin diaries EPUB file into a JSON file.
    """

    def __init__(self, epub_file_path):
        self.epub_file_path = epub_file_path
        self.entities = {}
        self.entries = []

    def read_epub(self):
        book = read_epub(self.epub_file_path)
        chapters = [get_chapter_by_id(book, f"c{chapter_id:02d}") for chapter_id in range(1, 12)]
        whos_who_chapter = [chapter for chapter in chapters if "Who in the Diaries" in chapter]
        whos_who_chapter = whos_who_chapter[0] if len(whos_who_chapter) > 0 else None

        entities = self.extract_entities(whos_who_chapter)
        all_entries = extract_entries(chapters, book)
        return all_entries, entities

    def iterate_over_entries(self):
        all_entries, entities = self.read_epub()
        for entry in all_entries:
            yield entry

    def convert_to_jsonl(self, entries_file_path, entities_file_path):
        all_entries, entities = self.read_epub()
        self.save_entries_to_jsonl(all_entries, entries_file_path)
        # self.save_entities_to_jsonl(entities, entities_file_path)

    # Markup the text with entity IDs
    def markup_text_with_entities(self, text, entities):
        sorted_entities = sorted(entities, key=lambda x: -len(x["name"]))
        for entity in sorted_entities:
            text = text.replace(entity["name"], f'<data entity="{entity["id"]}">{entity["name"]}</data>')
        return text

    def entity_link_all(self, text, entities):
        for entry in self.entries:
            marked_up_body = self.markup_text_with_entities(entry["body"], entities)
            entry["body"] = marked_up_body

    def save_entities_to_jsonl(self, entities, file_path):
        with open(file_path, 'w') as file:
            for entity in entities:
                file.write(json.dumps(entity) + '\n')

    # Save entries to a JSONL file with marked-up text
    def save_entries_to_jsonl(self, entries, file_path):
        with open(file_path, 'w') as file:
            for entry in entries:
                file.write(json.dumps(entry) + '\n')

    # Extract entities (recurring characters) from the "Who's Who in the Diaries" section
    def extract_entities(self, chapter):
        entities = []
        if not chapter:
            return entities
        soup = BeautifulSoup(chapter, 'html.parser')
        for p_tag in soup.find_all('p'):
            text = p_tag.get_text().strip()
            if text:
                name_and_desc = text.split(',', 1)
                name = name_and_desc[0].strip()
                desc = name_and_desc[1].strip() if len(name_and_desc) > 1 else ''
                entity_id = name.lower().replace(' ', '-').replace(',', '')
                relation = "acquaintance"
                category = "person"

                entities.append({
                    "name": name,
                    "type": category,
                    "full_text": text,
                    "id": entity_id
                })
        return entities


# this file should convert the epub to Day One JSON format
def main():
    converter = PalinEPubConverter("../data/palin_1988-1998_travelling_work.epub")
    converter.convert_to_jsonl("../data/palin_entities.jsonl", "../data/palin_entries.jsonl")


if __name__ == '__main__':
    main()
