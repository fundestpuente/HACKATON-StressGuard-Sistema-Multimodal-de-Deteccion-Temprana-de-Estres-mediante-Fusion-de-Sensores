# 🤖 Sistema de Chatbot Inteligente

Sistema de chatbot con integración de LLM y síntesis de voz para asistencia en detección de estrés.

## 📁 Archivos

- **inter_chatbot.py** - Interfaz principal del chatbot con Flet
- **prompts.py** - Configuración de prompts para Ollama LLM
- **test_chatbot.py** - Tests del sistema de chatbot

## 🚀 Uso

```bash
python inter_chatbot.py
```

## ⚙️ Características

- ✅ Chat de texto con Ollama LLM (llama3.2:3b-instruct-q8_0)
- ✅ Síntesis de voz en español (pyttsx3)
- ✅ Reconocimiento de voz (speech_recognition)
- ✅ Interfaz gráfica con Flet
- ✅ Respuestas contextuales sobre manejo de estrés

## 📋 Requisitos

- Ollama instalado con modelo `llama3.2:3b-instruct-q8_0`
- Voces TTS en español (ver [../docs/INSTALAR_VOCES_ESPAÑOL.md](../docs/INSTALAR_VOCES_ESPAÑOL.md))
- Dependencias en requirements.txt

## 🔧 Solución de Problemas

Si la voz no funciona en español, ejecutar:
```bash
python ../utils/verificar_voces.py
```

