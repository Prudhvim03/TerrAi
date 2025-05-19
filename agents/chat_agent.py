# agents/chat_agent.py

import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from prompts.prompts import SYSTEM_PROMPT

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

def get_rag_answer(question):
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=question)
    ]
    response = llm.invoke(messages)
    return response.content.strip()
