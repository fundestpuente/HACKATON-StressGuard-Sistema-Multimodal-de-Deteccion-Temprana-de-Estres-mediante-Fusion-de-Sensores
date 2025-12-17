# 📦 Guía de Instalación de Dependencias - StressGuard

## ✅ Instalación Completada

Todas las dependencias han sido instaladas correctamente:

### Paquetes Instalados

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| **flet** | 0.28.3 | Framework para interfaces gráficas |
| **scikit-learn** | 1.8.0 | Machine Learning (modelo de predicción) |
| **xgboost** | 3.1.2 | Modelo XGBoost para predicción de estrés |
| **numpy** | 2.3.5+ | Operaciones matemáticas |
| **pandas** | 2.3.3+ | Manejo de datos |
| **psutil** | 7.1.3 | Gestión de procesos del sistema |
| **pyttsx3** | 2.99+ | Texto a voz (TTS) |
| **SpeechRecognition** | 3.14.4 | Reconocimiento de voz |
| **requests** | 2.32.5+ | Comunicación HTTP con Ollama |

### Dependencias Secundarias

- **scipy** - Cálculos científicos
- **joblib** - Serialización de modelos ML
- **httpx** - Cliente HTTP asíncrono
- **oauthlib** - Autenticación
- **repath** - Enrutamiento

## 🚀 Próximos Pasos

### 1. Verificar Ollama

Asegúrate de tener Ollama instalado y el modelo descargado:

```bash
# Verificar que Ollama está instalado
ollama --version

# Descargar el modelo Llama 3.2
ollama pull llama3.2

# Iniciar el servidor de Ollama
ollama serve
```

### 2. Ejecutar el Sistema

Ahora puedes ejecutar el launcher:

**Opción 1 - Archivo Batch (Recomendado):**
```bash
INICIAR_STRESSGUARD.bat
```

**Opción 2 - Python directo:**
```bash
python launcher.py
```

## ⚠️ Notas Importantes

### PATH de Scripts

Se detectó que los scripts no están en el PATH:
```
C:\Users\59399\AppData\Roaming\Python\Python314\Scripts
```

**Esto no es un problema** ya que estamos ejecutando Python directamente, pero si quieres usar comandos como `flet` desde cualquier lugar:

1. Presiona `Win + R`
2. Escribe `sysdm.cpl` y presiona Enter
3. Ve a la pestaña "Avanzado"
4. Clic en "Variables de entorno"
5. En "Variables de usuario", selecciona "Path" y clic en "Editar"
6. Clic en "Nuevo" y agrega:
   ```
   C:\Users\59399\AppData\Roaming\Python\Python314\Scripts
   ```
7. Clic en "Aceptar" en todas las ventanas

### Actualizar pip (Opcional)

Hay una nueva versión de pip disponible:

```bash
python -m pip install --upgrade pip
```

## 🧪 Probar el Sistema

### Prueba 1: Launcher
```bash
python launcher.py
```
Deberías ver la interfaz gráfica del launcher.

### Prueba 2: Chatbot
```bash
cd Chatbot
python inter_chatbot.py
```
Deberías ver el chatbot en tu navegador.

### Prueba 3: Simulador
```bash
cd MachineLearning
python simu_reloj.py
```
Deberías ver el simulador de reloj en tu navegador.

## 🔧 Solución de Problemas

### Error: ModuleNotFoundError
Si aún ves este error, reinstala las dependencias:
```bash
pip install -r requirements.txt --force-reinstall
```

### Error: Ollama no responde
Asegúrate de que Ollama esté ejecutándose:
```bash
ollama serve
```

### Error: Puerto ocupado (65432)
Cambia el puerto en `receptor_datos.py` y `simu_reloj.py`

## 📊 Uso de Memoria

El sistema utilizará aproximadamente:
- **Launcher**: ~50 MB
- **Chatbot**: ~100 MB (+ Ollama ~2 GB)
- **Simulador**: ~100 MB
- **Receptor**: ~30 MB

**Total recomendado**: 4 GB RAM disponible

## ✅ Checklist de Instalación

- [x] Python 3.8+ instalado
- [x] Dependencias de Python instaladas
- [ ] Ollama instalado
- [ ] Modelo Llama 3.2 descargado
- [ ] Servidor Ollama ejecutándose

## 🎯 ¡Todo Listo!

Ahora puedes ejecutar:
```bash
INICIAR_STRESSGUARD.bat
```

O directamente:
```bash
python launcher.py
```

---

**Última actualización**: Diciembre 2025  
**Estado**: ✅ Todas las dependencias instaladas correctamente
