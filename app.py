import sqlite3
import streamlit as st
import pandas as pd
import tempfile

# Configuration =============================================================================================
st.set_page_config(page_title="SQL Wizard", page_icon="🔮", layout="wide", initial_sidebar_state="expanded")
st.title("🔮 SQL Wizard &nbsp;|&nbsp; :rainbow[AI Query Generator]", text_alignment="center")
st.write("")


with st.sidebar:
    st.title(":violet[⚙️Configuration] ", text_alignment="center")

    with st.container(border=True):
        st.subheader(":blue[Model Configuration : ]")
        GOOGLE_API_KEY = st.text_input(label=":green[Enter Google API Key : ]", 
                                       type='password') or st.secrets.api_key.GOOGLE_API_KEY

        model_name = st.selectbox(label=":green[Select Model Name : ]",
                                  options=['gemini-3.5-flash-lite', 'gemini-3.5-flash', 'gemini-3.1-flash-lite'],
                                  index=0)


    with st.container(border=True):
        st.subheader(":blue[Database Configuration : ]")
        uploaded_file = st.file_uploader(label=":green[Upload database : ]",
                                        type=[".db", ".sqlite", ".sqlite3"])
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_path = tmp_file.name

        table_names = []
        selected_table = st.selectbox(label=":green[Select Table : ]",
                                    options=table_names)

    with st.container(border=True):
        st.subheader(":red[Danger Zone : ]")
        auto_execute = st.toggle(label=":red[Auto Execute Query]")
# BackEnd ===================================================================================================
if uploaded_file:
    conn = sqlite3.Connection(temp_path)
    cursor = conn.cursor()

    cursor.execute("Select * from netflix_db limit 10")
    all_records = cursor.fetchall()


# FrontEnd ==================================================================================================
with st.container(border=True):
    st.subheader(":orange[Table Preview (upto 10 records) : ]")
    st.dataframe(data=pd.read_sql_query("""
                            Select * from netflix_db 
                            where director="Mike Flanagan" 
                            limit 10""", conn),
                hide_index=True)

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
    