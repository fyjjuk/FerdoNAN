import sys

def select_agent_interactive(agents):
    """
    Selector de agentes por número, con vista previa de descripción.
    Retorna el manifiesto del agente seleccionado o None si se cancela.
    """
    agent_list = list(agents.items())
    print("\n" + "="*60)
    print("🎮 SELECCIÓN DE AGENTE")
    print("="*60)
    for idx, (agent_id, manifest) in enumerate(agent_list, start=1):
        print(f"  {idx}. {manifest.name} (ID: {agent_id})")
    print("  0. Salir")
    print("="*60)
    
    while True:
        try:
            choice = input("\n👉 Elige un número: ").strip()
            if choice == "0":
                print("👋 Saliendo...")
                sys.exit(0)
            idx = int(choice) - 1
            if 0 <= idx < len(agent_list):
                agent_id, manifest = agent_list[idx]
                # Mostrar descripción del agente seleccionado
                desc = getattr(manifest, 'description', 'Sin descripción')
                print(f"\n✅ Agente seleccionado: {manifest.name}")
                print(f"📄 {desc}\n")
                return manifest
            else:
                print("❌ Número inválido. Intenta de nuevo.")
        except ValueError:
            print("❌ Entrada inválida. Ingresa un número.")
