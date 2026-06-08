import requests
from bs4 import BeautifulSoup
import json

def run(input_data: dict) -> dict:
    query = input_data.get("query", "")
    if not query:
        return {"error": "No query provided"}
    
    # Usar DuckDuckGo HTML (sin API key)
    url = f"https://html.duckduckgo.com/html/?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for result in soup.select('.result'):
            title_elem = result.select_one('.result__a')
            snippet_elem = result.select_one('.result__snippet')
            if title_elem and snippet_elem:
                results.append({
                    "title": title_elem.get_text(strip=True),
                    "snippet": snippet_elem.get_text(strip=True),
                    "url": title_elem.get('href', '')
                })
            if len(results) >= 5:
                break
        return {"results": results, "count": len(results)}
    except Exception as e:
        return {"error": str(e)}
