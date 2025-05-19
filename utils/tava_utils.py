import os
from langchain_tavily import TavilySearch

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
tavily_search = TavilySearch(api_key=TAVILY_API_KEY, max_results=3)

def tava_search(query):
    try:
        result = tavily_search.invoke({"query": query})
        if result and "results" in result and result["results"]:
            out = ""
            for r in result["results"][:2]:
                out += f"- [{r['title']}]({r['url']}): {r['content']}\n"
            return out
    except Exception:
        return ""
    return ""
