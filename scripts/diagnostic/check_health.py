#!/usr/bin/env python
import subprocess
import sys

def check_ollama():
    try:
        result = subprocess.run(["curl", "-s", "http://localhost:11434/api/tags"], capture_output=True)
        if result.returncode == 0:
            print("✅ Ollama está corriendo")
            return True
        else:
            print("❌ Ollama no responde")
            return False
    except:
        print("❌ Error conectando a Ollama")
        return False

def check_chromadb():
    try:
        import chromadb
        client = chromadb.Client()
        client.heartbeat()
        print("✅ ChromaDB está disponible")
        return True
    except Exception as e:
        print(f"❌ ChromaDB error: {e}")
        return False

def check_disk_space():
    import shutil
    usage = shutil.disk_usage(".")
    free_gb = usage.free / (1024**3)
    if free_gb > 5:
        print(f"✅ Espacio en disco: {free_gb:.1f} GB libres")
    else:
        print(f"⚠️  Espacio en disco bajo: {free_gb:.1f} GB libres")
    return free_gb > 1

if __name__ == "__main__":
    print("=== Health Check de FerdoNAN ===\n")
    ollama_ok = check_ollama()
    chroma_ok = check_chromadb()
    disk_ok = check_disk_space()
    print("\nResumen:", "✅ Todo bien" if (ollama_ok and chroma_ok and disk_ok) else "⚠️  Algunos servicios fallan")
