import streamlit as st
from streamlit_option_menu import option_menu

from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from langchain.prompts import MessagesPlaceholder
# from langsmith import Client
from formats.journal_db import JournalDatabase
from journal_index import JournalIndex
from src.styles.menu_styles import FOOTER_STYLES, HEADER_STYLES
from src.utils.lang import en
from ui import configure_ui
from import_data import import_journal_from

from config import save_settings, SETTINGS

# import streamlit.components.v1 as components
import os

if SETTINGS["openai_api_key"]:
    os.environ["OPENAI_API_KEY"] = SETTINGS["openai_api_key"]

st.set_page_config(
    page_title="📓 memoaire",
    page_icon="📓",
    layout="centered",
    initial_sidebar_state="auto",
)

configure_ui()

EMBEDDING_MODELS_OPTIONS = [
    "BAAI/bge-large-en",
    "BAAI/bge-base-en",
    "gte-large",
    "gte-base",
    "e5-large-v2",
    "bge-small-en",
    "instructor-xl",
    "instructor-large",
    "e5-base-v2",
    "multilingual-e5-large",
    "e5-large",
    "gte-small"
]

LLM_OPTIONS: list[str] = [
    "gpt-4",
    "gpt-3.5-turbo",
]

LANG_EN: str = "En"

# selected_lang = option_menu(
#     menu_title=None,
#     options=[LANG_EN],
#     icons=["globe2"],
#     menu_icon="cast",
#     default_index=0,
#     orientation="horizontal",
#     styles=HEADER_STYLES
# )

# langsmith
# client = Client()

# --- GENERAL SETTINGS ---
PAGE_ICON: str = "💡"

# folder_selector = components.declare_component("st-folder-selector", path="st-folder-selector")

# folder_name = folder_selector()

# if folder_name:
#     st.write(f"Selected folder: {folder_name}")

"# 📓 memoaire"


# @st.cache_resource(ttl="2h")
def configure_retriever():
    index = JournalIndex(SETTINGS['db_path'], SETTINGS['vector_path'])
    return index.as_retriever(search_kwargs={"k": SETTINGS["top_k"]})


# def send_feedback(run_id, score):
#     client.create_feedback(run_id, "user_score", score=score)


def page_settings():
    data_tab, advanced_tab = st.tabs(
        ["Journal data", "Advanced"]
    )

    journaldb = JournalDatabase(SETTINGS['db_path'])

    with data_tab:
        # Form 1
        with st.form(key='existing_index_form'):
            st.markdown('#### Existing index')
            n_entries = journaldb.count_entries()  # Assuming 10 entries
            st.markdown(f'Currently contains: {n_entries} entries')

            # Confirm deletion
            delete_button = st.form_submit_button(label='Delete index')
            if delete_button:
                journaldb.delete_all()
                index = JournalIndex(SETTINGS['db_path'], SETTINGS['vector_path'])
                index.delete_index()
                st.snow()
                st.success('Index deleted!')
        # Form 2
        with st.form(key='form2'):
            st.markdown('#### Import Journal')

            FORMAT_OPTIONS = ['DayOne JSON', 'DayOne XML', 'Markdown']
            # Tabs
            import_format = st.selectbox('Choose format', FORMAT_OPTIONS,
                                         index=FORMAT_OPTIONS.index(SETTINGS['import_format']))

            # Path textbox
            import_path = st.text_input('Path to journal file (e.g. .zip) or directory (e.g. .dayone XML files))',
                                        value=SETTINGS.get('import_path', ''))

            # Checkbox
            # watch_folder = st.checkbox('Watch folder for changes')

            # Import button
            import_button = st.form_submit_button(label='Import')
            if import_button:
                with st.spinner('Importing journal...'):
                    convert_dict = {'DayOne JSON': 'dayone_json', 'DayOne XML': 'dayone_xml', 'Markdown': 'markdown'}
                    try:
                        num_entries = import_journal_from(import_path, convert_dict[import_format])
                        index = JournalIndex(SETTINGS['db_path'], SETTINGS['vector_path'])
                        index.create_index()
                        SETTINGS['import_path'] = import_path
                        SETTINGS['import_format'] = import_format
                        st.balloons()
                        st.success(f'{num_entries} entries imported from {import_path} in {import_format} format.')
                        save_settings(SETTINGS)
                    except Exception as e:
                        st.error(f'Error: {e}')
                        return

    with advanced_tab:
        with st.form(key='advanced_form'):
            st.markdown('#### Advanced Settings')

            # API key
            if SETTINGS['openai_api_key']:
                api_key = SETTINGS['openai_api_key']
            else:
                api_key = os.environ.get('OPENAI_API_KEY', '')
            api_key = st.text_input('OpenAI API key', value=api_key)

            # Dropdown for LLM model
            llm_model = st.selectbox('LLM model', LLM_OPTIONS, index=LLM_OPTIONS.index(SETTINGS['llm_model']))

            # Dropdown for embeddings model
            embeddings_model = st.selectbox(
                'Embeddings model',
                EMBEDDING_MODELS_OPTIONS,
                index=EMBEDDING_MODELS_OPTIONS.index(SETTINGS['text_embedding_model'])
            )

            # Slider for top-k
            top_k = st.slider('Top-k', min_value=3, max_value=10, value=SETTINGS['top_k'])

            # Submit button
            submit_button = st.form_submit_button(label='Submit')
            if submit_button:
                SETTINGS['openai_api_key'] = api_key
                SETTINGS['llm_model'] = llm_model
                SETTINGS['text_embedding_model'] = embeddings_model
                SETTINGS['top_k'] = top_k

                st.success(f'Selected LLM model: {llm_model}, '
                           f'Embeddings model: {embeddings_model}, '
                           f'Top-k: {top_k}')
                # Add code to handle the selected options


