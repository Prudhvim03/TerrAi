import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from utils.tava_utils import tava_search
from utils.vector_utils import get_vector_db
from prompts.prompts import SYSTEM_PROMPT

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)

def get_rag_answer(question, chat_history=None):
    vectordb = get_vector_db()
    docs = vectordb.similarity_search(question, k=2)
    vector_context = "\n".join([doc.page_content for doc in docs]) if docs else ""
    web_info = tava_search(question)
    prompt = SYSTEM_PROMPT
    if vector_context:
        prompt += f"\n\nRelevant previous knowledge:\n{vector_context}"
    if web_info:
        prompt += f"\n\nLatest web information:\n{web_info}"
    messages = [
        SystemMessage(content=prompt),
        HumanMessage(content=question)
    ]
    response = llm.invoke(messages)
    answer = response.content.strip()
    if web_info:
        answer += f"\n\n**Web Sources:**\n{web_info}"
    return f"**AI Guidance:**\n{answer}"
