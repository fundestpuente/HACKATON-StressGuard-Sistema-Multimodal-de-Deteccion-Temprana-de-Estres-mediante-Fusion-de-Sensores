@echo off
title Entrenar Modelo Deep Learning - StressGuard

echo.
echo ========================================
echo   ENTRENAR MODELO DE DEEP LEARNING
echo ========================================
echo.
echo Este proceso entrenara el modelo para
echo detectar estres mediante imagenes.
echo.
echo REQUISITOS:
echo - Dataset en DeepLearning/data2/
echo - Python 3.12 instalado
echo - TensorFlow instalado
echo.
echo El entrenamiento puede tardar varios
echo minutos dependiendo de tu hardware.
echo.
pause

cd DeepLearning
py -3.12 train_stress_model.py

echo.
echo ========================================
echo   ENTRENAMIENTO COMPLETADO
echo ========================================
echo.
pause
