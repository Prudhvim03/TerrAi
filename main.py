import os
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Set up LLM and Tavily Search
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

# --- Branding & CSS ---
with open("static/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

futuristic_logo_svg = """<svg width="72" height="72" viewBox="0 0 72 72" fill="none">
  <defs>
    <radialGradient id="soil" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#a1887f" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#fffde7" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="stem" x1="36" y1="18" x2="36" y2="60" gradientUnits="userSpaceOnUse">
      <stop stop-color="#689f38"/>
      <stop offset="1" stop-color="#388e3c"/>
    </linearGradient>
    <linearGradient id="grain" x1="0" y1="0" x2="0" y2="18" gradientUnits="userSpaceOnUse">
      <stop stop-color="#ffe082"/>
      <stop offset="1" stop-color="#fbc02d"/>
    </linearGradient>
  </defs>
  <ellipse cx="36" cy="54" rx="22" ry="10" fill="url(#soil)"/>
  <path d="M36 54 Q46 34 62 22 Q46 28 36 54" fill="#ffe082" opacity="0.92"/>
  <path d="M36 54 Q26 34 10 22 Q26 28 36 54" fill="#ffe082" opacity="0.92"/>
  <rect x="34" y="18" width="4" height="36" rx="2" fill="url(#stem)"/>
  <ellipse cx="36" cy="18" rx="7" ry="9" fill="url(#grain)" stroke="#fbc02d" stroke-width="1.5"/>
  <path d="M36 54 L36 68" stroke="#8d6e63" stroke-width="2"/>
  <circle cx="36" cy="68" r="2.5" fill="#8d6e63"/>
  <path d="M41 44 L53 51" stroke="#8d6e63" stroke-width="2"/>
  <circle cx="53" cy="51" r="2.2" fill="#8d6e63"/>
  <path d="M31 44 L19 51" stroke="#8d6e63" stroke-width="2"/>
  <circle cx="19" cy="51" r="2.2" fill="#8d6e63"/>
  <circle cx="36" cy="14" r="3" fill="#fbc02d" stroke="#ffe082" stroke-width="1"/>
  <text x="36" y="15.5" font-size="2.5" text-anchor="middle" fill="#388e3c" font-family="Orbitron">AI</text>
</svg>
"""

st.markdown(f'<div class="futuristic-logo">{futuristic_logo_svg}</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">🌾 Terrคi: The Futuristic AI Farming Guide</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Empowering Indian farmers with AI, real-time insights, and smart agriculture innovations</div>', unsafe_allow_html=True)

# --- Prompt logic ---
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

def is_farming_question(question):
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
    return any(word in q for word in keywords)

def get_rag_answer(question, use_tavily=False):
    system_prompt = (
        "You are an Indian agricultural expert specializing in farming. "
        "Give practical, region-specific, step-by-step advice using both your knowledge and the latest information from trusted Indian agricultural sources. "
        "Always explain in clear, simple language. If possible, mention local varieties, climate, and sustainable practices. "
        "If you don't know, say so and suggest how to find out."
    )
    web_snippets = ""
    if use_tavily:
        tavily_result = tavily_search.invoke({"query": question})
        if tavily_result and "results" in tavily_result:
            for idx, result in enumerate(tavily_result["results"], 1):
                web_snippets += f"\nSource {idx}: {result.get('title', '')}\n{result.get('content', '')}\nURL: {result.get('url', '')}\n"
    prompt_with_web = system_prompt + (f"\n\nWeb search results:\n{web_snippets}" if web_snippets else "")
    messages = [
        SystemMessage(content=prompt_with_web),
        HumanMessage(content=question)
    ]
    response = llm.invoke(messages)
    answer = response.content.strip()
    references = ""
    if web_snippets:
        references = "\n\n**Top Sources:**\n"
        for idx, result in enumerate(tavily_result["results"], 1):
            references += f"- [{result.get('title', 'Source')}]({result.get('url', '')})\n"
    return f"**AI Guidance:**\n{answer}{references}"

def get_self_qa(question):
    prompt = (
        "Given this user question about Indian farming, generate 2-3 related follow-up questions a farmer might ask, "
        "and answer each in detail, focusing on Indian context and practical steps. "
        "Format:\nQ1: ...\nA1: ...\nQ2: ...\nA2: ...\n"
        f"User question: {question}"
    )
    messages = [
        SystemMessage(content="You are a helpful Indian farming assistant."),
        HumanMessage(content=prompt)
    ]
    response = llm.invoke(messages)
    return response.content.strip()

# --- Session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Input row with icons ---
st.markdown('<div class="input-row">', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["jpg", "png", "pdf"], label_visibility="collapsed", key="file-upload")

col1, col2, col3, col4 = st.columns([8,1,1,1])

with col1:
    user_text = st.text_input(
        "Ask about farming, soil, pests, irrigation, or anything in Indian agriculture…",
        key="chat-input",
        label_visibility="collapsed"
    )

with col2:
    mic_clicked = st.button("🎤", help="Dictate", key="mic-btn")

with col3:
    tavily_clicked = st.button("🔍", help="Web Search", key="tavily-btn")

with col4:
    st.markdown('<span title="Attach file">📎</span>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Handle Input Actions ---
if mic_clicked:
    # In production: integrate with your voice agent!
    st.session_state['messages'].append({"role": "user", "content": "[Voice dictation not implemented in browser demo]"})

if tavily_clicked and user_text:
    response = get_rag_answer(user_text, use_tavily=True)
    st.session_state['messages'].append({"role": "user", "content": user_text})
    st.session_state['messages'].append({"role": "assistant", "content": response})

if user_text and not tavily_clicked and not mic_clicked:
    st.session_state['messages'].append({"role": "user", "content": user_text})
    # Meta/self QA/farming logic
    if is_meta_query(user_text):
        response = handle_meta_query()
    elif is_selfqa_query(user_text):
        prev_user_msg = next((m["content"] for m in reversed(st.session_state['messages'][:-1]) if m["role"] == "user"), None)
        if prev_user_msg:
            response = get_self_qa(prev_user_msg)
        else:
            response = "Please ask a farming question first, then I can suggest more questions."
    elif not is_farming_question(user_text):
        response = (
            "🙏 Sorry, I can only answer questions related to farming, agriculture, or agri-studies. "
            "If you are a farmer, student, or agriculturalist, please ask about crops, soil, weather, pest management, agri-careers, etc."
        )
    else:
        response = get_rag_answer(user_text)
    st.session_state['messages'].append({"role": "assistant", "content": response})

if uploaded_file:
    # In production: call your image/PDF agent here!
    img_result = f"File '{uploaded_file.name}' received. (Image/PDF analysis coming soon!)"
    st.session_state['messages'].append({"role": "assistant", "content": img_result})

# --- Display Chat Messages ---
for message in st.session_state.get('messages', []):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#8d6e63; margin-top:2rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi • May 2025"
    "</div>",
    unsafe_allow_html=True
)
