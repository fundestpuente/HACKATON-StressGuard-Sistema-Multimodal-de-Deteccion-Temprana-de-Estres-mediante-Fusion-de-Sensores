# 🚀 GUÍA RÁPIDA DE USO - STRESSGUARD

## ⚡ Inicio Rápido (3 pasos)

### 1. Verificar el sistema
```bash
python verificar_sistema_completo.py
```

### 2. Iniciar el launcher
```bash
python launcher.py
```

### 3. Elegir modo de detección

---

## 🎯 Modos de Uso

### 🤖 Modo 1: Solo Chatbot
**¿Cuándo usar?**: Quieres conversar sin detección de estrés

**Pasos**:
1. Abrir launcher: `python launcher.py`
2. Click en **"Abrir Chatbot"** (tarjeta azul)
3. Conversar libremente con StressWard

**Características**:
- ✅ Conversación casual
- ✅ Sin contexto de estrés inicial
- ✅ Voz disponible (hablar/escuchar)

---

### 📷 Modo 2: Detector de Estrés por Imagen
**¿Cuándo usar?**: Quieres analizar tu estado mediante una foto

**Pasos**:
1. Abrir launcher: `python launcher.py`
2. Click en **"Abrir Detector"** (tarjeta morada)
3. Click en "📷 Seleccionar Imagen"
4. Elegir una foto facial (JPG/PNG/BMP)
5. Click en "🔍 Analizar Estrés"

**Resultados**:
- 📊 Probabilidades de: Non-Stress, Neutral, Stress
- 🎯 Clase predicha con confianza
- 🤖 Si detecta estrés → Chatbot se abre automáticamente

**Requisitos previos**:
```bash
# Si el modelo no está entrenado:
python entrenar_modelo_imagen.py
```

---

### ⌚ Modo 3: Sistema de Detección por Sensores
**¿Cuándo usar?**: Simular un reloj Samsung con sensores biométricos

**Pasos**:
1. Abrir launcher: `python launcher.py`
2. Click en **"Iniciar Sistema"** (tarjeta verde)
3. Se abrirá el simulador de reloj
4. Ajustar sensores con los sliders:
   - **EDA** (principal): >2.0 μS indica estrés
   - **BVP**: Variabilidad cardíaca
   - **Temperatura**: Temperatura corporal
5. Ver predicción en tiempo real
6. Si detecta estrés → Chatbot se abre automáticamente

**Detener sistema**:
- Click en **"Detener"** en el launcher

**Sensores por defecto**:
- 🟢 **EDA**: 0.4 μS (relajado)
- 🟢 **BVP**: 2.3 (normal)
- 🟢 **Temperatura**: 32.5°C (normal)

**Para simular estrés**:
- 🔴 Mover **EDA** a 2.5+ μS
- 🔴 Mover **BVP** a 0-1 (estrés)

---

## 🎓 Casos de Uso Prácticos

### Caso 1: Autoevaluación rápida con foto
```
1. Tomar selfie en el momento actual
2. Usar Modo 2 (Detector de Imagen)
3. Subir la foto
4. Ver análisis instantáneo
5. Si hay estrés → Chatbot da recomendaciones
```

### Caso 2: Monitoreo continuo con sensores
```
1. Usar Modo 3 (Sistema de Sensores)
2. Dejar el simulador abierto
3. Ajustar valores manualmente según sensación
4. Sistema alerta cuando detecta estrés
5. Chatbot interviene automáticamente
```

### Caso 3: Exploración del chatbot
```
1. Usar Modo 1 (Solo Chatbot)
2. Conversar sobre estrés, ansiedad, técnicas
3. Probar comandos de voz (botones 🎤 y 🔊)
4. Explorar recomendaciones personalizadas
```

---

## 🔧 Solución de Problemas

### ❌ "Modelo no encontrado" (Detector de Imagen)
**Solución**:
```bash
python entrenar_modelo_imagen.py
```

### ❌ "Ollama no responde" (Chatbot)
**Solución**:
```bash
# 1. Descargar Ollama desde: https://ollama.ai
# 2. Instalar
# 3. Ejecutar:
ollama pull llama3.2
```

