import os
import streamlit as st
from dotenv import load_dotenv

# Import your agents
from agents.chat_agent import get_rag_answer
from agents.voice_agent import voice_agent
from agents.image_agent import analyze_image

# Import prompts for greetings, meta, etc.
from prompts.prompts import (
    MAIN_TITLE, SUBTITLE, META_KEYWORDS, META_RESPONSE,
    SELF_QA_TRIGGERS, FARMING_KEYWORDS
)

# Load environment variables
load_dotenv()

# --- Branding & CSS ---
futuristic_logo_svg = """<svg width="72" height="72" ...> ... </svg>"""  # Use your SVG here
with open("static/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
st.markdown(f'<div class="futuristic-logo">{futuristic_logo_svg}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-title">{MAIN_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">{SUBTITLE}</div>', unsafe_allow_html=True)

# --- Helper functions ---
GREETINGS = ["hi", "hello", "hey", "namaste", "good morning", "good evening", "good afternoon"]

def is_greeting(text):
    return any(text.lower().strip().startswith(g) for g in GREETINGS)

def get_greeting_response():
    return (
        "👋 Hello! I am Terrคi, your AI farming assistant. "
        "Ask me anything about crops, soil, weather, pests, agri-markets, or even in your local language. "
        "How can I help you today?"
    )

def is_meta_query(q):
    return any(kw in q.lower() for kw in META_KEYWORDS)

def is_selfqa_query(q):
    return any(trigger in q.lower() for trigger in SELF_QA_TRIGGERS)

def is_language_request(q):
    for lang in ["telugu", "hindi", "tamil", "kannada", "marathi"]:
        if f"in {lang}" in q.lower():
            return lang
    return None

def is_farming_question(question, history):
    q = question.lower()
    if any(word in q for word in FARMING_KEYWORDS):
        return True
    for msg in reversed(history):
        if msg["role"] == "user" and any(word in msg["content"].lower() for word in FARMING_KEYWORDS):
            return True
    return False

# --- Session state for chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display chat history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Input section (Chat, Voice, Image) ---
col1, col2 = st.columns([6, 1])
with col1:
    prompt = st.chat_input("Ask about farming, soil, pests, irrigation, or anything in Indian agriculture…")
with col2:
    voice_btn = st.button("🎤 Voice", use_container_width=True)
uploaded_file = st.file_uploader("Attach an image for analysis", type=["jpg", "png"], label_visibility="collapsed")

# --- Handle Voice Input ---
if voice_btn:
    with st.spinner("Listening..."):
        user_text, ai_voice_response = voice_agent()
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.session_state.messages.append({"role": "assistant", "content": ai_voice_response})
        st.markdown(f"**Voice Agent:** {ai_voice_response}")

# --- Handle Image Input ---
if uploaded_file:
    img_result = analyze_image(uploaded_file)
    st.session_state.messages.append({"role": "user", "content": "[Image uploaded]"})
    st.session_state.messages.append({"role": "assistant", "content": img_result})
    st.markdown(img_result)

# --- Handle Chat Input ---
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        # Greetings
        if is_greeting(prompt):
            response = get_greeting_response()
        # Meta
        elif is_meta_query(prompt):
            response = META_RESPONSE
        # Self QA
        elif is_selfqa_query(prompt):
            prev_user_msg = next((m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"), None)
            response = get_rag_answer(prev_user_msg, st.session_state.messages) if prev_user_msg else "Please ask a farming question first."
        # Multilingual
        elif is_language_request(prompt):
            lang = is_language_request(prompt)
            prev_user_msg = next((m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"), None)
            response = get_rag_answer(prev_user_msg, st.session_state.messages, language=lang) if prev_user_msg else "Please ask a farming question first, then request translation."
        # Restrict to farming
        elif not is_farming_question(prompt, st.session_state.messages):
            response = (
                "🙏 Sorry, I can only answer questions related to farming, agriculture, or agri-studies. "
                "If you are a farmer, student, or agriculturalist, please ask about crops, soil, weather, pest management, agri-careers, etc."
            )
        # Main RAG
        else:
            with st.spinner("Consulting AI experts and searching the latest info..."):
                response = get_rag_answer(prompt, st.session_state.messages)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#8d6e63; margin-top:2rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi • May 2025"
    "</div>",
    unsafe_allow_html=True
)
