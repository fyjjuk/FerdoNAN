import subprocess
import sys
import shutil

def search_and_play(query):
    """Abre Spotify con la búsqueda de la consulta."""
    # Buscar el comando spotify
    spotify_cmd = shutil.which("spotify") or shutil.which("flatpak")
    if not spotify_cmd:
        return "❌ Spotify no está instalado o no se encuentra en el PATH."
    
    # Construir URI de búsqueda
    uri = f"spotify:search:{query.replace(' ', '%20')}"
    
    try:
        if "flatpak" in spotify_cmd:
            subprocess.Popen(["flatpak", "run", "com.spotify.Client", uri])
        else:
            subprocess.Popen(["spotify", "--uri=" + uri])
        return f"🔍 Abriendo Spotify con la búsqueda: '{query}'"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python spotify_search.py 'nombre de la canción'")
        sys.exit(1)
    query = sys.argv[1]
    print(search_and_play(query))
