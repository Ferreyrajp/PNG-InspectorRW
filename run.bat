@echo off
echo Iniciando PNG Inspector...

:: Verificar si Python está instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python no está instalado o no está en el PATH.
    echo Por favor, instala Python desde https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Verificar si pip está instalado
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: pip no está instalado.
    echo Por favor, instala pip siguiendo las instrucciones en https://pip.pypa.io/en/stable/installation/
    pause
    exit /b 1
)

:: Instalar dependencias si no están instaladas
pip install -r requirements.txt >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error al instalar las dependencias. Intentando continuar...
)

:: Iniciar el servidor
echo Iniciando el servidor en http://localhost:8081
echo Presiona Ctrl+C para detener el servidor

python png_inspector_simple.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error al iniciar el servidor.
    pause
    exit /b 1
)

pause
