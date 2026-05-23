@echo off
chcp 65001 >nul
title CHAT-O Builder
REM ============================================
REM Build CHAT-O como .exe para Windows
REM ============================================

echo.
echo === CHAT-O Builder ===
echo.

REM Verificar Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: No se encuentra Python. Instalalo desde python.org
    pause
    exit /b 1
)

REM Activar o crear entorno virtual
if not exist .venv\Scripts\activate (
    echo Creando entorno virtual...
    python -m venv .venv
)
call .venv\Scripts\activate

echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Construyendo ejecutable (esto tarda unos minutos)...
pyinstaller --onefile --noconsole --name "CHAT-O" ^
    --collect-all gradio --collect-all groq ^
    app.py

echo.
echo ========================================
echo LISTO! Busca CHAT-O.exe en la carpeta "dist"
echo.
echo ANTES DE EJECUTAR:
echo   1. Copia CHAT-O.exe a una carpeta nueva
echo   2. Crea un archivo .env en esa misma carpeta con:
echo      GROQ_API_KEY=gsk_tu_api_key_aqui
echo   3. Ejecuta CHAT-O.exe
echo.
echo Para conservar recuerdos, copia tambien memoria.db
echo ========================================
pause