def page_chat():
    tool = create_retriever_tool(
        configure_retriever(),
        "search_journal",
        "Searches and returns documents from the user's personal journal. The user has been keeping a journal for years. You do not know anything about the user beyond what is in this, so if you are ever asked about the user's life or memories you should use this tool.",
    )

    tools = [tool]
    llm = ChatOpenAI(temperature=0, streaming=True, model="gpt-4")
    # llm = ChatOpenAI(temperature=0, streaming=True, model="gpt-3.5-turbo")
    message = SystemMessage(
        content=(
            "You are a helpful chatbot that helps the user interact with their memoirs and journal. You answering questions about the user's life to the best of your ability. "
            "Unless otherwise explicitly stated, assume that questions are about the user's memories as captured in their journal entries. "
            "If there is any ambiguity, you assume they are about that."
            "You never output 'Based on your journal entries', the user already knows this. Don't mention their journal, only the useful information relevant to the question."
        )
    )
    prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=message,
        extra_prompt_messages=[MessagesPlaceholder(variable_name="history")],
    )
    agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
    )
    memory = AgentTokenBufferMemory(llm=llm)
    starter_message = "Ask me anything about your journal!"
    if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
        st.session_state["messages"] = [AIMessage(content=starter_message)]

    for msg in st.session_state.messages:
        if isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        memory.chat_memory.add_message(msg)

    if prompt := st.chat_input(placeholder=starter_message):
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            st_callback = StreamlitCallbackHandler(st.container())
            response = agent_executor(
                {"input": prompt, "history": st.session_state.messages},
                callbacks=[st_callback],
                include_run_info=True,
            )
            st.session_state.messages.append(AIMessage(content=response["output"]))
            st.write(response["output"])
            memory.save_context({"input": prompt}, response)
            st.session_state["messages"] = memory.buffer
            run_id = response["__run"].run_id
            #
            # col_blank, col_text, col1, col2 = st.columns([10, 2, 1, 1])
            # with col_text:
            #     st.text("Feedback:")
            #
            # with col1:
            #     st.button("👍", on_click=send_feedback, args=(run_id, 1))
            #
            # with col2:
            #     st.button("👎", on_click=send_feedback, args=(run_id, 0))


def run_app():
    st.session_state.locale = en
    # match selected_lang:
    #     case "En":
    #         st.session_state.locale = en
    #     case _:
    #         st.session_state.locale = en
    selected_tab = option_menu(
        menu_title=None,
        options=[
            st.session_state.locale.tab_option0,
            st.session_state.locale.tab_option1,
        ],
        icons=["chat-square-text", "gear-fill"],  # https://icons.getbootstrap.com/
        menu_icon="cast",
        # default_index=0,
        orientation="horizontal",
        styles=FOOTER_STYLES
    )
    match selected_tab:
        case st.session_state.locale.tab_option0:
            page_chat()
        case st.session_state.locale.tab_option1:
            page_settings()


if __name__ == "__main__":
    run_app()
