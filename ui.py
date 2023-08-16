import streamlit as st

"""
#444655
#343542
#ffffff
"""


def custom_css():
    custom_css = """
        <style>
          body {
            --primary-color: #ffffff;
            --background-color: #343542;
            --secondary-background-color: #444655;
            --bs-body-bg: var(--background-color);
            
            --text-color: #ffffff;
            # background-color: var(--secondary-background-color);
            # --font: "sans-serif";
          }

          .stApp {
            color: var(--text-color);
            # font-family: var(--font);
            background-color: var(--secondary-background-color);
          }

          .stChatFloatingInputContainer {
            background-color: var(--secondary-background-color);
          }
          
          textarea {
            background-color: var(--background-color);
            }

          button.st-c7 {
            background-color: var(--secondary-background-color);
          }

        .streamlit-expander {
            padding: 2px;
            }
            
        .menu {
            background-color: var(--secondary-background-color);
            }
            
        .app {
            background-color: var(--secondary-background-color);
            }
            

           .block-container {
                padding-top: 1rem;
                # padding-bottom: 5rem;
                padding-left: 5rem;
                padding-right: 5rem;
            }
        </style>
        """

    # Inject the custom CSS
    st.markdown(custom_css, unsafe_allow_html=True)


def configure_ui():
    custom_css()
