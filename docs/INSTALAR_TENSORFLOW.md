# 📦 Instalación de Dependencias - Detector de Imagen

## ⚠️ Problema

Si al abrir el **Detector de Estrés por Imagen** ves el mensaje:

```
❌ Dependencias Faltantes
Faltan las siguientes librerías:
• TensorFlow
• OpenCV
```

Sigue estas instrucciones:

---

## ✅ Solución Rápida

### Windows (PowerShell/CMD)

```powershell
pip install tensorflow opencv-python numpy Pillow
```

### Linux/Mac (Terminal)

```bash
pip3 install tensorflow opencv-python numpy Pillow
```

---

## 📋 Instalación Paso a Paso

### 1. Abrir Terminal

**Windows:**
- Presiona `Win + R`
- Escribe `powershell`
- Presiona Enter

**Linux/Mac:**
- Busca "Terminal" en aplicaciones

### 2. Navegar al Proyecto (Opcional)

```bash
cd "c:\Users\59399\Documentos\EPN\Samsung\Hackaton\HACKATON-StressGuard..."
```

### 3. Instalar Dependencias

```bash
pip install tensorflow opencv-python numpy Pillow
```

**Tiempo estimado:** 5-10 minutos (depende de tu conexión)

### 4. Verificar Instalación

```bash
python -c "import tensorflow; import cv2; print('✅ Todo instalado correctamente')"
```

Si ves `✅ Todo instalado correctamente`, ¡listo!

---

## 🔧 Solución de Problemas

### Error: "pip no se reconoce"

**Solución:**
```bash
python -m pip install tensorflow opencv-python numpy Pillow
```

### Error: "Permission denied"

**Windows (ejecutar PowerShell como Administrador):**
```powershell
pip install --user tensorflow opencv-python numpy Pillow
```

**Linux/Mac:**
```bash
sudo pip3 install tensorflow opencv-python numpy Pillow
```

### Error: "No matching distribution found"

Actualizar pip:
```bash
python -m pip install --upgrade pip
```

Luego reintentar:
```bash
pip install tensorflow opencv-python numpy Pillow
```

### TensorFlow tarda mucho en descargar

TensorFlow es una librería grande (~400MB). Es normal que tarde.

**Alternativa ligera (solo CPU):**
```bash
pip install tensorflow-cpu opencv-python numpy Pillow
```

---

## 📊 Requisitos del Sistema

### Mínimos
- Python 3.8 o superior
- 2 GB de RAM libre
- 2 GB de espacio en disco

### Recomendados
- Python 3.9 o 3.10
- 4 GB de RAM libre
- 5 GB de espacio en disco
- GPU (opcional, para entrenamiento más rápido)

---

## ✅ Verificación Completa

Ejecuta este script para verificar todo:

```bash
python verificar_sistema_completo.py
```

Debería mostrar:
```
✅ TensorFlow: X.X.X
✅ OpenCV: X.X.X
✅ NumPy: X.X.X
```

---

## 🚀 Después de Instalar

1. **Cerrar el detector** si está abierto
2. **Volver a abrir desde el launcher:**
   ```bash
   python launcher.py
   ```
3. Click en **"Abrir Detector"** (tarjeta morada)
4. ¡Ahora debería funcionar!

---

## 📝 Dependencias Específicas

| Librería | Versión | Propósito |
|----------|---------|-----------|
| **tensorflow** | ≥2.10.0 | Deep Learning (modelo CNN) |
| **opencv-python** | ≥4.8.0 | Procesamiento de imágenes |
| **numpy** | ≥1.24.0 | Cálculos numéricos |
| **Pillow** | ≥10.0.0 | Manejo de imágenes |
| **flet** | ≥0.24.0 | Interfaz gráfica (ya instalado) |

---

## 🔄 Instalar Todo el Sistema

Si prefieres instalar TODAS las dependencias del proyecto:

```bash
# Machine Learning (sensores)
pip install -r MachineLearning/requirements.txt

# Deep Learning (imágenes)
pip install tensorflow opencv-python numpy Pillow

# Interfaz y chatbot
pip install flet requests pyttsx3 SpeechRecognition
```

---

## ❓ FAQ

### ¿Por qué no están instaladas por defecto?

TensorFlow es muy grande (~400MB) y no todos los usuarios necesitan el detector de imágenes.

### ¿Puedo usar el sistema sin el detector de imagen?

Sí, puedes usar:
- ✅ Chatbot manual
- ✅ Sistema de detección por sensores (simulador de reloj)

Solo el detector de imagen requiere TensorFlow.

### ¿Afecta al resto del sistema?

No. Las otras partes del sistema (chatbot, simulador) funcionan independientemente.

---

## 🆘 Ayuda Adicional

Si sigues teniendo problemas:

1. **Verificar versión de Python:**
   ```bash
   python --version
   ```
   Debe ser 3.8 o superior.

2. **Reinstalar Python** si es muy antiguo:
   - Descargar de: https://www.python.org/downloads/

3. **Usar un entorno virtual** (avanzado):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   pip install tensorflow opencv-python numpy Pillow
   ```

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0
