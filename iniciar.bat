@echo off
echo.
echo  ================================
echo   VTT Manager - Iniciando...
echo  ================================
echo.

echo [1/3] Levantando base de datos...
docker-compose up -d
if %errorlevel% neq 0 (
    echo.
    echo  ERROR: No se pudo iniciar Docker.
    echo  Asegurate de que Docker Desktop esta en ejecucion.
    pause
    exit /b 1
)

echo.
echo [2/3] Esperando a que la base de datos este lista...
timeout /t 4 /nobreak > nul

echo.
echo [3/3] Lanzando aplicacion...
if exist "%temp%\vtt_manager.lock" (
    echo  La aplicacion ya esta en ejecucion.
    pause
    exit /b 0
)
echo lock > "%temp%\vtt_manager.lock"
python main.py
del "%temp%\vtt_manager.lock" 2>nul

