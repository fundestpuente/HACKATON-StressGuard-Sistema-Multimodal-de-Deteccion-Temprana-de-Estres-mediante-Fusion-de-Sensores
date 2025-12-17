# 🏥 StressGuard - Sistema Multimodal de Detección Temprana de Estrés

Sistema inteligente de detección de estrés mediante sensores biométricos y chatbot asistente con IA.

## 🚀 Inicio Rápido

### ⚡ Método 1: Launcher Gráfico (RECOMENDADO)

**Windows:**
```bash
# Doble clic en:
INICIAR_STRESSGUARD.bat
```

**Python directo:**
```bash
python launcher.py
```

El launcher te permitirá:
- ✅ Abrir el chatbot manualmente
- ✅ Iniciar el sistema de detección completo
- ✅ Ver el estado de todos los módulos
- ✅ Detener procesos fácilmente

### 📖 Método 2: Ejecución Manual

**1. Receptor de datos:**
```bash
cd MachineLearning
python receptor_datos.py
```

**2. Simulador de reloj (en otra terminal):**
```bash
cd MachineLearning
python simu_reloj.py
```

**3. Chatbot (opcional - se abre automáticamente):**
```bash
cd Chatbot
python inter_chatbot.py
```

## 📁 Estructura del Proyecto

```
HACKATON-StressGuard/
│
├── launcher.py                    # 🚀 INTERFAZ PRINCIPAL (INICIAR AQUÍ)
├── INICIAR_STRESSGUARD.bat       # Script de inicio rápido
├── README_LAUNCHER.md             # Documentación del launcher
│
├── Chatbot/
│   ├── inter_chatbot.py          # Chatbot con Ollama (Llama 3.2)
│   └── prompts.py                # Prompts del sistema
│
├── MachineLearning/
│   ├── chatbot_manager.py        # Gestor de chatbot (instancia única)
│   ├── receptor_datos.py         # Receptor de señales de estrés
│   ├── simu_reloj.py            # Simulador de reloj Samsung
│   ├── stress_model.py          # Modelo de Machine Learning
│   ├── requirements.txt         # Dependencias
│   └── README_CHATBOT_INTELIGENTE.md
│
└── DeepLearning/
    ├── train_stress_model.py    # Entrenamiento del modelo
    └── predict_stress.py        # Predicción con modelo
```

## 🛠️ Instalación

### 1. Requisitos Previos

- Python 3.8 o superior
- Ollama con modelo Llama 3.2

### 2. Instalar Ollama

```bash
# Descargar e instalar Ollama desde: https://ollama.ai
# Luego descargar el modelo:
ollama pull llama3.2
```

### 3. Instalar Dependencias Python

```bash
pip install flet psutil scikit-learn numpy pandas pyttsx3 SpeechRecognition requests
```

O usar el archivo de requisitos:

```bash
cd MachineLearning
pip install -r requirements.txt
```

## 🎯 Características Principales

### 🤖 Sistema de Chatbot Inteligente

- **Modo Automático**: Se abre cuando se detecta estrés
  - Mensaje inicial: "He detectado una señal de estrés en tus sensores..."
  - Contexto de estrés conocido
  
- **Modo Manual**: Usuario abre el chatbot
  - Conversación libre
  - Sin contexto inicial de estrés

- **Control de Instancia Única**: Solo una ventana a la vez
- **Voz**: Texto a voz y reconocimiento de voz en español
- **Router Pattern**: Alterna entre prompt de charla y prompt de guía según el contexto

### 📊 Sistema de Detección

- **Simulador de Reloj Samsung (Empatica E4)**
  - Sensores: BVP, EDA, Temperatura
  - Predicción en tiempo real
  - Envío automático al detectar estrés

- **Receptor de Datos**
  - Socket listener (puerto 65432)
  - Recibe señales de estrés
  - Activa el chatbot automáticamente

- **Machine Learning**
  - Modelo entrenado con scikit-learn
  - Predicción binaria: Estrés / Sin estrés

### 🎨 Launcher Gráfico

- ✅ Interfaz intuitiva con Flet
- ✅ Control centralizado de todos los módulos
- ✅ Indicadores de estado en tiempo real
- ✅ Gestión automática de procesos

## 📖 Guías de Uso

### Escenario 1: Solo conversar con el chatbot

1. Ejecutar `launcher.py`
2. Clic en "Abrir Chatbot"
3. Conversar libremente

### Escenario 2: Detección completa de estrés

1. Ejecutar `launcher.py`
2. Clic en "Iniciar Sistema"
3. Ajustar sensores en el simulador
4. Cuando se detecte estrés → Chatbot se abre automáticamente
5. Conversar sobre el estado de estrés

### Escenario 3: Desarrollo/Debugging

1. Ejecutar `receptor_datos.py` manualmente
2. Ejecutar `simu_reloj.py` manualmente
3. Observar logs en consola

## 🧪 Pruebas

### Probar el Gestor de Chatbot

```bash
cd MachineLearning
python chatbot_manager.py
```

### Probar el Modelo de ML

```bash
cd MachineLearning
python stress_model.py
```

## 🔧 Configuración

### Cambiar el puerto del receptor

Editar en `receptor_datos.py` y `simu_reloj.py`:
```python
PORT = 65432  # Cambiar a otro puerto
```

### Cambiar el modelo de Ollama

Editar en `Chatbot/inter_chatbot.py`:
```python
MODELO_OLLAMA = "llama3.2:3b-instruct-q8_0"  # Cambiar modelo
```

Para ver qué modelos tienes instalados:
```bash
ollama list
```

### Ajustar prompts del chatbot

Editar `Chatbot/prompts.py`:
- `PROMPT_CHARLA`: Para conversación general
- `PROMPT_GUIA`: Para situaciones de estrés

## 📊 Flujo del Sistema

```
┌─────────────────┐
│  Launcher       │  Usuario selecciona opción
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────┐   ┌──────────┐
│Chat │   │ Receptor │ ← Escucha puerto 65432
│bot  │   └────┬─────┘
└─────┘        │
               ▲
               │
         ┌─────┴──────┐
         │ Simulador  │ → Detecta estrés
         │ de Reloj   │ → Envía datos
         └────────────┘
               │
               ▼
         [Estrés?] → SÍ → Abre Chatbot (modo auto)
```

## ⚠️ Solución de Problemas

### El launcher no inicia
```bash
pip install flet psutil
```

### Ollama no responde
```bash
# Verificar que Ollama esté ejecutándose
ollama list
ollama serve
```

### Puerto ocupado
- Cambiar el puerto en configuración
- O cerrar el proceso que usa el puerto 65432

### El chatbot no se abre automáticamente
```bash
pip install psutil
# Verificar que existe chatbot_manager.py
```

## 📚 Documentación Adicional

- [Launcher - Guía de Uso](README_LAUNCHER.md)
- [Chatbot Inteligente](MachineLearning/README_CHATBOT_INTELIGENTE.md)
- [Modelo de Deep Learning](DeepLearning/readme.md)

## 👥 Equipo de Desarrollo

Proyecto desarrollado para **Samsung Hackaton 2025**  
Sistema de detección temprana de estrés mediante fusión de sensores

## 📄 Licencia

Proyecto académico - EPN (Escuela Politécnica Nacional)

---

**⚡ Inicio rápido**: `python launcher.py` o doble clic en `INICIAR_STRESSGUARD.bat`
