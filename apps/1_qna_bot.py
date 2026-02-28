from dotenv import load_dotenv
load_dotenv()
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st

llm=ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    )

st.title("🤖 AskBuddy - AI Qna Bot")
st.markdown("My Qna Bot with Langchain and Gemini")

if "messages" not in st.session_state:
    st.session_state.messages = []

for messege in st.session_state.messages:
    role=messege["role"]
    content=messege["content"]
    st.chat_message(role).markdown(content)

# que="Who is PM of India"

# while True:
#     query=input("User: ")
#     if query.lower() in ["quit","exit","bye"]:
#         print ("Good Bye 👋")
#         break
#     res=llm.invoke(query)
#     print("AI: ", res.content, "\n")

query=st.chat_input("Ask anything ?")
if query:
    st.session_state.messages.append({"role":"user", "content":query})
    st.chat_message("user").markdown(query)
    res=llm.invoke(query)
    st.chat_message("ai").markdown(res.content)
    st.session_state.messages.append({"role":"ai", "content":res.content})
