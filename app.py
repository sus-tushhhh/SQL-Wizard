import sqlite3
import streamlit as st

# Configuration =============================================================================================
st.set_page_config(page_title="SQL Wizard", page_icon="🔮", layout="wide", initial_sidebar_state="expanded")
st.title("🔮 SQL Wizard &nbsp;|&nbsp; :violet[AI Query Generator]", text_alignment="center")
st.write("")


st.sidebar.title(":violet[Configuration]", text_alignment='center')
GOOGLE_API_KEY = st.sidebar.text_input(":green[Enter Google API Key: ]", type='password') or st.secrets.api_key.GOOGLE_API_KEY


model_name = st.sidebar.selectbox(":green[Select Model Name: ]",
                                  options=['gemini-3.5-flash-lite', 'gemini-3.5-flash', 'gemini-3.1-flash-lite'],
                                  index=0)
# BackEnd ===================================================================================================



# FrontEnd ==================================================================================================
with st.container(border=True, horizontal_alignment="right"):
    st.subheader(":green[Enter Query in Natural Language : ]")
    prompt_input_section, prompt_button_section = st.columns([10,2], vertical_alignment='bottom')
    with prompt_input_section:
        prompt_input = st.text_input("", label_visibility='collapsed',
                                     placeholder=r"Example : Increment 10% salary for all employees")
    with prompt_button_section:
        prompt_button = st.button("Generate ✨", width='stretch', type='primary')

    info_placeholder = st.empty()


if prompt_button:
    if not prompt_input:
        info_placeholder.info("Please enter a query.")
    elif len(prompt_input) < 5:
        info_placeholder.info("Query must be longer than 5 letters.")

    else:
        code_section, explaination = st.columns([3, 2]) 

        with code_section:
            with st.container(border=True, height='stretch'):
                st.subheader(":green[AI Generated Query : ]")
                with st.spinner("Generating ..."):
                    sql_query = """
                        UPDATE your_table_name
                        SET your_column_name = date(your_column_name, 'unixepoch');
                    """.replace("  ", "")

                    st.code(sql_query, language='sql', height='stretch')

        with explaination:
            with st.container(border=True, height='stretch'):
                st.subheader(":green[Explanation : ]")
                st.code("""Hello""", language=None, height='stretch')
    