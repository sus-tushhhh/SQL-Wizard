import sqlite3
import streamlit as st
import pandas as pd
import tempfile
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

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
        #st.info("Keep database empty to use sample database or use {table_name} as placeholder")
        uploaded_file = st.file_uploader(label=":green[Upload database : ]",
                                         type=[".db", ".sqlite", ".sqlite3"])
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_path = tmp_file.name

        if uploaded_file:
            conn = sqlite3.Connection(temp_path)
            cursor = conn.cursor()
        else:
            conn = sqlite3.Connection("assets/sample.db")
            cursor = conn.cursor()

        if cursor:
            table_names = pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table';", conn)
            selected_table = st.selectbox(label=":green[Select Table : ]",
                                          options=table_names['name'].to_list() + ["{table_name} as placeholder"])

    with st.container(border=True):
        st.subheader(":red[Danger Zone : ]")
        auto_commit_toggle = st.toggle(label=":red[Auto Commit Changes]")


# BackEnd ===================================================================================================
gemini = ChatGoogleGenerativeAI(
    model=model_name,
    google_api_key=GOOGLE_API_KEY
)

agent = create_agent(
    model=gemini
)

@st.cache_data
def query_generator(query, _agent=agent) -> list[str]:
    prompt = f"""
        You are a Natural Language to SQL query generator agent
        create your answer in three parts 
        first generate SQL command based on user query
        second you have to explain the query to the user
        third provide a tip for the user to enhace, optimize the query
        don't write headings of parts and don't write ```sql
        always use semicolons where ever needed and highlight words in explanationa and tip using ``

        don't answer anything other than SQL queries if user says anything out of context just say
        "I can only generate SQL Queries"

        User query = {query}, table = {selected_table}
    """

    if selected_table != "{table_name} as placeholder":
        prompt += "\nSample Records : " + pd.read_sql_query(f"Select * from {selected_table} limit 5", conn).to_string()

        prompt += "\nTable columns : " + pd.read_sql_query(f"PRAGMA table_info({selected_table})", conn).to_string()

    response = _agent.invoke({'messages' : [{'role': 'user', 'content': prompt}]})
    answer = response['messages'][-1].content[-1]['text']

    if answer == "I can only generate SQL Queries":
        return [answer]
    else:
        return answer.split('\n\n')


    

# FrontEnd ==================================================================================================
if selected_table != "{table_name} as placeholder":
    with st.container(border=True):
        st.subheader(":orange[Table Preview (upto 10 records) : ]")
        table_preview_placeholder = st.empty()
        table_preview_placeholder.dataframe(data=pd.read_sql_query(f"""
                                                            Select * from {selected_table}  
                                                            LIMIT 10""", conn),
                                            hide_index=True)

        
def update_table(query: str):
    if query.startswith("SELECT"):
        table_preview_placeholder.dataframe(data=pd.read_sql_query(query[:-1] + " LIMIT 10;", conn),
                                            hide_index=True)
    else:
        table_preview_placeholder.dataframe(data=pd.read_sql_query(f"""
                                                                    Select * from {selected_table}  
                                                                    LIMIT 10""", conn),
                                                    hide_index=True)


with st.container(border=True):
    st.subheader(":green[Enter Query in Natural Language : ]")
    prompt_input_section, prompt_button_section = st.columns([10,2], vertical_alignment='bottom')
    with prompt_input_section:
        prompt_input = st.text_input("", label_visibility='collapsed',
                                     placeholder=r"Example : Increment 10% salary for all employees")
    with prompt_button_section:
        prompt_button = st.button("Generate ✨", width='stretch', type='secondary')

    info_placeholder = st.empty()


if not prompt_input:
    info_placeholder.info("Please enter a query.")
elif len(prompt_input) < 5:
    info_placeholder.info("Query must be longer than 5 letters.")


elif prompt_input or prompt_button:
    with st.spinner("Generating ..."):
        if response := query_generator(query=prompt_input):
            if len(response) > 1:
                sql_query, explaination_text, tip = response

                code_section, explaination = st.columns([3, 2]) 
                with code_section:
                    with st.container(border=True, height='stretch'):
                        st.subheader(":violet[AI Generated Query : ]")
                        st.code(sql_query, language='sql', height='stretch')

                with explaination:
                    with st.container(border=True, height='stretch'):
                        st.subheader(":violet[Explanation : ]")
                        st.write(explaination_text)

                with st.container(border=True):
                    st.subheader(":violet[Pro Tip : ]")
                    st.write(tip)

                if selected_table != "{table_name} as placeholder":
                    update_table(sql_query)

            else:
                st.warning(response[0])


if selected_table != "{table_name} as placeholder":
    if not auto_commit_toggle:
        left, middle, right = st.columns(3)
        with right:
            commit_button = st.button("Commit Changes", type='primary', width="stretch")
    else:
        left, middle = st.columns(2)

    with left:
        execute_button = st.button("Execute Query", type='secondary', width="stretch")
    with middle:
        rollback_button = st.button("Rollback", type='secondary', width="stretch")
    