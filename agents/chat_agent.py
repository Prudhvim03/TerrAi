import os
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import SystemMessage, HumanMessage

# Load environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Set up LLM and Tavily Search
llm = ChatGroq(model="llama3-70b-8192", api_key=GROQ_API_KEY)
tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

def get_rag_answer(question):
    """
    Uses Tavily to fetch top web results, then asks the LLM to answer the user's question
    using both its own knowledge and the Tavily results for accuracy and recency.
    """
    # 1. Retrieve relevant web results
    tavily_result = tavily_search.invoke({"query": question})
    web_snippets = ""
    if tavily_result and "results" in tavily_result:
        for idx, result in enumerate(tavily_result["results"], 1):
            web_snippets += f"\nSource {idx}: {result.get('title', '')}\n{result.get('content', '')}\nURL: {result.get('url', '')}\n"

    # 2. Build a system prompt that includes the web context
    system_prompt = (
        "You are an Indian agricultural expert specializing in farming. "
        "Use the following up-to-date information from the web (from Google and trusted sources) to answer the user's question accurately and practically. "
        "If the web results are relevant, ground your answer in them. If not, use your own knowledge. "
        "Always explain in clear, simple language. If possible, mention local varieties, climate, and sustainable practices. "
        "If you don't know, say so and suggest how to find out.\n\n"
        f"Web search results:\n{web_snippets if web_snippets else '[No relevant web results found]'}"
    )

    # 3. Ask the LLM to answer, grounded in the web context
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    response = llm.invoke(messages)
    answer = response.content.strip()

    # 4. Optionally, show the top sources as references
    references = ""
    if web_snippets:
        references = "\n\n**Top Sources:**\n"
        for idx, result in enumerate(tavily_result["results"], 1):
            references += f"- [{result.get('title', 'Source')}]({result.get('url', '')})\n"

    return f"**AI Guidance:**\n{answer}{references}"
