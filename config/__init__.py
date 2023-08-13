import json
from os.path import exists

DEFAULT_SETTINGS = {
    'db_path': "db/journal.db",
    'vector_path': "index/",
    'vector_db_provider': 'faiss',
    'text_embedding_model': 'BAAI/bge-base-en',
    'llm_model': 'gpt-4',
    'top_k': 6,
    'import_path': "",
    'import_format': "DayOne XML",
    'watch_path': False,
}



def load_settings(settings_filename='config/settings.json'):
    settings = DEFAULT_SETTINGS

    if exists(settings_filename):
        with open(settings_filename, 'r') as f:
            settings = json.load(f)

    for key in DEFAULT_SETTINGS:
        if key not in settings:
            settings[key] = DEFAULT_SETTINGS[key]

    return settings


def save_settings(settings_filename='config/settings.json'):
    with open('config/settings.json', 'w') as f:
        json.dump(settings_filename, f, indent=4)

SETTINGS = load_settings()
