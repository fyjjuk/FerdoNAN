import requests
from bs4 import BeautifulSoup
import sys
import json

def fetch_and_summarize(url: str, max_length: int = 500) -> str:
    """Obtiene y resume el contenido de una URL."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Eliminar elementos no deseados
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Extraer texto
        text = soup.get_text(separator=' ', strip=True)
        
        # Limpiar y acortar
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Resumir (primeros max_length caracteres)
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return f"✅ Contenido de {url}:\n\n{text}"
    except requests.RequestException as e:
        return f"❌ Error al acceder a {url}: {str(e)}"
    except Exception as e:
        return f"❌ Error procesando {url}: {str(e)}"

def run(input_data: dict) -> dict:
    url = input_data.get("url", input_data.get("query", ""))
    if not url:
        return {"error": "No se proporcionó URL"}
    
    result = fetch_and_summarize(url)
    return {"result": result, "url": url}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python web_fetch.py 'https://ejemplo.com'")
        sys.exit(1)
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"url": sys.argv[1]}
    result = run(args)
    print(result.get("result", result.get("error", "")))
