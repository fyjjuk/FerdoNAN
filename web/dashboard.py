"""Dashboard web para FerdoNAN con FastAPI y WebSockets."""
import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
import yaml
import psutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logger import logger

app = FastAPI(title="FerdoNAN Dashboard", version="2.2.0")

active_websockets: List[WebSocket] = []
agents_cache: Dict[str, Dict[str, Any]] = {}

def load_agents() -> Dict[str, Dict[str, Any]]:
    agents_dir = Path("agents")
    agents = {}
    
    if not agents_dir.exists():
        return agents
    
    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir():
            config_path = agent_dir / "config.yaml"
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                    
                    routes_dir = agent_dir / "routes"
                    route_count = len(list(routes_dir.glob("*.yaml"))) if routes_dir.exists() else 0
                    
                    agents[data.get("id", agent_dir.name)] = {
                        "id": data.get("id", agent_dir.name),
                        "name": data.get("name", agent_dir.name),
                        "description": data.get("description", "")[:100],
                        "model": data.get("llm_provider", {}).get("model", "unknown"),
                        "provider": data.get("llm_provider", {}).get("name", "unknown"),
                        "routes": route_count,
                        "memory_window": data.get("short_term_memory_window", 5),
                        "execution_mode": data.get("execution_mode", "exclusive")
                    }
                except Exception as e:
                    logger.error(f"Error cargando agente {agent_dir.name}: {e}")
    
    return agents

def update_agents_cache():
    global agents_cache
    agents_cache = load_agents()

# @app.on_event("startup") (deprecated)
# Startup message printed below
    print("🚀 Dashboard iniciado en http://localhost:8000")
    print("   - Metrics: http://localhost:8000/metrics")
    print("   - Health:  http://localhost:8000/api/health")
    print("   - Agents:  http://localhost:8000/api/agents")
async def startup_event():
    update_agents_cache()
    logger.info("Dashboard web iniciado en http://localhost:8000")

