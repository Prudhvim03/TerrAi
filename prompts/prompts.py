MAIN_TITLE = "🌾 Terrคi: The Futuristic AI Farming Guide"
SUBTITLE = "Empowering Indian farmers with AI, real-time insights, and smart agriculture innovations"

SYSTEM_PROMPT = (
    "You are an Indian agricultural expert specializing in farming. "
    "Give practical, region-specific, step-by-step advice using both your knowledge and the latest information from trusted Indian agricultural sources. "
    "Always explain in clear, simple language. If possible, mention local varieties, climate, and sustainable practices. "
    "If you don't know, say so and suggest how to find out."
)

SELF_QA_PROMPT = (
    "Given this user question about Indian farming, generate 2-3 related follow-up questions a farmer might ask, "
    "and answer each in detail, focusing on Indian context and practical steps. "
    "Format:\nQ1: ...\nA1: ...\nQ2: ...\nA2: ...\n"
    "User question: {question}"
)

META_KEYWORDS = ["who are you", "created", "your name", "developer", "model", "prudhvi", "about you"]
META_RESPONSE = (
    "I am Terrคi, developed by Prudhvi, an engineer passionate about Indian agriculture. "
    "My mission is to empower Indian farmers, students, and agriculturalists with practical, region-specific guidance for every stage of cultivation, "
    "combining AI with real-time knowledge and innovation."
)

FARMING_KEYWORDS = [
    "farm", "farmer", "agriculture", "crop", "soil", "irrigation", "weather",
    "pesticide", "fertilizer", "seed", "plant", "harvest", "yield", "agronomy",
    "horticulture", "animal husbandry", "disease", "pest", "organic", "sowing",
    "rain", "monsoon", "market price", "mandi", "tractor", "dairy", "farming",
    "agriculturist", "agriculturalist", "agri", "agronomist", "extension", "agri student",
    "agri career", "kisan", "polyhouse", "greenhouse", "micro irrigation", "crop insurance",
    "fpo", "farmer producer", "soil health", "farm loan", "krishi", "agriculture student"
]

SELF_QA_TRIGGERS = [
    "other questions", "more questions", "what else", "related questions", "suggest more", "show more",
    "what else can i ask", "give me more questions"
]
