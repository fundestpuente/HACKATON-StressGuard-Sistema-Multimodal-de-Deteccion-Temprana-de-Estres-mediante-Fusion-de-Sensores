# Código para guardar, cargar y hacer inferencia con el modelo de Random Forest.

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Función para guardar el modelo entrenado y el scaler
def save_model(model, scaler, model_path='stress_rf_model.pkl', scaler_path='scaler.pkl'):
    """
    Guarda el modelo Random Forest entrenado y el scaler en archivos separados.
    Parámetros:
    - model: Modelo RandomForestClassifier entrenado
    - scaler: StandardScaler ajustado
    - Ruta donde guardar el modelo ('stress_rf_model.pkl')
    - Ruta donde guardar el scaler ('scaler.pkl')
    """
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"Modelo guardado en {model_path}")
    print(f"Scaler guardado en {scaler_path}")

# Función para cargar el pipeline completo
def load_model(model_path='best_wesad_xgboost_con_smote_model_v2.pkl'):
    """
    Carga el pipeline completo (StandardScaler + SMOTE + XGBoost).

    Parámetros:
    - model_path: Ruta del archivo del pipeline

    Retorna:
    - pipeline: Pipeline completo (scaler + smote + modelo)
    
    NOTA: Requiere sklearn 1.7.1 e imbalanced-learn
    """
    pipeline = joblib.load(model_path)
    print(f"Pipeline CON SMOTE cargado desde {model_path}")
    return pipeline

# Función de inferencia
def predict_stress(bvp, temp, eda, pipeline):
    """
    Realiza la predicción de estrés basada en los valores de los sensores.
    Parámetros:
    - bvp: Señal de volumen de pulso sanguíneo
    - temp: Temperatura
    - eda: Actividad electrodérmica
    - pipeline: Pipeline completo (scaler + smote + modelo XGBoost)

    Retorna:
    - stress = 1 (estrés) o stress = 0 (no estrés)
    """
    import pandas as pd
    
    # Usar DataFrame con nombres de características para evitar warnings
    features = pd.DataFrame([[bvp, eda, temp]], columns=['bvp', 'eda', 'temp'])

    # El pipeline incluye scaler y SMOTE (solo para fit), luego predice
    prediction = pipeline.predict(features)[0]
    
    # Imprimir el resultado
    print(f"stress = {int(prediction)}")
    
    return int(prediction)


if __name__ == "__main__":
    # Cargar el pipeline
    pipeline = load_model()

    # Valores de entrada simulados (ejemplo)
    bvp = 0.5  # Señal BVP
    temp = 36.5  # Temperatura
    eda = 0.2  # Actividad electrodérmica

    # Realizar la predicción
    predict_stress(bvp, temp, eda, pipeline)