# HTML simplificado inline
HTML_PAGE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FerdoNAN Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }
        h1 { text-align: center; margin-bottom: 20px; color: #00d4ff; }
        .status-bar { display: flex; gap: 20px; justify-content: center; margin-bottom: 30px; flex-wrap: wrap; }
        .status-card { background: rgba(255,255,255,0.1); padding: 15px 25px; border-radius: 10px; text-align: center; }
        .status-card .value { font-size: 1.5em; font-weight: bold; }
        .online .value { color: #4ecdc4; }
        .offline .value { color: #ff6b6b; }
        .agents-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .agent-card { background: rgba(255,255,255,0.08); border-radius: 15px; padding: 20px; cursor: pointer; transition: transform 0.2s; }
        .agent-card:hover { transform: translateY(-5px); background: rgba(255,255,255,0.12); }
        .agent-name { font-size: 1.3em; font-weight: bold; color: #00d4ff; margin-bottom: 10px; }
        .agent-id { font-size: 0.8em; color: #888; margin-bottom: 10px; }
        .agent-desc { font-size: 0.9em; color: #ccc; margin-bottom: 15px; }
        .agent-stats { display: flex; gap: 10px; flex-wrap: wrap; font-size: 0.8em; }
        .agent-stats span { background: rgba(0,212,255,0.2); padding: 4px 10px; border-radius: 20px; }
        .logs-section { background: rgba(0,0,0,0.5); border-radius: 15px; padding: 20px; }
        .logs-container { background: #0a0a0a; border-radius: 10px; padding: 15px; height: 300px; overflow-y: auto; font-family: monospace; font-size: 0.8em; }
        .log-entry { padding: 5px 0; border-bottom: 1px solid #222; }
        .log-info { color: #4ecdc4; }
        .log-warning { color: #ffd93d; }
        .log-error { color: #ff6b6b; }
        .timestamp { color: #666; margin-right: 10px; }
        .refresh-btn { background: #00d4ff; border: none; padding: 5px 15px; border-radius: 5px; cursor: pointer; color: #1a1a2e; font-weight: bold; margin-left: 10px; }
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); justify-content: center; align-items: center; z-index: 1000; }
        .modal-content { background: #1a1a2e; border-radius: 15px; padding: 30px; max-width: 500px; width: 90%; border: 1px solid #00d4ff; }
        .close { float: right; cursor: pointer; font-size: 1.5em; color: #ff6b6b; }
    </style>
</head>
<body>
    <h1>🤖 FerdoNAN Dashboard v2.2.0</h1>
    
    <div class="status-bar" id="statusBar">
        <div class="status-card" id="ollamaStatus">
            <div class="label">Ollama</div>
            <div class="value">🔄</div>
        </div>
        <div class="status-card">
            <div class="label">Agentes</div>
            <div class="value" id="agentCount">0</div>
        </div>
        <div class="status-card">
            <div class="label">CPU</div>
            <div class="value" id="cpuValue">--%</div>
        </div>
        <div class="status-card">
            <div class="label">Memoria</div>
            <div class="value" id="memValue">--%</div>
        </div>
    </div>
    
    <div class="agents-grid" id="agentsGrid">Cargando agentes...</div>
    
    <div class="logs-section">
        <div class="logs-header">
            <h3>📋 Logs en tiempo real</h3>
            <button class="refresh-btn" onclick="clearLogs()">Limpiar</button>
        </div>
        <div class="logs-container" id="logsContainer">
            <div class="log-entry log-info">📡 Conectando al servidor de logs...</div>
        </div>
    </div>
    
    <div id="modal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle"></h2>
            <div id="modalBody"></div>
        </div>
    </div>
    
    <script>
        let ws = null;
        
        async function loadAgents() {
            try {
                const resp = await fetch('/api/agents');
                const agents = await resp.json();
                document.getElementById('agentCount').innerHTML = agents.length;
                
                const grid = document.getElementById('agentsGrid');
                if (agents.length === 0) {
                    grid.innerHTML = '<p>No hay agentes configurados</p>';
                    return;
                }
                
                grid.innerHTML = agents.map(a => `
                    <div class="agent-card" onclick="showDetails('${a.id}')">
                        <div class="agent-name">${escapeHtml(a.name)}</div>
                        <div class="agent-id">${a.id}</div>
                        <div class="agent-desc">${escapeHtml(a.description)}</div>
                        <div class="agent-stats">
                            <span>🤖 ${a.model}</span>
                            <span>🔌 ${a.provider}</span>
                            <span>📁 ${a.routes} rutas</span>
                        </div>
                    </div>
                `).join('');
            } catch(e) {
                console.error(e);
            }
        }
        
        function escapeHtml(text) { return text ? text.replace(/[&<>]/g, function(m){return m==='&'?'&amp;':m==='<'?'&lt;':m==='>'?'&gt;':'';}) : ''; }
        
        async function showDetails(id) {
            try {
                const resp = await fetch(`/api/agents/${id}`);
                const a = await resp.json();
                document.getElementById('modalTitle').innerHTML = a.name;
                document.getElementById('modalBody').innerHTML = `
                    <p><strong>ID:</strong> ${a.id}</p>
                    <p><strong>Descripción:</strong> ${a.description}</p>
                    <p><strong>Modelo:</strong> ${a.model}</p>
                    <p><strong>Proveedor:</strong> ${a.provider}</p>
                    <p><strong>Rutas:</strong> ${a.routes}</p>
                    <p><strong>Memoria:</strong> ${a.memory_window} mensajes</p>
                `;
                document.getElementById('modal').style.display = 'flex';
            } catch(e) { console.error(e); }
        }
        
        function closeModal() { document.getElementById('modal').style.display = 'none'; }
        
        function connectWebSocket() {
            const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${location.host}/ws/logs`);
            ws.onopen = () => addLog('info', 'Conectado al servidor de logs');
            ws.onmessage = (e) => { const data = JSON.parse(e.data); addLog(data.level || 'info', data.message); };
            ws.onclose = () => { addLog('warning', 'Desconectado. Reconectando...'); setTimeout(connectWebSocket, 3000); };
        }
        
        function addLog(level, msg) {
            const container = document.getElementById('logsContainer');
            const entry = document.createElement('div');
            entry.className = `log-entry log-${level}`;
            entry.innerHTML = `<span class="timestamp">[${new Date().toLocaleTimeString()}]</span> ${msg}`;
            container.appendChild(entry);
            entry.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            while (container.children.length > 500) container.removeChild(container.firstChild);
        }
        
        function clearLogs() {
            document.getElementById('logsContainer').innerHTML = '<div class="log-entry log-info">📋 Logs limpiados</div>';
        }
        
        async function updateStatus() {
            try {
                const resp = await fetch('/api/health');
                const data = await resp.json();
                const card = document.getElementById('ollamaStatus');
                if (data.ollama) { card.className = 'status-card online'; card.querySelector('.value').innerHTML = '✅ Online'; }
                else { card.className = 'status-card offline'; card.querySelector('.value').innerHTML = '❌ Offline'; }
            } catch(e) {}
            
            try {
                const resp = await fetch('/api/metrics');
                const data = await resp.json();
                document.getElementById('cpuValue').innerHTML = `${data.cpu_percent}%`;
                document.getElementById('memValue').innerHTML = `${data.memory_percent}%`;
            } catch(e) {}
        }
        
        loadAgents();
        connectWebSocket();
        updateStatus();
        setInterval(updateStatus, 5000);
        setInterval(loadAgents, 30000);
        window.onclick = (e) => { if (e.target === document.getElementById('modal')) closeModal(); };
    </script>
</body>
</html>
"""

from pathlib import Path

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(HTML_PAGE)

@app.get("/api/agents")
async def get_agents():
    update_agents_cache()
    return JSONResponse(content=list(agents_cache.values()))

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    update_agents_cache()
    if agent_id not in agents_cache:
        return JSONResponse(status_code=404, content={"error": "Agente no encontrado"})
    return JSONResponse(content=agents_cache[agent_id])

@app.get("/api/health")
async def health_check():
    import subprocess
    health = {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "2.2.0", "ollama": False, "agents": len(agents_cache)}
    try:
        result = subprocess.run(["curl", "-s", "http://localhost:11434/api/tags"], capture_output=True, timeout=3)
        health["ollama"] = result.returncode == 0
    except:
        health["ollama"] = False
    return JSONResponse(content=health)

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

from monitoring.metrics import get_metrics as get_prom_metrics



@app.get("/metrics")
async def metrics_endpoint():
    """Endpoint Prometheus para scraping."""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=get_prom_metrics().decode("utf-8"), media_type="text/plain")

@app.get("/api/metrics")
async def get_metrics():
    metrics = {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_available_mb": psutil.virtual_memory().available / (1024 * 1024),
        "agents_loaded": len(agents_cache)
    }
    return JSONResponse(content=metrics)

def run_server(host: str = "0.0.0.0", port: int = 8000):
    import uvicorn
    print(f"🌐 Dashboard iniciado en http://{host}:{port}")
    print(f"📊 Health check: http://{host}:{port}/api/health")
    print(f"🤖 Agentes: http://{host}:{port}/api/agents")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()
