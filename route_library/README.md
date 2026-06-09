# Biblioteca de rutas para FerdoNAN

Esta carpeta contiene ejemplos de rutas funcionales que puedes copiar a tus agentes.

## Cómo usar una ruta

1. Copia el archivo `.yaml` a `agents/tu_agente/routes/`.
2. Opcionalmente, renómbralo y ajusta el `route_id` (debe ser único dentro del agente).
3. Modifica la descripción, system_prompt y otros campos según necesites.
4. Reinicia FerdoNAN (no requiere recarga en caliente).

## Índice de rutas

| Archivo | Tipo | Descripción |
|---------|------|-------------|
| `web_search.yaml` | cognitive | Buscar en internet (usa DuckDuckGo) |
| `web_fetch.yaml` | cognitive | Resumir una URL |
| `spotify_control.yaml` | cognitive | Control básico de Spotify (play/pause/next/previous) |
| `spotify_open.yaml` | cognitive | Abrir Spotify |
| `spotify_playlist_fantasy.yaml` | script | Abrir playlist de música fantástica |
| `linux_commands.yaml` | cognitive | Ayuda con comandos de Linux |
| `example_stage_creative.yaml` | cognitive | Ejemplo de stages (extraer keywords + responder) |

## Personalización

- Puedes combinar varias rutas en un mismo agente.
- Añade `gatekeeper_required: true` si quieres aprobación humana.
- Ajusta `stream: true` para respuestas en tiempo real.

¡Explora y crea tus propios agentes!
