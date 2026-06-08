import subprocess
import json

def run(input_data: dict) -> dict:
    action = input_data.get("action")
    query = input_data.get("query", "")
    
    try:
        if action == "play":
            subprocess.run(["playerctl", "--player=spotify", "play"], check=True, capture_output=True)
            return {"success": True, "message": "Reproduciendo"}
        elif action == "pause":
            subprocess.run(["playerctl", "--player=spotify", "pause"], check=True, capture_output=True)
            return {"success": True, "message": "Pausado"}
        elif action == "next":
            subprocess.run(["playerctl", "--player=spotify", "next"], check=True, capture_output=True)
            return {"success": True, "message": "Siguiente canción"}
        elif action == "previous":
            subprocess.run(["playerctl", "--player=spotify", "previous"], check=True, capture_output=True)
            return {"success": True, "message": "Canción anterior"}
        elif action == "search_and_play":
            # Buscar y reproducir (requiere spotify-cli)
            result = subprocess.run(["spotify", "play", query], capture_output=True, text=True)
            return {"success": result.returncode == 0, "message": result.stdout if result.returncode == 0 else result.stderr}
        elif action == "status":
            result = subprocess.run(["playerctl", "--player=spotify", "status"], capture_output=True, text=True)
            return {"status": result.stdout.strip(), "success": True}
        else:
            return {"error": f"Acción desconocida: {action}"}
    except Exception as e:
        return {"error": str(e)}
