# LLM
# TOOL - Google Search Tool
# Agent
# Memory
# Streaming
# Web Interface

from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st

llmmodel=ChatGroq(model="openai/gpt-oss-20b",streaming=True)
search=GoogleSerperAPIWrapper()
Searchtool= [search.run]

if "memory" not in st.session_state:
    st.session_state.memory=MemorySaver()
    st.session_state.history=[]
# memory=MemorySaver()


agent=create_agent(
    model=llmmodel,
    tools=Searchtool,
    checkpointer=st.session_state.memory,
    system_prompt="You are an ai agent and search on google too"
)

#  Building interface
st.subheader("🗨️ Chat bot with Google Search Capability")


for message in st.session_state.history:
    role=message["role"]
    content=message["content"]
    st.chat_message(role).markdown(content)


query=st.chat_input("Ask me Anything ?")

# while True:

if query:
    st.chat_message("User").markdown(query)
    st.session_state.history.append({"role":"User", "content":query})

    response=agent.stream(
        {"messages":[{"role":"user", "content":query}]},
        {"configurable":{"thread_id":"1"}},
        stream_mode="messages"
    )

    # answer=response["messages"][-1].content
    # st.chat_message("AI").markdown(answer)

    # st.session_state.history.append({"role":"AI", "content":answer})

    ai_container=st.chat_message("AI")
    with ai_container:
        space=st.empty()

        message="" 

        for chunck in response:
            message=message+chunck[0].content
            space.write(message)

        st.session_state.history.append({"role":"AI", "content":message})
# print(response["messages"][-1].content)