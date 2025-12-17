# 📁 Organización del Proyecto StressGuard

## 🗂️ Estructura de Carpetas

```
HACKATON-StressGuard/
│
├── 📄 README.md                          # Documentación principal del proyecto
├── 📄 requirements.txt                   # Dependencias del proyecto
├── 🚀 INICIAR_STRESSGUARD.bat           # Lanzador principal
├── ⚙️ INSTALAR_DEPENDENCIAS.bat         # Instalador de dependencias
├── 🧪 evaluar_modelo.py                 # Script de evaluación del modelo ML
├── ✅ verificar_sistema.py               # Verificador de sistema
├── 🎯 launcher.py                        # Launcher de la aplicación
│
├── 📁 Chatbot/                           # Sistema de chatbot inteligente
│   ├── inter_chatbot.py                 # Interfaz principal del chatbot
│   ├── prompts.py                       # Prompts para el LLM
│   ├── test_chatbot.py                  # Tests del chatbot
│   └── readme.md                        # Documentación del chatbot
│
├── 📁 MachineLearning/                   # Modelos de Machine Learning
│   ├── stress_model.py                  # Modelo principal de estrés
│   ├── predict_stress.py                # Predicciones de estrés
│   ├── receptor_datos.py                # Receptor de datos del reloj
│   ├── chatbot_manager.py               # Manager del chatbot
│   ├── simu_reloj.py                    # Simulador de reloj
│   ├── reentrenar_modelo_mejorado.py    # Script de reentrenamiento optimizado
│   ├── wesad-completo-cloud.ipynb       # Notebook de entrenamiento
│   ├── readme.md                        # Documentación ML
│   └── requirements.txt                 # Dependencias específicas
│
├── 📁 DeepLearning/                      # Modelos de Deep Learning (visión)
│   ├── stress_detector_model.py         # Modelo detector de estrés
│   ├── train_stress_model.py            # Entrenamiento del modelo
│   ├── predict_stress.py                # Predicciones con DL
│   ├── readme.md                        # Documentación DL
│   ├── requirements.txt                 # Dependencias específicas
│   └── data2/                           # Dataset de entrenamiento
│
├── 📁 docs/                              # 📚 DOCUMENTACIÓN
│   ├── README_LAUNCHER.md               # Guía del launcher
│   ├── INSTALAR_VOCES_ESPAÑOL.md        # Instalación de voces TTS
│   ├── README_CHATBOT_INTELIGENTE.md    # Documentación del chatbot
│   ├── INSTRUCCIONES_SMOTE.md           # Instrucciones de SMOTE
│   └── README_ORGANIZACION.md           # Este archivo
│
└── 📁 utils/                             # 🔧 UTILIDADES
    ├── verificar_voces.py               # Verificador de voces TTS
    ├── solucionar_voz.py                # Solucionador de problemas de voz
    ├── hablar_gtts.py                   # Alternativa Google TTS
    ├── codigo_con_smote_simplificado.py # Ejemplo de SMOTE
    └── reentrenar_modelo_con_smote.py   # Reentrenamiento antiguo
```

## 🎯 Archivos Principales por Función

### 🚀 Iniciar el Sistema
- `INICIAR_STRESSGUARD.bat` - Lanzador principal (Windows)
- `launcher.py` - Launcher interactivo

### 🧪 Evaluación y Diagnóstico
- `evaluar_modelo.py` - Evaluar modelo ML
- `verificar_sistema.py` - Verificar instalación

### 🤖 Chatbot
- `Chatbot/inter_chatbot.py` - Sistema de chatbot con voz
- `Chatbot/prompts.py` - Configuración de prompts

### 📊 Machine Learning
- `MachineLearning/stress_model.py` - Modelo de predicción
- `MachineLearning/reentrenar_modelo_mejorado.py` - Reentrenamiento optimizado
- `MachineLearning/wesad-completo-cloud.ipynb` - Notebook de entrenamiento completo

### 👁️ Deep Learning
- `DeepLearning/stress_detector_model.py` - Detector visual de estrés
- `DeepLearning/train_stress_model.py` - Entrenamiento del modelo

## 📚 Documentación

Toda la documentación se encuentra en la carpeta `docs/`:

- **Launcher**: [docs/README_LAUNCHER.md](README_LAUNCHER.md)
- **Voces TTS**: [docs/INSTALAR_VOCES_ESPAÑOL.md](INSTALAR_VOCES_ESPAÑOL.md)
- **Chatbot**: [docs/README_CHATBOT_INTELIGENTE.md](README_CHATBOT_INTELIGENTE.md)
- **SMOTE**: [docs/INSTRUCCIONES_SMOTE.md](INSTRUCCIONES_SMOTE.md)

## 🔧 Utilidades

Scripts auxiliares en la carpeta `utils/`:

- **Verificar voces**: `utils/verificar_voces.py`
- **Solucionar voz**: `utils/solucionar_voz.py`
- **Google TTS**: `utils/hablar_gtts.py`
- **Ejemplos SMOTE**: `utils/codigo_con_smote_simplificado.py`

## 🗑️ Archivos Eliminados (Temporales)

Los siguientes archivos fueron eliminados por ser temporales:

- ❌ DIAGNOSTICO_VOZ.md
- ❌ INSTALACION_COMPLETADA.md
- ❌ REPORTE_EVALUACION.md
- ❌ analizar_chatbot_profundo.py
- ❌ comparar_chatbot.py
- ❌ diagnostico_profundo.py

## 📦 Instalación

1. Ejecutar `INSTALAR_DEPENDENCIAS.bat`
2. Verificar con `python verificar_sistema.py`
3. Iniciar con `INICIAR_STRESSGUARD.bat`

## 🎯 Flujo de Trabajo Típico

1. **Desarrollo ML**: Trabajar en `MachineLearning/wesad-completo-cloud.ipynb`
2. **Reentrenar**: Ejecutar `python MachineLearning/reentrenar_modelo_mejorado.py`
3. **Evaluar**: Ejecutar `python evaluar_modelo.py`
4. **Usar**: Ejecutar `INICIAR_STRESSGUARD.bat`

---

**Última actualización**: Diciembre 2025
**Versión**: 2.0 (Organización mejorada)
