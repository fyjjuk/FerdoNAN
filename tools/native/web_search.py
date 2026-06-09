import requests
from bs4 import BeautifulSoup
import json
import time
from typing import List, Dict, Any

def search_duckduckgo(query: str, max_retries: int = 3, timeout: int = 15) -> List[Dict[str, str]]:
    """Busca en DuckDuckGo con reintentos y parsing robusto."""
    url = "https://html.duckduckgo.com/html/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    params = {"q": query}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Múltiples selectores para robustez (DDG puede cambiar clases)
            results = []
            selectors = ['.result', '.web-result', '.links_main', '.result__body']
            result_elements = []
            for selector in selectors:
                result_elements = soup.select(selector)
                if result_elements:
                    break
            
            for elem in result_elements[:5]:
                title_elem = elem.select_one('.result__a, .result__title, a[data-testid="result-title"]')
                snippet_elem = elem.select_one('.result__snippet, .result__abstract, .snippet')
                link_elem = elem.select_one('.result__a, .result__url, a[data-testid="result-url"]')
                
                title = title_elem.get_text(strip=True) if title_elem else "Sin título"
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else "Sin descripción"
                url_link = link_elem.get('href') if link_elem else ""
                if url_link and not url_link.startswith('http'):
                    url_link = "https://duckduckgo.com" + url_link
                
                results.append({"title": title, "snippet": snippet, "url": url_link})
            
            if results:
                return results
            else:
                # Si no se encontraron resultados, esperar y reintentar
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    return [{"title": "No se encontraron resultados", "snippet": "Intenta con otra consulta", "url": ""}]
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # backoff exponencial
                continue
            else:
                return [{"title": "Error en la búsqueda", "snippet": f"Se produjo un error: {str(e)}", "url": ""}]
    return []

def run(input_data: dict) -> dict:
    query = input_data.get("query", "")
    if not query:
        return {"error": "No se proporcionó consulta", "results": []}
    
    results = search_duckduckgo(query)
    return {"results": results, "count": len(results)}
