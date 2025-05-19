import os
from livekit import Client, AudioTrack
from agents.chat_agent import get_rag_answer

def voice_agent():
    # Placeholder: Replace with real LiveKit stream in production
    user_text = input("Speak your question (simulate): ")
    if not user_text:
        return "Sorry, I couldn't hear you. Please try again."
    ai_text = get_rag_answer(user_text)
    print(f"[AI Speaking]: {ai_text}")
    return ai_text
