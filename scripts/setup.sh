#!/bin/bash
echo "🔧 Configurando FerdoNAN..."

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorios necesarios
mkdir -p logs cache data/rag_storage

# Copiar .env ejemplo
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📝 Creado .env - edita con tus API keys"
fi

echo "✅ Listo! Ejecuta: python main.py"
