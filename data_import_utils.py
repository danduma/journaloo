import dateparser
import re
import pypandoc
import json
import datetime


def adapt_metadata_chroma(metadata):
    """
    Given a metadata dictionary, adapt it to the format expected by chromadb.
    :param metadata:
    :return:
    """
    adapted_metadata = {}
    for key, value in metadata.items():
        if isinstance(value, datetime.datetime):
            adapted_metadata[key] = value.timestamp()
        else:
            adapted_metadata[key] = value
    return adapted_metadata


def extract_entries_from_file(filename):
    """
    Given a (text) file, extract all the entries from it.

    :param filename:
    :return: dict(date, title, text)
    """
    output = pypandoc.convert_file(filename, 'markdown')
    entries = split_markdown_file(output)
    return entries


def split_markdown_file(text):
    """
    Given a markdown file, extract all the entries from it.
    :param filename:
    :return:
    """
    entries = []

    regex = "\s*(\d{2}-\d{2}-\d{2})[:\-]?\s*(.+)?\n[-=]{6,100}\n\s*([\s\S]+?)(?=(\d{2}-\d{2}-\d{2})[:\-]?\s*(\w+)?\n[-=]{6,100})"

    for match in re.finditer(regex, text):
        date = dateparser.parse(match.group(1))
        new_entry = {
            'metadata': {
                'date': date,
            },
            'title': match.group(2),
            'text': match.group(3)
        }
        entries.append(new_entry)
    return entries

# def split_json_file(doc_data):
#     entries = []
#     current_entry = None
#
#     for element in doc_data['blocks']:
#         if element['t'] == 'Header':
#             # Extract header level and text
#             header_level = element['c'][0]
#             header_text = element['c'][2][0]['c']
#             match = re.search(r'(\d+-\d+-\d+)', header_text)
#             if match:
#                 date = dateparser.parse(match.group(1))
#             else:
#                 date = dateparser.parse(header_text)
#
#             new_entry = {
#                 'date': date,
#                 'header_text': header_text
#             }
#             entries.append(new_entry)
#     return entries
