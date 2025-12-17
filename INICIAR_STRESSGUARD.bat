@echo off
title StressGuard Launcher
cls

echo ============================================================
echo     STRESSGUARD - SISTEMA DE DETECCION DE ESTRES
echo ============================================================
echo.
echo Iniciando interfaz grafica...
echo.

python launcher.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo iniciar el launcher
    echo Verifica que Python este instalado y las dependencias esten correctas
    echo.
    pause
)
