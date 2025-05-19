import os
import streamlit as st
from dotenv import load_dotenv
from agents.chat_agent import get_rag_answer
from agents.voice_agent import voice_agent
from agents.image_agent import analyze_image
from prompts.prompts import (
    MAIN_TITLE, SUBTITLE, META_KEYWORDS, META_RESPONSE,
    SELF_QA_TRIGGERS, SELF_QA_PROMPT, FARMING_KEYWORDS
)

load_dotenv()

with open("static/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

futuristic_logo_svg = """<svg width="72" height="72" ...> ... </svg>"""  # Use your SVG from paste.txt

st.markdown(f'<div class="futuristic-logo">{futuristic_logo_svg}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-title">{MAIN_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">{SUBTITLE}</div>', unsafe_allow_html=True)

def is_meta_query(q): return any(kw in q.lower() for kw in META_KEYWORDS)
def is_selfqa_query(q): return any(trigger in q.lower() for trigger in SELF_QA_TRIGGERS)
def is_farming_question(q): return any(word in q.lower() for word in FARMING_KEYWORDS)
def get_self_qa(question):
    from langchain_groq import ChatGroq
    from langchain_core.messages import SystemMessage, HumanMessage
    llm = ChatGroq(model="llama3-70b-8192", api_key=os.getenv("GROQ_API_KEY"))
    prompt = SELF_QA_PROMPT.format(question=question)
    messages = [
        SystemMessage(content="You are a helpful Indian farming assistant."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    return response.content.strip()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask about farming, soil, pests, irrigation, or anything in Indian agriculture…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        if is_meta_query(prompt):
            st.markdown(META_RESPONSE)
            st.session_state.messages.append({"role": "assistant", "content": META_RESPONSE})
        elif is_selfqa_query(prompt):
            prev_user_msg = next((m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"), None)
            if prev_user_msg:
                st.markdown("**Other questions you may have:**")
                self_qa = get_self_qa(prev_user_msg)
                st.markdown(self_qa)
                st.session_state.messages.append({"role": "assistant", "content": self_qa})
            else:
                st.markdown("Please ask a farming question first, then I can suggest more questions.")
        elif not is_farming_question(prompt):
            response = (
                "🙏 Sorry, I can only answer questions related to farming, agriculture, or agri-studies. "
                "If you are a farmer, student, or agriculturalist, please ask about crops, soil, weather, pest management, agri-careers, etc."
            )
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            with st.spinner("Consulting AI experts and searching the latest info..."):
                rag_answer = get_rag_answer(prompt)
                st.markdown(rag_answer)
                st.session_state.messages.append({"role": "assistant", "content": rag_answer})

if st.button("🎤 Voice Assistant"):
    with st.spinner("Listening..."):
        voice_response = voice_agent()
        st.markdown(f"**Voice Agent:** {voice_response}")
        st.session_state.messages.append({"role": "assistant", "content": voice_response})

uploaded_img = st.file_uploader("Upload a crop image for analysis", type=["jpg", "png"])
if uploaded_img:
    img_result = analyze_image(uploaded_img)
    st.markdown(img_result)
    st.session_state.messages.append({"role": "assistant", "content": img_result})

st.markdown(
    "<div style='text-align:center; color:#8d6e63; margin-top:2rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi • May 2025"
    "</div>",
    unsafe_allow_html=True
)
