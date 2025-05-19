import os
import streamlit as st
from dotenv import load_dotenv
from agents.chat_agent import get_rag_answer
from agents.voice_agent import voice_agent
from agents.image_agent import analyze_image

# --- Load environment variables ---
load_dotenv()

# --- Branding & CSS ---
futuristic_logo_svg = """<svg width="72" height="72" ...> ... </svg>"""  # Use your SVG here
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&display=swap');
        .stApp {background: linear-gradient(135deg, #fffde7 0%, #e8f5e9 100%);color: #37474f;}
        .futuristic-logo {display: flex;justify-content: center;align-items: center;margin-bottom: -8px;}
        .main-title {text-align: center;color: #689f38;font-size: 2.7rem;font-family: 'Orbitron', sans-serif;font-weight: bold;letter-spacing: 1.5px;text-shadow: 0 0 10px #fbc02d, 0 0 40px #fbc02d44;margin-bottom: 0.5rem;}
        .subtitle {text-align: center;color: #8d6e63;font-size: 1.1rem;margin-bottom: 2rem;font-family: 'Orbitron', sans-serif;}
    </style>
""", unsafe_allow_html=True)
st.markdown(f'<div class="futuristic-logo">{futuristic_logo_svg}</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🌾 Terrคi: The Futuristic AI Farming Guide</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Empowering Indian farmers with AI, real-time insights, and smart agriculture innovations</div>', unsafe_allow_html=True)

# --- Helper functions for meta/greetings/multilingual ---
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
    meta_keywords = ["who are you", "created", "your name", "developer", "model", "prudhvi", "about you"]
    return any(kw in q.lower() for kw in meta_keywords)

def handle_meta_query():
    return (
        "I am Terrคi, developed by Prudhvi, an engineer passionate about Indian agriculture. "
        "My mission is to empower Indian farmers, students, and agriculturalists with practical, region-specific guidance for every stage of cultivation, "
        "combining AI with real-time knowledge and innovation."
    )

def is_selfqa_query(q):
    triggers = [
        "other questions", "more questions", "what else", "related questions", "suggest more", "show more",
        "what else can i ask", "give me more questions"
    ]
    q_lower = q.strip().lower()
    return any(trigger in q_lower for trigger in triggers)

def is_language_request(q):
    return "in telugu" in q.lower() or "in hindi" in q.lower() or "in tamil" in q.lower() or "in kannada" in q.lower() or "in marathi" in q.lower()

def get_requested_language(q):
    for lang in ["telugu", "hindi", "tamil", "kannada", "marathi"]:
        if f"in {lang}" in q.lower():
            return lang
    return None

def is_farming_question(question, history):
    keywords = [
        "farm", "farmer", "agriculture", "crop", "soil", "irrigation", "weather",
        "pesticide", "fertilizer", "seed", "plant", "harvest", "yield", "agronomy",
        "horticulture", "animal husbandry", "disease", "pest", "organic", "sowing",
        "rain", "monsoon", "market price", "mandi", "tractor", "dairy", "farming",
        "agriculturist", "agriculturalist", "agri", "agronomist", "extension", "agri student",
        "agri career", "kisan", "polyhouse", "greenhouse", "micro irrigation", "crop insurance",
        "fpo", "farmer producer", "soil health", "farm loan", "krishi", "agriculture student"
    ]
    q = question.lower()
    if any(word in q for word in keywords):
        return True
    for msg in reversed(history):
        if msg["role"] == "user" and any(word in msg["content"].lower() for word in keywords):
            return True
    return False

# --- Chat Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display chat history ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Input: Chat, Voice, Image ---
col1, col2 = st.columns([6, 1])
with col1:
    prompt = st.chat_input("Ask about farming, soil, pests, irrigation, or anything in Indian agriculture…")
with col2:
    voice_button = st.button("🎤 Voice", use_container_width=True)
uploaded_file = st.file_uploader("Attach an image for analysis", type=["jpg", "png"], label_visibility="collapsed")

# --- Handle Voice Input ---
if voice_button:
    with st.spinner("Listening..."):
        voice_response = voice_agent()
        st.session_state.messages.append({"role": "user", "content": "[Voice input]"})
        st.session_state.messages.append({"role": "assistant", "content": voice_response})
        st.markdown(f"**Voice Agent:** {voice_response}")

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
            response = handle_meta_query()
        # Self QA
        elif is_selfqa_query(prompt):
            prev_user_msg = next((m["content"] for m in reversed(st.session_state.messages[:-1]) if m["role"] == "user"), None)
            response = get_rag_answer(prev_user_msg, st.session_state.messages) if prev_user_msg else "Please ask a farming question first."
        # Multilingual
        elif is_language_request(prompt):
            lang = get_requested_language(prompt)
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

