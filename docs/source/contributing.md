# Contributing Guide

## Adding a New Agent

1. Create directory: `agents/your_agent/`
2. Add `config.yaml`:

~~~yaml
id: "your_agent"
name: "Your Agent"
description: "Description"
llm_provider:
  name: "ollama"
  model: "llama3.2:3b"
~~~

3. Add YAML routes in `routes/` directory

## Adding a New Tool

1. Create file: `tools/native/your_tool.py`
2. Implement:

~~~python
def run(input_data: dict) -> dict:
    # Your logic here
    return {"result": "value"}
~~~

3. Make executable: `chmod +x tools/native/your_tool.py`

## Adding a New Theme

1. Create file: `ui/themes/your_theme.yaml`
2. Define structure:

~~~yaml
name: "Your Theme"
colors:
  primary: "#COLOR"
badges:
  agent: "[🤖]"
console:
  use_emoji: true
  use_colors: true
~~~

3. Set via `FERDONAN_THEME=your_theme`

## Code Standards
- Type hints required
- Docstrings in Google format
- Maximum line length: 100
