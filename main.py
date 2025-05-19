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

# --- Load environment variables ---
load_dotenv()

# --- Apply Custom CSS ---
with open("static/custom.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Logo (SVG) ---
futuristic_logo_svg = """
<svg width="72" height="72" viewBox="0 0 72 72" fill="none">
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
st.markdown(f'<div class="main-title">{MAIN_TITLE}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">{SUBTITLE}</div>', unsafe_allow_html=True)

# --- Helper Functions ---
def is_meta_query(q):
    return any(kw in q.lower() for kw in META_KEYWORDS)

def is_selfqa_query(q):
    return any(trigger in q.lower() for trigger in SELF_QA_TRIGGERS)

def is_farming_question(q):
    return any(word in q.lower() for word in FARMING_KEYWORDS)

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

# --- Chat Session State ---
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

# --- Voice Agent Button (optional, for CLI simulation) ---
if st.button("🎤 Voice Assistant"):
    with st.spinner("Listening..."):
        voice_response = voice_agent()
        st.markdown(f"**Voice Agent:** {voice_response}")
        st.session_state.messages.append({"role": "assistant", "content": voice_response})

# --- Image Analyzer (optional stub) ---
uploaded_img = st.file_uploader("Upload a crop image for analysis", type=["jpg", "png"])
if uploaded_img:
    img_result = analyze_image(uploaded_img)
    st.markdown(img_result)
    st.session_state.messages.append({"role": "assistant", "content": img_result})

# --- Footer ---
st.markdown(
    "<div style='text-align:center; color:#8d6e63; margin-top:2rem;'>"
    "Developed for Indian farmers • Powered by Prudhvi • May 2025"
    "</div>",
    unsafe_allow_html=True
)
