from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent
import streamlit as st

db = SQLDatabase.from_uri("sqlite:///my_tasks.db")

db.run(""" 
    CREATE TABLE IF NOT EXISTS tasks(
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       title TEXT NOT NULL,
       description TEXT,
       status TEXT CHECK (status IN ('pending', 'in_progress', 'completed')) DEFAULT 'pending',
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
       ); 
    
""")

## llm, tool, memory, system_prompt

llmmodel=ChatGroq(model="openai/gpt-oss-20b",streaming=True)
toolkit =SQLDatabaseToolkit(db=db, llm=llmmodel)
tools= toolkit.get_tools()
memory= InMemorySaver()

system_prompt = """
You are a task management assistant that interacts with a SQL database containing a 'tasks

TASK RULES:
1. Limit SELECT queries to 18 results max with ORDER BY created_at DESC
2. After CREATE/UPDATE/DELETE, confirm with SELECT query
3. If the user requests a list of tasks, present the output in a structured table format to ensure a clean and organized display in the browser.

CRUD OPERATIONS:
    CREATE: INSERT INTO tasks(title, description, status)
    READ: SELECT * FRON tasks WHERE ... LIMIT 10
    UPDATE: UPDATE tasks SET status=? WHERE id=? OR title=?
    DELETE: DELETE FROM tasks WHERE id=? OR title=?
Table schema: id, title, description, status(pending/in_progress/completed), created_at.
"""

@st.cache_resource
def get_agent():
    agent=create_agent(
        model=llmmodel,
        tools=tools,
        checkpointer=memory,
        system_prompt=system_prompt
    )
    return agent

agent= get_agent()

st.subheader("SQL baised LLM-BOT")


if "messages" not in st.session_state:
    st.session_state.messages=[]

for message in st.session_state.messages:
    role=message["role"]
    content=message["content"]
    st.chat_message(role).markdown(content)

prompt =st.chat_input("Manage task through here")

if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"User", "content":prompt})
    with st.chat_message("ai"):
        with st.spinner("Processing.."):
            response =agent.invoke(
                {"messages":[{"role":"user", "content":prompt}]},
                {"configurable":{"thread_id":"1"}}
            )
            result = response["messages"][-1].content
            st.markdown(result)
            st.session_state.messages.append({"role":"AI", "content":result})
            # print("AI: ", result)
# while True:
#     query=input("User: ")
#     response =agent.invoke(
#         {"messages":[{"role":"user", "content":query}]},
#         {"configurable":{"thread_id":"1"}}
#     )
#     result = response["messages"][-1].content
#     print("AI: ", result)



# print("db TABLE created Successfully ✅")