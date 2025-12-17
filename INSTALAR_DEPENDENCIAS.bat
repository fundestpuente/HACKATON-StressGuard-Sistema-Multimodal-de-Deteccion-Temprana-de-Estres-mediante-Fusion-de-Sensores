@echo off
title Instalador de Dependencias - StressGuard
cls

echo ============================================================
echo     STRESSGUARD - INSTALADOR DE DEPENDENCIAS
echo ============================================================
echo.
echo Este script instalara todas las dependencias necesarias
echo para ejecutar el sistema StressGuard.
echo.
echo Presiona cualquier tecla para continuar...
pause >nul

echo.
echo [1/3] Actualizando pip...
echo ============================================================
python -m pip install --upgrade pip

echo.
echo [2/3] Instalando dependencias principales...
echo ============================================================
pip install -r requirements.txt

echo.
echo [3/3] Verificando instalacion...
echo ============================================================
python -c "import flet; import sklearn; import xgboost; import psutil; import pyttsx3; import speech_recognition; import requests; print('✓ Todas las dependencias instaladas correctamente')"

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo     INSTALACION COMPLETADA EXITOSAMENTE
    echo ============================================================
    echo.
    echo Ahora puedes ejecutar INICIAR_STRESSGUARD.bat
    echo.
) else (
    echo.
    echo ============================================================
    echo     ERROR EN LA INSTALACION
    echo ============================================================
    echo.
    echo Algunas dependencias no se instalaron correctamente.
    echo Revisa los mensajes de error anteriores.
    echo.
)

echo Presiona cualquier tecla para salir...
pause >nul
