from utils.livekit_utils import record_and_transcribe, speak_response
from agents.chat_agent import get_rag_answer

def voice_agent():
    user_text = record_and_transcribe()
    if not user_text:
        return "Sorry, I couldn't hear you. Please try again."
    ai_text = get_rag_answer(user_text)
    speak_response(ai_text)
    return ai_text