### ❌ "Error al cargar modelo ML" (Sensores)
**Solución**:
```bash
# El modelo ML ya debería existir
# Verificar en: MachineLearning/best_wesad_xgboost_con_smote_model_v2.pkl
```

### ⚠️ Chatbot no se abre automáticamente
**Verificar**:
1. Que el launcher esté abierto
2. Que Ollama esté ejecutándose
3. Ver logs en la consola del launcher

### ⚠️ Error al instalar dependencias
**Solución**:
```bash
# Si tienes Python 3.14, bajar scikit-learn:
pip install scikit-learn==1.7.2

# Instalar todas las dependencias:
pip install -r MachineLearning/requirements.txt
pip install tensorflow opencv-python
```

---

## 📊 Interpretación de Resultados

### Detector de Imagen

| Resultado | Significado | Acción |
|-----------|-------------|--------|
| 🟢 **Non-Stress** (>70%) | Sin señales de estrés | Ninguna |
| 🟠 **Neutral** (>50%) | Estado ambiguo | Observar |
| 🔴 **Stress** (>60%) | Estrés detectado | Chatbot se abre |

### Simulador de Sensores

| Sensor | Rango Normal | Rango Estrés | Indicador |
|--------|--------------|--------------|-----------|
| **EDA** | 0.2-1.0 μS | >2.0 μS | ⭐ PRINCIPAL |
| **BVP** | 2-10 | <1 o >15 | Secundario |
| **Temp** | 32-33°C | 33.5+°C | Menor |

**Predicción**:
- 🟢 **Probabilidad < 30%**: Sin estrés
- 🟡 **Probabilidad 30-70%**: Zona intermedia
- 🔴 **Probabilidad > 70%**: Estrés detectado → Alerta

---

## 💡 Consejos de Uso

### Para mejor detección por imagen:
- ✅ Usar fotos frontales
- ✅ Buena iluminación
- ✅ Rostro visible y claro
- ❌ Evitar fotos borrosas
- ❌ Evitar ángulos extremos

### Para mejor simulación de sensores:
- ✅ EDA es el factor más importante
- ✅ Subir EDA gradualmente para ver cambio
- ✅ Observar la "Zona de Detección" (naranja/roja)
- ✅ Ver probabilidad en tiempo real

### Para mejor experiencia con chatbot:
- ✅ Ser específico en las consultas
- ✅ Usar comandos de voz si prefieres hablar
- ✅ Seguir las recomendaciones paso a paso
- ✅ Cerrar el chatbot cuando termines (solo 1 instancia)

---

## 📚 Documentación Adicional

- **Launcher**: Ver `README_LAUNCHER.md`
- **Chatbot**: Ver `MachineLearning/README_CHATBOT_INTELIGENTE.md`
- **Detector Imagen**: Ver `DeepLearning/README_DETECTOR_IMAGEN.md`
- **Organización**: Ver `docs/README_ORGANIZACION.md`

---

## 🎯 Flujo Completo Recomendado

```
1. Verificar sistema
   ↓
   python verificar_sistema_completo.py
   ↓
2. Si falta algo → Instalar/Entrenar
   ↓
3. Iniciar launcher
   ↓
   python launcher.py
   ↓
4. Elegir modo según necesidad:
   
   Solo conversar → Modo 1 (Chatbot)
   Analizar foto → Modo 2 (Imagen)
   Monitoreo continuo → Modo 3 (Sensores)
   ↓
5. Si detecta estrés → Chatbot interviene
   ↓
6. Seguir recomendaciones
   ↓
7. Cerrar cuando termines
```

---

## ⚙️ Configuración Avanzada

### Cambiar puerto del receptor (sensores):
Editar en `MachineLearning/receptor_datos.py` y `simu_reloj.py`:
```python
PORT = 65432  # Cambiar a otro puerto si 65432 está ocupado
```

### Ajustar umbral de detección (sensores):
Editar en `MachineLearning/receptor_datos.py`:
```python
# Cambiar de 0.7 (70%) a otro valor
if probabilidad >= 0.7:  # Umbral de estrés
```

### Personalizar prompts del chatbot:
Editar en `Chatbot/prompts.py`

---

**Última actualización**: 2024  
**Versión**: 1.0  
**Desarrollado por**: StressGuard Team
