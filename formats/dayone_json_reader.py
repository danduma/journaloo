import json
import zipfile
import re
from collections import OrderedDict

from formats.base_reader import BaseReader

FIELDS_TO_IGNORE = ['richText']


class DayOneJSONReader(BaseReader):
    """
    A class for reading Day One zipped JSON files
    """

    def read(self, path):
        return load_dayone_json(path)


def convert_camel_case_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def load_dayone_json(zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for filename in zip_ref.namelist():
            if filename.endswith('.json'):
                with zip_ref.open(filename) as file:
                    data = json.load(file)
                    for entry in data['entries']:
                        new_entry = OrderedDict()
                        new_entry['date'] = entry['creationDate']

                        if not entry.get('text'):
                            continue

                        text_lines = entry['text'].split('\n')
                        new_entry['title'] = text_lines[0].lstrip('# ')
                        new_entry['body'] = '\n'.join(text_lines[1:])

                        metadata = {}
                        for key, value in entry.items():
                            if key not in ['creationDate', 'text'] and key not in FIELDS_TO_IGNORE:
                                metadata[convert_camel_case_to_snake_case(key)] = value

                        new_entry['metadata'] = metadata

                        yield new_entry


def main():
    # Replace 'file.xml' with the name of your XML file
    reader = DayOneJSONReader()
    for data in reader.read_directory('../data', file_mask='dayone.zip'):
        print(json.dumps(data, indent=4))


if __name__ == '__main__':
    main()
