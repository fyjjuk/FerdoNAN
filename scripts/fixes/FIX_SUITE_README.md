# FERDONAN v2.0 - Fix Suite

Conjunto de scripts para corregir vulnerabilidades y completar funcionalidades en FerdoNAN.

## Estructura

```
/home/claude/
├── MASTER_FIX.sh              ← Ejecuta TODOS los fixes automáticamente
├── fix_interactive.sh          ← Selector interactivo (RECOMENDADO)
├── fix_stages_validation.sh    ← Fix #1: Validación de Stages
├── fix_gatekeeper_activation.sh← Fix #2: Gatekeeper Activation
├── fix_rag_injection.sh        ← Fix #3: RAG Injection Hardening
├── fix_resource_profiles.sh    ← Fix #4: Dynamic Resource Profiles
├── fix_streaming.sh            ← Fix #5: Real Streaming
├── fix_critical_routes.sh      ← Fix #6: Critical Routes Protection
└── FIX_SUITE_README.md         ← Este archivo
```

## Guía Rápida

### Opción 1: Modo Interactivo (RECOMENDADO)

```bash
bash /home/claude/fix_interactive.sh
```

**Ventajas:**
- Seleccionar fixes individuales
- Ver información detallada de cada fix
- Rollback fácil si algo falla
- Menú interactivo amigable

### Opción 2: Ejecutar TODO automáticamente

```bash
bash /home/claude/MASTER_FIX.sh
```

**Ventajas:**
- Rápido
- Aplica todas las correcciones en orden
- Verifica sintaxis Python automáticamente

### Opción 3: Ejecutar fix individual

```bash
bash /home/claude/fix_stages_validation.sh    # Fix #1
bash /home/claude/fix_rag_injection.sh        # Fix #3
# etc...
```

**Ventajas:**
- Control total
- Depuración específica

---

## Qué hace cada Fix

### Fix #1: Validación de Stages (CRÍTICA)

**Problema:** 
- Método `_validate_stage_output()` existe pero nunca se invoca
- Stages pueden producir salida vacía sin error

**Solución:**
- Inyecta llamada a `_validate_stage_output()` en `CognitiveExecutor.execute()`
- Lanza `ValueError` si stage produce salida inválida
- Logging detallado de errores

**Archivos modificados:**
- `services/executor/cognitive.py`

**Backup:** 
- `services/executor/cognitive.py.backup_stages`

---

### Fix #2: Gatekeeper Activation (CRÍTICA)

**Problema:**
- Gatekeeper existe pero `gatekeeper_required: false` en TODAS las rutas
- Nunca se invoca el checkpoint de aprobación humana

**Solución:**
- Auditoría de rutas críticas (detecta automáticamente)
- Identifica rutas que deberían estar protegidas
- Genera script para habilitar gatekeeper
- Logging del estado en `logs/approvals.log`

**Archivos modificados:**
- Ninguno (solo auditoría + generación de script)

**Instrucciones manuales:**
```bash
# Para cada ruta crítica:
sed -i 's/gatekeeper_required: false/gatekeeper_required: true/g' \
  agents/[agent]/routes/[ruta].yaml
```

---

### Fix #3: RAG Query Injection Hardening (CRÍTICA)

**Problema:**
- Sin sanitización de entrada antes de buscar en ChromaDB
- Posible injection de queries malformadas

**Solución:**
- Validación de tipo (str)
- Limitación de longitud (max 1000 chars)
- Check de query vacío
- Logging en cada etapa

**Archivos modificados:**
- `services/vector_store.py` (método `rag_query`)

**Backup:**
- `services/vector_store.py.backup_rag`

---

### Fix #4: Dynamic Resource Profiles (ALTA)

**Problema:**
- Lógica de selección de perfil incompleta
- No considera CPU usage
- Fallback pobre si no hay VRAM

**Solución:**
- Considera CPU% en decisión (evita overload)
- Mejor fallback usando solo RAM
- Logging detallado de decisión
- Umbrales claramente documentados

**Archivos modificados:**
- `orchestration/resource_manager.py` (método `select_resource_profile`)

**Backup:**
- `orchestration/resource_manager.py.backup_profiles`

**Umbrales (ajustables):**
```
HIGH:   VRAM > 4000MB & RAM > 8000MB
MEDIUM: VRAM > 2000MB & RAM > 4000MB
LOW:    Fallback (poca memoria)
```

---

### Fix #5: Real Streaming (MEDIA)

**Problema:**
- Método `_stream_response()` existe pero NO se integra en `execute()`
- Streaming no funciona en tiempo real

**Solución:**
- Integra streaming condicional en `CognitiveExecutor.execute()`
- Crea método `_stream_with_yield()` para generadores
- Fallback automático si LLM no soporta streaming

