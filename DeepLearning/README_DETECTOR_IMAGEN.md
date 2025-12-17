# 📷 Detector de Estrés por Imagen

## Descripción

El **Detector de Estrés por Imagen** es un módulo de Deep Learning que analiza fotografías faciales para detectar señales de estrés utilizando redes neuronales convolucionales (CNN) con transfer learning de MobileNetV2.

---

## 🎯 Características

- ✅ **Análisis facial**: Detecta estrés en expresiones faciales
- ✅ **3 clases**: Non-Stress, Stress, Neutral
- ✅ **Transfer Learning**: Usa MobileNetV2 pre-entrenado
- ✅ **Interfaz visual**: Flet UI con preview de imagen
- ✅ **Probabilidades**: Muestra confianza para cada clase
- ✅ **Integración automática**: Abre chatbot si detecta estrés
- ✅ **Formatos aceptados**: JPG, PNG, BMP

---

## 📁 Archivos

### 1. `stress_detector_model.py`
Clase principal del detector con métodos:
- `load_model()`: Carga el modelo entrenado
- `predict_stress()`: Predice estrés en una imagen
- Retorna: `{'class': str, 'confidence': float, 'probabilities': dict}`

### 2. `train_stress_model.py`
Script para entrenar el modelo:
- Usa dataset con 3 clases
- Arquitectura: MobileNetV2 + capas personalizadas
- Data augmentation para mejor generalización
- Guarda modelo en `stress_model.h5`

### 3. `predict_stress.py`
Script de línea de comandos para predicciones:
```bash
python predict_stress.py ruta/a/imagen.jpg
```

### 4. `detector_imagen.py` (Raíz del proyecto)
Interfaz gráfica con Flet:
- File picker para seleccionar imágenes
- Preview de la imagen
- Análisis con visualización de resultados
- Apertura automática del chatbot si detecta estrés

---

## 🚀 Uso desde el Launcher

1. **Abrir el launcher**:
   ```bash
   python launcher.py
   ```

2. **Seleccionar "Detector por Imagen"**
   - Icono morado de cámara
   - Click en "Abrir Detector"

3. **Usar el detector**:
   - Click en "📷 Seleccionar Imagen"
   - Elegir una foto facial
   - Click en "🔍 Analizar Estrés"
   - Ver resultados con probabilidades

4. **Si detecta estrés**:
   - Muestra alerta roja
   - Abre automáticamente el chatbot (espera 2 segundos)
   - El chatbot ayuda a manejar el estrés

---

## 🧠 Arquitectura del Modelo

```python
Base: MobileNetV2 (ImageNet)
    ↓
GlobalAveragePooling2D
    ↓
Dense(128, relu) + Dropout(0.5)
    ↓
Dense(3, softmax)  # Non-Stress, Stress, Neutral
```

**Entrada**: 224x224x3 (RGB)  
**Salida**: 3 probabilidades (suma = 1.0)

---

## 📊 Clases de Predicción

| Clase | Descripción | Color | Acción |
|-------|-------------|-------|--------|
| **Non-Stress** | Sin señales de estrés | 🟢 Verde | Ninguna |
| **Neutral** | Estado neutro/ambiguo | 🟠 Naranja | Ninguna |
| **Stress** | Estrés detectado | 🔴 Rojo | Abre chatbot |

---

## 🎨 Interfaz Visual

La interfaz muestra:

1. **Estado del modelo**: Verifica si está cargado
2. **Selector de imagen**: File picker con formatos JPG/PNG/BMP
3. **Preview**: Vista previa de la imagen seleccionada
4. **Botón analizar**: Ejecuta la predicción
5. **Resultados**:
   - Icono grande indicando clase
   - Mensaje claro (ej: "⚠️ ESTRÉS DETECTADO")
   - Confianza principal en porcentaje
   - 3 tarjetas con probabilidades de cada clase
   - Mensaje de acción si aplica

---

## 📝 Ejemplo de Uso Programático

```python
from DeepLearning.stress_detector_model import StressDetector

# Crear detector
detector = StressDetector()
detector.load_model('DeepLearning/stress_model.h5')

# Analizar imagen
result = detector.predict_stress('foto.jpg')

print(f"Clase: {result['class']}")
print(f"Confianza: {result['confidence']:.1%}")
print(f"Prob Estrés: {result['probabilities']['Stress']:.1%}")

# Verificar si hay estrés
if result['class'] == 'Stress':
    print("⚠️ Estrés detectado - abriendo chatbot...")
```

---

## ⚙️ Configuración

### Ruta del Modelo
Por defecto busca el modelo en:
```
DeepLearning/stress_model.h5
```

Si no existe, se muestra un mensaje indicando que debe entrenarse.

### Entrenar Modelo

1. Preparar dataset en `DeepLearning/data2/`:
   ```
   data2/
   ├── train/
   │   ├── Non-Stress/
   │   ├── Stress/
   │   └── Neutral/
   └── valid/
       ├── Non-Stress/
       ├── Stress/
       └── Neutral/
   ```

2. Ejecutar entrenamiento:
   ```bash
   cd DeepLearning
   python train_stress_model.py
   ```

3. El modelo se guardará en `stress_model.h5`

---

## 🔄 Flujo de Detección

```
Usuario selecciona imagen
        ↓
Preview en interfaz
        ↓
Click "Analizar Estrés"
        ↓
Modelo predice clase + probabilidades
        ↓
Muestra resultados visuales
        ↓
¿Clase == Stress?
    ├─ Sí → Espera 2s → Abre chatbot
    └─ No → Fin
```

---

## 🎯 Casos de Uso

1. **Detección rápida**: Usuario toma selfie y analiza su estado
2. **Monitoreo continuo**: Análisis periódico de fotos
3. **Validación cruzada**: Combinar con sensor del reloj
4. **Investigación**: Analizar expresiones en diferentes contextos

---

## ⚠️ Notas Importantes

- ✅ El detector funciona **completamente local** (no requiere internet)
- ✅ Las imágenes **no se guardan** ni se envían a ningún servidor
- ✅ El modelo debe estar entrenado antes de usar
- ✅ Mejor desempeño con fotos frontales y buena iluminación
- ✅ La privacidad del usuario está garantizada

---

## 🛠️ Troubleshooting

### "⚠️ Modelo no encontrado"
**Solución**: Entrenar el modelo con `train_stress_model.py`

### "❌ Error al cargar modelo"
**Solución**: Verificar que TensorFlow esté instalado:
```bash
pip install tensorflow opencv-python numpy
```

### "Error al analizar imagen"
**Solución**: 
- Verificar que la imagen sea válida (JPG/PNG/BMP)
- Asegurar que la imagen contiene un rostro visible
- Revisar que no esté corrupta

---

## 📚 Dependencias

```txt
tensorflow>=2.10.0
opencv-python>=4.8.0
numpy>=1.24.0
Pillow>=10.0.0
flet>=0.24.0
```

Instalar con:
```bash
pip install -r DeepLearning/requirements.txt
```

---

## 🔗 Integración con el Sistema

El detector se integra perfectamente con:

- **Chatbot**: Se abre automáticamente al detectar estrés
- **Launcher**: Accesible desde el menú principal
- **Sistema completo**: Complementa la detección por sensores

---

## 📈 Futuras Mejoras

- [ ] Análisis de video en tiempo real
- [ ] Detección de múltiples rostros
- [ ] Historial de análisis
- [ ] Exportar reportes
- [ ] Integración con cámara web
- [ ] Versión mobile (Flutter)

---

**Desarrollado por**: StressGuard Team  
**Versión**: 1.0  
**Fecha**: 2024
