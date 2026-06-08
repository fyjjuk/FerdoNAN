import subprocess

def run(input_data: dict) -> dict:
    playlist_name = input_data.get("playlist", "")
    if not playlist_name:
        return {"error": "No playlist specified"}
    try:
        # Buscar y reproducir playlist con spotify (asumiendo que spotify está instalado)
        subprocess.run(["spotify", "play", "playlist", playlist_name], capture_output=True)
        return {"success": True, "message": f"Reproduciendo playlist: {playlist_name}"}
    except Exception as e:
        return {"error": str(e)}
