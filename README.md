<h1 align="center">
📓 Memoaire
</h1>

Talk to your memories. 

## 🔧 Features

- Import your journal in several formats
    - currently only DayOne XML is supported
- Find interesting stuff in your journal.
- Think qualitative rather than quantitative questions for now 

## Installation

1. Clone the repository📂

```bash
git clone git@github.com:danduma/memoaire.git
cd memoaire
```

2. Install dependencies📦

A [virtualenv](https://pypi.org/project/virtualenv/) is not required but recommended:

```bash
virtualenv venv
source venv/bin/activate
```

Make sure you have Python 3.7+ and [pip](https://pip.pypa.io/en/stable/) installed.

```bash
pip install -r requirements.txt
```

3. Run the app🚀

```bash
streamlit run run.py
```

This should launch a browser window with the app running. 

## Getting Started

1. Get your OpenAI API key from [here](https://platform.openai.com/).
2. In the app, go to Settings and paste your API key.
3. Go to the "Journal data" tab and import your journal: select the right format, manually input the path to the directory or file, and click "Import".
4. Go to the "Chat" tab and start talking to your memories!
