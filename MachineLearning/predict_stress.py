import numpy as np
from stress_model import load_model, predict_stress

# Cargar el pipeline
pipeline = load_model()

# Datos de ejemplo (valores simulados de sensores)
bvp = 30.0  # Señal BVP
temp = 36.0  # Temperatura
eda = 1.0    # EDA

# Predecir estrés
prediccion = predict_stress(bvp, temp, eda, pipeline)
print(f"Predicción de estrés: {prediccion}")