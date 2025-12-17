# 🔧 Instrucciones para Usar Modelo con SMOTE

## 📊 Estado Actual

✅ **Modelo con SMOTE creado:** `best_wesad_xgboost_con_smote_model.pkl`  
⚠️ **No se puede usar actualmente** por incompatibilidad de versiones

---

## ⚠️ Problema de Compatibilidad

El modelo fue entrenado con:
- `scikit-learn 1.7.1`
- `imbalanced-learn` compatible con sklearn 1.7.1

Tu sistema tiene:
- `scikit-learn 1.8.0`
- `imbalanced-learn 0.14.0` (no compatible con sklearn 1.8.0)

**Error resultante:**
```
ImportError: cannot import name '_is_pandas_df' from 'sklearn.utils.validation'
```

---

## 🛠️ Soluciones

### Opción 1: Downgrade sklearn a 1.7.1 (Rápido)

```bash
# Desinstalar versión actual
python -m pip uninstall scikit-learn -y

# Instalar versión compatible
python -m pip install scikit-learn==1.7.1

# Verificar instalación
python -c "import sklearn; print(sklearn.__version__)"

# Ejecutar evaluación
python evaluar_modelo.py
```

**Después del downgrade, actualiza estos archivos:**

1. [stress_model.py](MachineLearning/stress_model.py) línea 24:
```python
def load_model(model_path='best_wesad_xgboost_con_smote_model.pkl'):
```

2. [evaluar_modelo.py](evaluar_modelo.py) líneas 19, 109, 135:
```python
model_path = os.path.join(os.path.dirname(__file__), 'MachineLearning', 'best_wesad_xgboost_con_smote_model.pkl')
```

---

### Opción 2: Reentrenar con sklearn 1.8.0 (Recomendado)

Esta es la mejor solución a largo plazo.

#### Paso 1: Preparar datos
Asegúrate de tener `df_reduced` con las columnas: `bvp`, `eda`, `temp`, `stress`

#### Paso 2: Ejecutar reentrenamiento
```bash
cd MachineLearning
python reentrenar_modelo_con_smote.py
```

#### Paso 3: Verificar modelo generado
El script creará:
- `best_wesad_xgboost_con_smote_model.pkl` (nuevo, compatible)
- `best_wesad_xgboost_sin_smote_model.pkl` (para comparar)

#### Paso 4: Evaluar
```bash
python ../evaluar_modelo.py
```

---

### Opción 3: Usar modelo SIN SMOTE (Actual)

El sistema está configurado para usar el modelo SIN SMOTE que es compatible:

```bash
python evaluar_modelo.py
```

**Limitaciones:**
- No balancea clases
- Puede tener sesgo hacia clase mayoritar ia
- Precisión reducida en datasets desbalanceados

---

## 📝 Código SMOTE Simplificado

Si vas a reentrenar, aquí está el código esencial:

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib

# 1. Preparar datos
X = df_reduced[['bvp', 'eda', 'temp']]
y = df_reduced['stress']

# 2. Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. Pipeline con SMOTE
pipeline = ImbPipeline([
    ('scaler', StandardScaler()),
    ('smote', SMOTE(random_state=42)),
    ('classifier', XGBClassifier(
        n_estimators=100,
        max_depth=10,
        learning_rate=0.1,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    ))
])

# 4. Entrenar
pipeline.fit(X_train, y_train)

# 5. Guardar
joblib.dump(pipeline, 'best_wesad_xgboost_con_smote_model.pkl')
```

---

## 🎯 Recomendación Final

**Para desarrollo rápido:** Usa Opción 1 (downgrade)  
**Para producción:** Usa Opción 2 (reentrenar)

**Pasos sugeridos:**
1. Downgrade sklearn a 1.7.1
2. Probar modelo con SMOTE
3. Si funciona bien, planificar reentrenamiento con sklearn 1.8.0
4. Actualizar requirements.txt con versiones fijas

---

## 📦 requirements.txt Actualizado

Agrega estas líneas para fijar versiones:

```txt
# ML con SMOTE
scikit-learn==1.7.1
imbalanced-learn==0.12.0
xgboost>=2.0.0
```

O para usar versiones actuales:

```txt
# ML sin SMOTE (sklearn 1.8.0)
scikit-learn>=1.8.0
xgboost>=2.0.0
# imbalanced-learn pendiente de actualización
```

---

## 🧪 Verificar Instalación

```bash
python -c "import sklearn, imblearn; print(f'sklearn: {sklearn.__version__}'); print(f'imblearn: {imblearn.__version__}')"
```

Salida esperada (Opción 1):
```
sklearn: 1.7.1
imblearn: 0.12.0
```

Salida actual:
```
sklearn: 1.8.0
imblearn: 0.14.0 (incompatible)
```

---

## 📞 Soporte

Si tienes problemas:
1. Verifica versiones con el comando de arriba
2. Revisa que `df_reduced` tenga las columnas correctas
3. Ejecuta `verificar_sistema.py` para diagnóstico completo
