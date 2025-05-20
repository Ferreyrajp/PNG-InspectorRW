#!/bin/bash
echo "Iniciando PNG Inspector..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado."
    echo "Por favor, instala Python 3 usando tu gestor de paquetes."
    echo "Ejemplo para Ubuntu/Debian: sudo apt install python3"
    exit 1
fi

# Verificar si pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "pip3 no está instalado. Instalando..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-pip
    else
        echo "No se pudo instalar pip automáticamente. Por favor instálalo manualmente."
        exit 1
    fi
fi

# Instalar dependencias
pip3 install -r requirements.txt

# Hacer el script ejecutable
chmod +x run.sh

# Iniciar el servidor
echo "Iniciando el servidor en http://localhost:8081"
echo "Presiona Ctrl+C para detener el servidor"

python3 png_inspector_simple.py

if [ $? -ne 0 ]; then
    echo -e "\nError al iniciar el servidor."
    exit 1
fi
