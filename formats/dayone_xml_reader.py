import xml.etree.ElementTree as ET
import json

from formats.base_reader import BaseReader

KEYS_TO_IGNORE = ["Region", "Generation Date"]


class DayOneXMLReader(BaseReader):
    """
    A class for reading Day One XML files to JSON
    """

    def read(self, path):
        return [load_dayone_xml(path)]


def load_dayone_xml(filename):
    with open(filename, 'r') as file:
        xml_string = file.read()

    root = ET.fromstring(xml_string)
    result = {
        'date': None,
        'title': None,
        'body': None,
        'metadata': {}
    }

    entry_text = None

    for child in root.find('dict'):
        if child.tag == 'key':
            key_name = child.text
        else:
            if key_name == 'Creation Date':
                result['date'] = child.text
            elif key_name == 'Entry Text':
                entry_text = child.text
                result['title'], result['body'] = entry_text.split('\n', 1)
                result['body'] = result['body'].strip()
            else:
                result['metadata'][key_name] = extract_value(child)

    result = transform_dict(result)
    return result


def extract_value(element):
    if element.tag == 'string':
        return element.text
    elif element.tag == 'real':
        return float(element.text)
    elif element.tag == 'false':
        return False
    elif element.tag == 'true':
        return True
    elif element.tag == 'array':
        return [extract_value(child) for child in element]
    elif element.tag == 'dict':
        sub_dict = {}
        sub_key = None
        for child in element:
            if child.tag == 'key':
                sub_key = child.text
            else:
                sub_dict[sub_key] = extract_value(child)
        return sub_dict
    else:
        return None


def transform_dict(data):
    # Function to handle key transformation
    def transform_key(key):
        if key == "Time Zone":
            return "tz"
        return key.lower().replace(" ", "_")

    # Recursive function to iterate through dictionaries
    def process(obj):
        if isinstance(obj, dict):
            return {transform_key(key): process(value) for key, value in obj.items() if key not in KEYS_TO_IGNORE}
        elif isinstance(obj, list):
            return [process(item) for item in obj]
        else:
            return obj

    return process(data)


def main():
    # Replace 'file.xml' with the name of your XML file
    reader = DayOneXMLReader()
    for data in reader.read_directory('../data', file_mask='*.doentry'):
        print(json.dumps(data, indent=4))


if __name__ == '__main__':
    main()
