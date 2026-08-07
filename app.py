import sqlite3
import streamlit as st
import pandas as pd
import tempfile
import base64
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

# Configuration =============================================================================================
st.set_page_config(page_title="SQL Wizard", page_icon="🔮", layout="wide", initial_sidebar_state="expanded")
st.title("🔮 SQL Wizard &nbsp;|&nbsp; :rainbow[AI Query Generator]", text_alignment="center")
st.write("")

def set_bg_from_local(image_file):
    with open(image_file, "rb") as f:
        encoded_string = base64.b64encode(f.read()).decode()
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
set_bg_from_local("assets/harry_bg.webp")


def set_sidebar_background(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] {{
            background-image: url("data:image/png;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
set_sidebar_background("assets/bg.avif")


with st.sidebar:
    st.title(":orange[⚙️Configuration] ", text_alignment="center")

    with st.container(border=True):
        st.subheader(":blue[Model : ]")
        GOOGLE_API_KEY = st.text_input(label=":green[Enter Google API Key : ]", 
                                       type='password') or st.secrets.api_key.GOOGLE_API_KEY

        model_name = st.selectbox(label=":green[Select Model Name : ]",
                                  options=['gemini-3.5-flash-lite', 'gemini-3.5-flash', 'gemini-3.1-flash-lite'],
                                  index=0)

    def clear_cache():
        st.cache_resource.clear()
        st.cache_data.clear()


    with st.container(border=True):
        st.subheader(":blue[Database : ]")
        #st.info("Keep database empty to use sample database or use {table_name} as placeholder")
        uploaded_file = st.file_uploader(label=":green[Upload database : ]",
                                         type=[".db", ".sqlite", ".sqlite3"],
                                         on_change=clear_cache)

        @st.cache_resource
        def get_conn() -> sqlite3.Connection:
            if uploaded_file:
                buf = uploaded_file.getbuffer()
            else:
                with open("assets/sample.db", "rb") as f:
                    buf = f.read()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_file:
                tmp_file.write(buf)
                temp_path = tmp_file.name

            if "temp_path" not in st.session_state:
                st.session_state.temp_path = temp_path
            
            conn = sqlite3.Connection(temp_path, check_same_thread=False)
        
            return conn


        conn = get_conn()
        cursor = conn.cursor()

        uploaded_file = None

        if cursor:
            table_names = pd.read_sql_query("SELECT name FROM sqlite_schema WHERE type='table';", conn)
            selected_table = st.selectbox(label=":green[Select Table : ]",
                                          options=["{table_name} as placeholder"] + table_names['name'].to_list(),
                                          index=0,
                                          on_change=clear_cache)

    with st.container(border=True):
        st.subheader(":red[Critical : ]")
        auto_commit_toggle = st.toggle(label=":red[Auto Commit Changes]")


if selected_table != "{table_name} as placeholder":
    with st.container(border=True):
        header, download = st.columns([8, 2], vertical_alignment="bottom")
        with header:
            st.subheader(":violet[📋 Table Preview (top 5 records) : ]")
        with download:
            with open(st.session_state.temp_path, 'rb') as f:
                st.download_button("Download Database",
                                   data=f.read(),
                                   file_name="sql_wizard.db",
                                   mime="application/octet-stream",
                                   width='stretch',
                                   icon=":material/download:")

        table_preview_placeholder = st.empty()
        table_preview_placeholder.dataframe(data=pd.read_sql_query(f"""
                                                            Select * from {selected_table}  
                                                            LIMIT 5""", conn),
                                            hide_index=True)

# BackEnd ===================================================================================================
gemini = ChatGoogleGenerativeAI(
    model=model_name,
    google_api_key=GOOGLE_API_KEY
)

agent = create_agent(
    model=gemini
)

def update_table(query: str):
    if query.startswith('SELECT'):
        query = query[: -1] + " LIMIT 5;"

    table_preview_placeholder.dataframe(data=pd.read_sql_query(query, conn),
                                        hide_index=True)
    
def rollback_sql():
    conn.rollback()
    update_table(f"SELECT * from {selected_table};")


def commit_sql():
    conn.commit()


def execute_sql(sql_query):
    try:
        cursor.execute(sql_query)
        if auto_commit_toggle:
            commit_sql() 

        if cursor.fetchall():
            if selected_table != "{table_name} as placeholder":
                update_table(sql_query)
            
        else:
            if selected_table != "{table_name} as placeholder":
                update_table(f"SELECT * from {selected_table};") 

        return [True, "Successfully executed query"]

    except Exception as e:
        rollback_sql()
        return [False, "Changes were rolled back", sql_query, e]




@st.cache_data
def query_generator(query, _agent=agent) -> list[str]:
    prompt = f"""
        You are a Natural Language to SQL query generator agent
        create your answer in Three parts 
        first generate SQL command based on user query
        second you have to explain the query to the user
        third provide a tip for the user to enhace, optimize the query
        don't write headings of parts and don't write ```sql
        use `` to escape column names for only reserved keywords not for other column names
        always use semicolons where ever needed and highlight words in explanationa and tip using ``

        don't answer anything other than SQL queries if user says anything out of context just say
        "I can only generate SQL Queries based on the selected table"

        User query = {query}, table = {selected_table}
    """

    if selected_table != "{table_name} as placeholder":
        prompt += "\nSample Records : " + pd.read_sql_query(f"Select * from {selected_table} limit 5;", conn).to_string()

        prompt += "\nTable columns : " + pd.read_sql_query(f"PRAGMA table_info({selected_table});", conn).to_string()

    response = _agent.invoke({'messages' : [{'role': 'user', 'content': prompt}]})
    answer = response['messages'][-1].content[-1]['text']

    if answer == "I can only generate SQL Queries":
        return [answer]
    else:
        return answer.split('\n\n')



# FrontEnd ==================================================================================================
with st.container(border=True):
    st.subheader(":violet[🔍 Enter Query in Natural Language : ]")
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
              
                with st.container(border=True, height='stretch'):
                    st.subheader(":violet[✨ AI Generated Query : ]")
                    st.code(sql_query, language='sql', height='stretch')

                explaination_section, tip_section = st.columns(2)
                with explaination_section:
                    with st.container(border=True, height='stretch'):
                        st.subheader(":violet[📖 Explanation : ]")
                        st.write(explaination_text)

                with tip_section:
                    with st.container(border=True):
                        st.subheader(":violet[💡 Pro Tip : ]")
                        st.write(tip)

            else:
                st.warning(response[0])


if selected_table != "{table_name} as placeholder":
    if not auto_commit_toggle:
        left, middle, right = st.columns(3)
        with right:
            commit_button = st.button("Commit Changes", type='primary', width="stretch")
            if commit_button:
                commit_sql()
                st.success("Changes committed.")
    else:
        left, middle = st.columns(2)

    with left:
        execute_button = st.button("Execute Query", type='secondary', width="stretch")
        if execute_button:
            status = execute_sql(sql_query)
            if status[0]:
                st.success(status[1])
            else:
                st.error(f"{status[1]}: {status[3]}")

    with middle:
        rollback_button = st.button("Rollback", type='secondary', width="stretch", disabled=auto_commit_toggle)
        if rollback_button:
            rollback_sql()
            st.info("Changes rolled back.")
    