"""
Selector interactivo de agentes con soporte para comandos slash.
"""

import sys
from ui.cli_commands import process_slash_command


def select_agent_interactive(agents):
    """Selector de agente interactivo con flechas y comandos slash."""
    agent_list = list(agents.values())
    
    while True:
        print("\n" + "=" * 60)
        print("🎮 SELECCIÓN DE AGENTE")
        print("=" * 60)
        for i, agent in enumerate(agent_list, 1):
            print(f"  {i}. {agent.name} (ID: {agent.id})")
        print("  S. Scripts y utilidades")
        print("  0. Salir")
        print("  /help - Ver comandos disponibles")
        print("=" * 60)
        
        try:
            choice = input("\n👉 Elige un número, 'S' para utilidades, o escribe /comando: ").strip()
            
            if not choice:
                continue
            
            # Procesar comandos slash
            if choice.startswith('/'):
                msg, _, should_exit = process_slash_command(choice, agents, None)
                print(msg)
                if should_exit:
                    sys.exit(0)
                continue
            
            if choice.upper() == 'S':
                # Mostrar menú de utilidades (scripts)
                from ui.plugin_menu import display_plugin_menu
                display_plugin_menu()
                continue
            
            if choice == '0':
                print("👋 Saliendo...")
                sys.exit(0)
            
            idx = int(choice) - 1
            if 0 <= idx < len(agent_list):
                return agent_list[idx]
            else:
                print(f"❌ Opción inválida. Elige entre 1 y {len(agent_list)}")
        except ValueError:
            print("❌ Por favor, ingresa un número válido, 'S', o un comando /")
        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            sys.exit(0)


def select_agent(agents):
    """Selector numérico simple (fallback si no hay prompt_toolkit)."""
    agent_list = list(agents.values())
    print("\n" + "=" * 60)
    print("🎮 SELECCIÓN DE AGENTE")
    print("=" * 60)
    for i, agent in enumerate(agent_list, 1):
        print(f"  {i}. {agent.name} (ID: {agent.id})")
    print("  0. Salir")
    print("=" * 60)
    
    while True:
        try:
            choice = input("\n👉 Elige un número: ").strip()
            if choice == "0":
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(agent_list):
                return agent_list[idx]
            print(f"❌ Opción inválida. Elige entre 1 y {len(agent_list)}")
        except ValueError:
            print("❌ Por favor, ingresa un número válido")
        except KeyboardInterrupt:
            print("\n👋 Saliendo...")
            return None
