import subprocess
import shutil
import sys
import urllib.parse
import time

def find_spotify_cmd():
    """Detecta el comando para abrir Spotify (binario o flatpak)."""
    if shutil.which("spotify"):
        return "spotify"
    elif shutil.which("flatpak"):
        # Verificar si flatpak de Spotify está instalado
        result = subprocess.run(["flatpak", "list", "--columns=application"], capture_output=True, text=True)
        if "com.spotify.Client" in result.stdout:
            return "flatpak run com.spotify.Client"
    return None

def open_spotify_search(query: str, max_retries: int = 2) -> str:
    """Abre Spotify con la búsqueda de la playlist, con reintentos."""
    spotify_cmd = find_spotify_cmd()
    if not spotify_cmd:
        return "❌ Spotify no está instalado o no se encuentra."
    
    encoded_name = urllib.parse.quote(query)
    uri = f"spotify:search:{encoded_name}%20playlist"
    
    for attempt in range(max_retries):
        try:
            # Usar Popen para no bloquear (abre en segundo plano)
            if "flatpak" in spotify_cmd:
                subprocess.Popen(["flatpak", "run", "com.spotify.Client", uri])
            else:
                subprocess.Popen(["spotify", "--uri=" + uri])
            return f"🔍 Buscando playlist '{query}' en Spotify. Selecciona la playlist y dale play."
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            return f"❌ Error al abrir Spotify: {str(e)}"
    return "❌ No se pudo abrir Spotify después de varios intentos."

def run(input_data: dict) -> dict:
    playlist_name = input_data.get("playlist", "")
    if not playlist_name:
        return {"error": "No se especificó playlist"}
    
    message = open_spotify_search(playlist_name)
    if message.startswith("❌"):
        return {"error": message}
    return {"success": True, "message": message}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python spotify_playlist.py 'nombre de la playlist'")
        sys.exit(1)
    result = run({"playlist": sys.argv[1]})
    print(result.get("message", result.get("error", "")))
