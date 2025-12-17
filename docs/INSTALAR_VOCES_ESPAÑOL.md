# 🔊 Guía para Instalar Voces en Español en Windows

## Problema Identificado
El chatbot StressGuard está usando voces en inglés porque **no hay voces en español instaladas** en tu sistema Windows.

**Voces actuales disponibles:**
- Microsoft David Desktop - English (United States) 🇺🇸
- Microsoft Zira Desktop - English (United States) 🇺🇸

---

## 🎯 Soluciones

### Opción 1: Instalar Voces de Windows (RECOMENDADO)

#### Para Windows 10/11:

1. **Abrir Configuración de Windows**
   - Presiona `Win + I`
   - O ve a Inicio > Configuración ⚙️

2. **Navegar a Configuración de Voz**
   - **Windows 11**: Hora e idioma > Voz
   - **Windows 10**: Hora e idioma > Región e idioma

3. **Agregar Español**
   - Busca "Agregar idioma" o "Add a language"
   - Selecciona **Español (España)** o **Español (México)**
   - Marca la opción "Conversión de texto a voz"
   - Haz clic en "Instalar"

4. **Descargar paquete de voz**
   - Una vez instalado el idioma, ve a:
     - Configuración > Hora e idioma > Voz
     - Selecciona una voz en español (ej: "Helena", "Sabina", "Laura")

5. **Reiniciar el chatbot**
   - Cierra el chatbot si está abierto
   - Ejecuta nuevamente `python Chatbot/verificar_voces.py`
   - Deberías ver voces en español ahora

---

### Opción 2: Usar gTTS (Google Text-to-Speech) - Alternativa con Internet

Si no puedes instalar voces en Windows, puedes modificar el chatbot para usar gTTS (requiere conexión a internet):

#### Instalar gTTS:
```bash
pip install gtts pygame
```

#### Código para reemplazar en inter_chatbot.py:

```python
# ================================
# TEXTO A VOZ CON GTTS (Requiere Internet)
# ================================
from gtts import gTTS
import pygame
import tempfile
import os

def hablar(texto):
    def _hablar():
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                temp_file = fp.name
            
            # Generar audio con Google TTS
            tts = gTTS(text=texto, lang='es', slow=False)
            tts.save(temp_file)
            
            # Reproducir audio
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Esperar a que termine
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Limpiar
            pygame.mixer.quit()
            os.unlink(temp_file)
            
        except Exception as e:
            print(f"❌ Error TTS: {e}")

    threading.Thread(target=_hablar, daemon=True).start()
```

---

### Opción 3: Usar pyttsx3 con voz en inglés (Temporal)

El chatbot ya está configurado para usar la voz disponible si no encuentra español. Simplemente **desactiva la voz** con el botón 🔊 en el chat para evitar escuchar el inglés.

---

## 🧪 Verificar Voces Instaladas

Después de instalar voces, ejecuta:

```bash
cd Chatbot
python verificar_voces.py
```

Deberías ver algo como:

```
✅ VOZ EN ESPAÑOL ENCONTRADA #2:
   Nombre: Microsoft Helena Desktop - Spanish (Spain)
   ID: HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_HELENA_11.0
```

---

## 📝 Voces en Español Comunes en Windows

| Nombre | Idioma | Género | Región |
|--------|--------|--------|--------|
| Helena | Español | Femenino | España 🇪🇸 |
| Laura | Español | Femenino | España 🇪🇸 |
| Pablo | Español | Masculino | España 🇪🇸 |
| Sabina | Español | Femenino | México 🇲🇽 |
| Raul | Español | Masculino | México 🇲🇽 |

---

## ⚡ Solución Rápida (Sin instalar nada)

Si no quieres instalar voces ahora, simplemente:

1. Abre el chatbot
2. Haz clic en el botón 🔊 (arriba a la derecha)
3. Esto desactivará la voz
4. Sigue usando el chatbot normalmente en modo texto

---

## 🐛 Problemas Comunes

### "No se encuentra la voz después de instalar"

**Solución:**
1. Reinicia Windows
2. Verifica que descargaste el paquete de "Texto a voz" completo
3. Ejecuta `verificar_voces.py` nuevamente

### "La voz suena robótica"

**Solución:**
- Las voces de Windows son sintéticas
- Para mejor calidad, usa gTTS (Opción 2)

### "Error: engine.say() no funciona"

**Solución:**
```bash
pip uninstall pyttsx3
pip install pyttsx3==2.90
```

---

## 📞 Soporte

Si tienes problemas:
1. Ejecuta `Chatbot/verificar_voces.py` y comparte el resultado
2. Verifica la versión de Windows: `Win + R` → `winver`
3. Comprueba que tienes conexión a internet (para gTTS)

---

**Estado Actual del Chatbot:**
- ✅ Chatbot funcional
- ✅ Ollama/LLM operativo
- ⚠️ Voz en español NO instalada
- ✅ Opción de desactivar voz disponible

**Siguiente paso recomendado:** Instalar voces en español (Opción 1) o usar gTTS (Opción 2)