**Archivos modificados:**
- `services/executor/cognitive.py`
- `services/llm_providers/ollama.py` (si existe `stream_response`)

**Backup:**
- `services/executor/cognitive.py.backup_streaming`

**Nota:** Requiere ediciones manuales si estructura es diferente a esperada

---

### Fix #6: Critical Routes Protection (CRÍTICA)

**Problema:**
- Rutas que acceden a sistema (spotify, linux) sin protección
- Cualquiera puede ejecutar comandos

**Solución:**
- Auditoría automática de rutas críticas
- Detecta por keywords (comandos, control, reproducir, etc.)
- Detecta por herramientas permitidas
- Genera script para habilitar gatekeeper

**Archivos identificados:**
```
agents/spotify_player/routes/reproducir.yaml
agents/spotify_player/routes/control_directo.yaml
agents/spotify_player/routes/control_rapido.yaml
agents/experto_linux/routes/comandos_basicos.yaml
```

---

## Preguntas Frecuentes

### P: ¿Qué pasa si un fix falla?

**R:** Cada fix crea un backup automáticamente:
```bash
# Ver backups creados
find . -name "*.backup*" -type f

# Restaurar (ejemplo)
cp core/engine.py.backup_gatekeeper core/engine.py
```

### P: ¿Puedo ejecutar fixes parcialmente?

**R:** Sí, usa `fix_interactive.sh` para seleccionar qué ejecutar.

### P: ¿En qué orden debería ejecutar los fixes?

**R:** Orden recomendado:
```
1. Fix #1 (Validación de Stages)      ← Seguridad crítica
2. Fix #3 (RAG Injection)              ← Seguridad crítica
3. Fix #6 (Critical Routes)            ← Seguridad crítica
4. Fix #4 (Resource Profiles)          ← Funcionalidad
5. Fix #5 (Streaming)                  ← UX
```

O ejecuta `MASTER_FIX.sh` para todos en orden automático.

### P: ¿Cómo verifico que los fixes funcionan?

**R:** Después de ejecutar:
```bash
# 1. Verificar sintaxis
python3 -m py_compile core/engine.py
python3 -m py_compile services/executor/cognitive.py

# 2. Ejecutar tests
pytest tests/ -v

# 3. Probar en vivo
python main.py
```

### P: ¿Puedo editar los scripts?

**R:** Sí, son completamente personalizables. Ubicación:
```
/home/claude/fix_*.sh
```

---

## Guía de Depuración

### Si un fix falla durante ejecución

1. **Leer el error** (está en stdout/stderr)
2. **Revisar el backup** para ver qué se intentó cambiar
3. **Restaurar si es necesario:**
   ```bash
   cp archivo.backup_[tipo] archivo
   ```
4. **Editar manualmente** (instrucciones en cada fix script)

### Logs útiles

```bash
# Ver logs de ejecución en tiempo real
tail -f logs/ferdonan.log

# Ver aprobaciones de gatekeeper
cat logs/approvals.log

# Ver auditoría de seguridad
cat logs/audit.log
```

### Verificar cambios específicos

```bash
# Ver qué cambió en engine.py
diff core/engine.py.backup_gatekeeper core/engine.py

# Buscar palabra clave
grep -n "validate_stage_output" services/executor/cognitive.py
```

---

## Instalación & Uso desde Cero

```bash
# 1. Navegar a FerdoNAN
cd ~/ferdonan

# 2. Ejecutar fix suite interactivo
bash /home/claude/fix_interactive.sh

# O ejecutar todo automáticamente:
bash /home/claude/MASTER_FIX.sh

# 3. Ejecutar tests
pytest tests/ -v

# 4. Iniciar FerdoNAN
python main.py
```

---

## Contacto & Soporte

Si un fix no funciona:
1. Captura la salida completa del error
2. Revisa el archivo `.backup_*` para entender qué se intentó
3. Edita manualmente usando las instrucciones en el script

---

## Cambios Resumen

| Fix # | Severidad | Archivo | Cambio |
|-------|-----------|---------|--------|
| 1 | 🔴 CRÍTICA | `services/executor/cognitive.py` | Inyecta validación de stages |
| 2 | 🔴 CRÍTICA | N/A | Auditoría + instrucciones gatekeeper |
| 3 | 🔴 CRÍTICA | `services/vector_store.py` | Sanitización RAG queries |
| 4 | 🟠 ALTA | `orchestration/resource_manager.py` | Lógica perfiles mejorada |
| 5 | 🟡 MEDIA | `services/executor/cognitive.py` | Integración streaming |
| 6 | 🔴 CRÍTICA | Rutas YAML | Auditoría + gatekeeper activation |

---

**Versión:** 2.0 | **Fecha:** Junio 2026 | **Estado:** Production Ready

