# ⚠️ IMPORTANTE - Python 3.14 vs Python 3.12

## 🔴 Problema Detectado

TensorFlow (necesario para Deep Learning) **NO soporta Python 3.14** todavía.

## ✅ Solución Implementada

Se ha instalado **Python 3.12** adicional que SÍ tiene soporte para TensorFlow.

---

## 🎯 Cómo Usar el Sistema

### Sistema Principal (Python 3.14)
- ✅ Launcher
- ✅ Chatbot
- ✅ Sistema de sensores (simulador de reloj)
- ✅ Machine Learning con scikit-learn

### Detector de Imagen (Python 3.12)
- ✅ Análisis de estrés por fotos faciales
- ✅ Deep Learning con TensorFlow

---

## 🚀 Iniciar el Sistema

### Opción 1: Desde el Launcher (Recomendado)
```bash
python launcher.py
```

El launcher automáticamente usará:
- Python 3.14 para componentes principales
- Python 3.12 para detector de imagen

### Opción 2: Detector de Imagen Directo
```bash
py -3.12 detector_imagen.py
```

O doble click en: **DETECTOR_IMAGEN.bat**

---

## 📦 Estado de las Instalaciones

### Python 3.14 (Principal)
- ✅ Flet (interfaz)
- ✅ scikit-learn (ML sensores)
- ✅ Keras 3 + JAX backend
- ✅ OpenCV, NumPy, Pandas
- ❌ TensorFlow (no disponible)

### Python 3.12 (Para Deep Learning)
- ✅ TensorFlow 2.20.0
- ✅ Keras 3.12.0
- ✅ OpenCV 4.12.0.88
- ✅ Flet 0.28.3
- ✅ NumPy, Pandas, Matplotlib, Seaborn

---

## 🧠 Entrenar el Modelo de Imagen

### Primera vez - Entrenar:
```bash
# Opción 1: Script automático
ENTRENAR_MODELO.bat

# Opción 2: Manual
cd DeepLearning
py -3.12 train_stress_model.py
```

### Modelo Entrenado
Una vez entrenado, se guardará en:
```
DeepLearning/stress_model.h5
```

---

## 📊 Dataset

El dataset está en:
```
DeepLearning/data2/
├── train/ (785 imágenes)
├── valid/ (98 imágenes)
└── test/ (98 imágenes)
```

Clases:
- **Stress**: 307 imágenes (39.1%)
- **Neutral**: 478 imágenes (60.9%)
- **Non-Stress**: 0 imágenes (no hay datos)

---

## 🔄 Comandos Útiles

### Verificar Versiones de Python
```bash
# Python principal
python --version

# Python 3.12 (Deep Learning)
py -3.12 --version
```

### Verificar TensorFlow
```bash
py -3.12 -c "import tensorflow; print(tensorflow.__version__)"
```

### Listar Pythons Instalados
```bash
py --list
```

---

## ⚙️ Por Qué Dos Versiones de Python

| Componente | Python | Razón |
|------------|--------|-------|
| Sistema principal | 3.14 | Más reciente, mejor rendimiento general |
| Detector imagen | 3.12 | TensorFlow solo funciona hasta Python 3.12 |

**No es un error**, es la solución óptima hasta que TensorFlow soporte Python 3.14.

---

## 🆘 Troubleshooting

### Error: "py -3.12 no reconocido"
**Solución**: Instalar Python 3.12:
```bash
winget install Python.Python.3.12
```

### Error: "No module named tensorflow"
**Solución**: Instalar en Python 3.12:
```bash
py -3.12 -m pip install tensorflow opencv-python
```

### Detector muestra "Modelo no disponible"
**Solución**: Entrenar el modelo:
```bash
ENTRENAR_MODELO.bat
```

---

## 📝 Notas Adicionales

- El launcher gestiona automáticamente qué versión de Python usar
- No necesitas preocuparte por las versiones al usar el launcher
- Todo funcionará transparentemente

---

**Fecha**: Diciembre 17, 2025  
**Versión**: 1.0
