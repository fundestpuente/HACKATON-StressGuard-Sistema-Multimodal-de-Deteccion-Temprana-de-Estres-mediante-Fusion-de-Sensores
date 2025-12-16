"# Sistema de Detección de Estrés - Proyecto IA

Sistema de detección de estrés en tiempo real utilizando Machine Learning con datos de sensores fisiológicos del dataset WESAD.

## 📋 Características

- **Modelo ML**: XGBoost entrenado con dataset WESAD
- **Sensores**: BVP, EDA, Temperatura
- **Interfaz**: Simulador web con Flet
- **Comunicación**: Socket TCP para alertas en tiempo real

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd SIC_Proyecto_IA
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Descargar modelo pre-entrenado
El modelo `best_wesad_xgboost_no_smote_model.pkl` debe estar en la raíz del proyecto.
**Nota**: Por su tamaño no está en el repositorio. Descárgalo desde [enlace] o entrena uno nuevo con el notebook.

## 📦 Estructura del Proyecto

```
.
├── stress_model.py           # Modelo ML y funciones de predicción
├── simu_reloj.py            # Simulador de sensores (Flet)
├── receptor_datos.py        # Receptor de alertas por socket
├── predict_stress.py        # Script de prueba
├── wesad-completo-cloud.ipynb  # Notebook de entrenamiento
├── best_wesad_xgboost_no_smote_model.pkl  # Modelo entrenado (no incluido)
└── requirements.txt         # Dependencias Python
```

## 🎮 Uso

### Iniciar el sistema completo

1. **Terminal 1 - Receptor de alertas**:
```bash
python receptor_datos.py
```

2. **Terminal 2 - Simulador**:
```bash
python simu_reloj.py
```

El simulador abrirá una interfaz web donde puedes ajustar los valores de los sensores.

### Entrenar nuevo modelo

Abre y ejecuta el notebook `wesad-completo-cloud.ipynb` para:
- Descargar dataset WESAD desde Kaggle
- Entrenar modelo XGBoost
- Guardar modelo como `best_wesad_xgboost_no_smote_model.pkl`

## 🔧 Configuración

- **Puerto**: 65432 (modificable en `simu_reloj.py` y `receptor_datos.py`)
- **Frecuencia de envío**: 2 segundos
- **Umbrales**: Configurados automáticamente por el modelo ML

## 📊 Dataset

- **Nombre**: WESAD (Wearable Stress and Affect Detection)
- **Fuente**: Kaggle
- **Características usadas**: BVP, EDA, Temperatura
- **Clases**: 0 (sin estrés), 1 (con estrés)

## 🧪 Tecnologías

- Python 3.14
- XGBoost
- scikit-learn
- Flet (UI)
- pandas, numpy
- joblib

## 👥 Autores

Proyecto IA - EPN Samsung

## 📝 Licencia" 
