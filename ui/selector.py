import sys
from ui.script_menu import run as run_script_menu

def select_agent_interactive(agents):
    """
    Selector de agentes por número, con opción para acceder al menú de scripts.
    Retorna el manifiesto del agente seleccionado o None si se cancela.
    """
    agent_list = list(agents.items())
    
    while True:
        print("\n" + "="*60)
        print("🎮 SELECCIÓN DE AGENTE")
        print("="*60)
        for idx, (agent_id, manifest) in enumerate(agent_list, start=1):
            print(f"  {idx}. {manifest.name} (ID: {agent_id})")
        print("  S. Scripts y utilidades")
        print("  0. Salir")
        print("="*60)
        
        choice = input("\n👉 Elige un número, 'S' para utilidades, o 0 para salir: ").strip()
        
        if choice == "0":
            print("👋 Saliendo...")
            sys.exit(0)
        elif choice.lower() == "s":
            run_script_menu()
            # Después de ejecutar scripts, volvemos al selector
            continue
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(agent_list):
                    agent_id, manifest = agent_list[idx]
                    desc = getattr(manifest, 'description', 'Sin descripción')
                    print(f"\n✅ Agente seleccionado: {manifest.name}")
                    print(f"📄 {desc}\n")
                    return manifest
                else:
                    print("❌ Número inválido.")
            except ValueError:
                print("❌ Entrada inválida. Ingresa un número, 'S' o 0.")
