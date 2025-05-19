import os
import streamlit as st
from dotenv import load_dotenv

from agents.chat_agent import get_rag_answer
from agents.voice_agent import voice_agent
from agents.image_agent import analyze_image
from prompts.prompts import (
    MAIN_TITLE, SUBTITLE, META_KEYWORDS, META_RESPONSE,
    SELF_QA_TRIGGERS, FARMING_KEYWORDS
)

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

# --- Display chat history in modern bubbles ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f'<div class="chat-bubble user-bubble">{message["content"]}</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-bubble ai-bubble">{message["content"]}</div>',
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)

# --- Floating input bar with icons ---
st.markdown("""
<div class="floating-input-bar">
    <form action="" method="post" enctype="multipart/form-data" id="chat-form">
        <label for="image-upload" class="icon-btn" title="Attach image">
            <span>📎</span>
            <input type="file" id="image-upload" name="image-upload" accept="image/*" style="display:none">
        </label>
        <button type="button" class="icon-btn" id="voice-btn" title="Voice input">🎤</button>
        <input type="text" id="chat-input" name="chat-input" placeholder="Type your message..." autocomplete="off" class="chat-text-input">
        <button type="submit" class="icon-btn" id="send-btn" title="Send">➡️</button>
    </form>
</div>
<script>
const input = window.parent.document.querySelector('#chat-input');
if(input) input.focus();
</script>
""", unsafe_allow_html=True)

# --- Handle input (Streamlit can't handle JS form, so use st.text_input and st.file_uploader) ---
st.markdown('<div style="height: 80px"></div>', unsafe_allow_html=True)  # Spacer for floating bar

# Hidden Streamlit input for backend logic
with st.form("chatbot-form", clear_on_submit=True):
    chat_input = st.text_input("", key="chat_input_real", placeholder="Type your message...", label_visibility="collapsed")
    image_file = st.file_uploader("", type=["jpg", "png"], label_visibility="collapsed", key="image_upload_real")
    voice_btn = st.form_submit_button("🎤 Voice")
    send_btn = st.form_submit_button("Send")

# --- Handle Voice Input ---
if voice_btn:
    with st.spinner("Listening..."):
        user_text, ai_voice_response = voice_agent(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": user_text})
        st.session_state.messages.append({"role": "assistant", "content": ai_voice_response})
        st.experimental_rerun()

# --- Handle Image Input ---
if image_file:
    img_result = analyze_image(image_file)
    st.session_state.messages.append({"role": "user", "content": "[Image uploaded]"})
    st.session_state.messages.append({"role": "assistant", "content": img_result})
    st.experimental_rerun()

# --- Handle Chat Input ---
if send_btn and chat_input:
    st.session_state.messages.append({"role": "user", "content": chat_input})
    # Routing logic
    if is_greeting(chat_input):
        response = get_greeting_response()
    elif is_meta_query(chat_input):
        response = META_RESPONSE
    elif is_selfqa_query(chat_input):
        prev_user_msg = next((m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"), None)
        response = get_rag_answer(prev_user_msg, st.session_state.messages) if prev_user_msg else "Please ask a farming question first."
    elif is_language_request(chat_input):
        lang = is_language_request(chat_input)
        prev_user_msg = next((m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"), None)
        response = get_rag_answer(prev_user_msg, st.session_state.messages, language=lang) if prev_user_msg else "Please ask a farming question first, then request translation."
    elif not is_farming_question(chat_input, st.session_state.messages):
        response = (
            "🙏 Sorry, I can only answer questions related to farming, agriculture, or agri-studies. "
            "If you are a farmer, student, or agriculturalist, please ask about crops, soil, weather, pest management, agri-careers, etc."
        )
    else:
        with st.spinner("Consulting AI experts and searching the latest info..."):
            response = get_rag_answer(chat_input, st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.experimental_rerun()

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#8d6e63; margin-top:2rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi • May 2025"
    "</div>",
    unsafe_allow_html=True
)
