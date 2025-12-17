"""
quick_fix.py
Mejora rápida en 1 hora para modelo con 87% accuracy
Enfocado en reducir confusión con clase Stress
"""

import numpy as np
from stress_detector_model import StressDetector, load_all_datasets
from tensorflow import keras
import os

# ==============================================================================
# ESTRATEGIA 1: AJUSTAR THRESHOLD DE DECISIÓN (15 min)
# ==============================================================================

def optimize_threshold(model_path='models/stress_model_final.h5', data_root='data2'):
    """
    Encuentra el threshold óptimo para la clase Stress
    Reduce falsos positivos/negativos
    """
    print("="*60)
    print("🎯 OPTIMIZACIÓN DE THRESHOLD PARA STRESS")
    print("="*60)
    
    # Cargar datos de validación
    print("\n📂 Cargando datos de validación...")
    (_, _), (X_val, y_val), (_, _) = load_all_datasets(data_root)
    
    # Cargar modelo
    detector = StressDetector()
    detector.load_model(model_path)
    
    # Obtener predicciones (probabilidades)
    print("🔍 Calculando predicciones...")
    predictions = detector.model.predict(X_val, verbose=0)
    
    # Probar diferentes thresholds para la clase Stress
    best_threshold = 0.5
    best_accuracy = 0
    best_balance = 0
    
    print("\n📊 Probando thresholds...")
    print("-" * 60)
    print(f"{'Threshold':<12} {'Accuracy':<10} {'Prec(S)':<10} {'Rec(S)':<10} {'Balance':<10}")
    print("-" * 60)
    
    results = []
    
    for threshold in np.arange(0.3, 0.8, 0.05):
        # Aplicar threshold custom
        y_pred_custom = np.argmax(predictions, axis=1)
        
        # Si queremos ser más conservadores con Stress, aumentar threshold
        # Si queremos detectar más Stress, bajar threshold
        stress_probs = predictions[:, 1]  # Probabilidad de Stress
        
        # Ajustar predicciones basado en threshold
        for i in range(len(y_pred_custom)):
            if stress_probs[i] >= threshold and y_pred_custom[i] != 1:
                # Forzar a Stress si supera threshold
                if stress_probs[i] > predictions[i, y_pred_custom[i]]:
                    y_pred_custom[i] = 1
            elif stress_probs[i] < threshold and y_pred_custom[i] == 1:
                # Quitar Stress si no supera threshold
                second_best = np.argsort(predictions[i])[-2]
                y_pred_custom[i] = second_best
        
        # Calcular métricas
        accuracy = np.mean(y_val == y_pred_custom)
        
        # Métricas específicas para Stress
        stress_mask_true = y_val == 1
        stress_mask_pred = y_pred_custom == 1
        
        tp = np.sum(stress_mask_true & stress_mask_pred)
        fp = np.sum(~stress_mask_true & stress_mask_pred)
        fn = np.sum(stress_mask_true & ~stress_mask_pred)
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        balance = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        results.append({
            'threshold': threshold,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'balance': balance
        })
        
        print(f"{threshold:.2f}         {accuracy:.4f}     {precision:.4f}     {recall:.4f}     {balance:.4f}")
        
        if balance > best_balance:
            best_balance = balance
            best_threshold = threshold
            best_accuracy = accuracy
    
    print("-" * 60)
    print(f"\n✅ Mejor threshold encontrado: {best_threshold:.2f}")
    print(f"   Accuracy: {best_accuracy:.4f}")
    print(f"   Balance (F1): {best_balance:.4f}")
    
    return best_threshold, results


# ==============================================================================
# ESTRATEGIA 2: FINE-TUNING RÁPIDO (30-40 min)
# ==============================================================================

def quick_fine_tune(model_path='models/stress_model_final.h5', 
                    data_root='data2',
                    epochs=10):
    """
    Fine-tuning ultra rápido enfocado en clase Stress
    Solo 10 epochs con learning rate muy bajo
    """
    print("="*60)
    print("⚡ FINE-TUNING RÁPIDO (10 epochs)")
    print("="*60)
    
    # Cargar datos
    print("\n📂 Cargando datos...")
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = load_all_datasets(data_root)
    
    # Cargar modelo existente
    print(f"📥 Cargando modelo: {model_path}")
    detector = StressDetector()
    detector.load_model(model_path)
    
    # Incrementar class weight para Stress
    from sklearn.utils.class_weight import compute_class_weight
    
    # Forzar más peso a la clase Stress
    unique_classes = np.unique(y_train)
    class_weights = compute_class_weight('balanced', classes=unique_classes, y=y_train)
    
    # Aumentar el peso de Stress (clase 1) en 1.5x
    class_weights[1] *= 1.5
    
    class_weight_dict = {int(i): float(class_weights[i]) for i in range(len(class_weights))}
    
    print(f"\n⚖️  Class weights ajustados (más peso a Stress):")
    class_labels = {0: 'Non-Stress', 1: 'Stress', 2: 'Neutral'}
    for cls_id, weight in class_weight_dict.items():
        print(f"   {class_labels[cls_id]}: {weight:.3f}")
    
    # Descongelar últimas capas
    print("\n🔓 Descongelando últimas capas...")
    detector.model.trainable = True
    
    # Congelar todas menos las últimas 20 capas
    for layer in detector.model.layers[:-20]:
        layer.trainable = False
    
    # Recompilar con learning rate MUY bajo
    print("⚙️  Recompilando con learning rate ultra bajo...")
    detector.model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=5e-6),  # Ultra bajo
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy',
                keras.metrics.Precision(name='precision'),
                keras.metrics.Recall(name='recall')]
    )
    
    # Entrenar solo 10 epochs
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True),
        ModelCheckpoint('models/stress_model_quick_finetuned.h5', 
                       monitor='val_accuracy', save_best_only=True, verbose=0)
    ]
    
    print(f"\n🚀 Entrenando {epochs} epochs rápidos...")
    print("   (Esto tomará ~30-40 minutos)")
    
    history = detector.model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=32,
        class_weight=class_weight_dict,
        callbacks=callbacks,
        verbose=1
    )
    
    detector.history = history
    
    # Evaluar mejora
    print("\n📊 Evaluando mejora...")
    predictions = detector.model.predict(X_test, verbose=0)
    y_pred = np.argmax(predictions, axis=1)
    
    accuracy = np.mean(y_test == y_pred)
    
    # Métricas de Stress
    stress_mask_true = y_test == 1
    stress_mask_pred = y_pred == 1
    
    tp = np.sum(stress_mask_true & stress_mask_pred)
    fp = np.sum(~stress_mask_true & stress_mask_pred)
    fn = np.sum(stress_mask_true & ~stress_mask_pred)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    print(f"\n✅ Resultados después de fine-tuning:")
    print(f"   Accuracy general: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"   Precision (Stress): {precision:.4f}")
    print(f"   Recall (Stress): {recall:.4f}")
    
    # Guardar
    detector.save_model('models/stress_model_quick_fixed.h5')
    
    return detector


# ==============================================================================
# ESTRATEGIA 3: CREAR PREDICTOR OPTIMIZADO (5 min)
# ==============================================================================

class OptimizedStressPredictor:
    """
    Predictor con threshold optimizado y lógica mejorada
    """
    
    def __init__(self, model_path, stress_threshold=0.5):
        self.detector = StressDetector()
        self.detector.load_model(model_path)
        self.stress_threshold = stress_threshold
        
        print(f"✅ Predictor optimizado cargado")
        print(f"   Threshold para Stress: {stress_threshold:.2f}")
    
    def predict_stress(self, image_path):
        """
        Predice con threshold optimizado
        """
        import cv2
        
        # Cargar imagen
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, self.detector.img_size)
        img_array = np.expand_dims(img_resized, axis=0) / 255.0
        
        # Predicción
        predictions = self.detector.model.predict(img_array, verbose=0)[0]
        
        # Aplicar threshold optimizado para Stress
        stress_prob = predictions[1]
        
        if stress_prob >= self.stress_threshold:
            predicted_class = 1  # Stress
        else:
            # Elegir entre Non-Stress y Neutral
            predicted_class = 0 if predictions[0] > predictions[2] else 2
        
        confidence = predictions[predicted_class]
        
        class_labels = {0: 'Non-Stress', 1: 'Stress', 2: 'Neutral'}
        
        result = {
            'predicted_class': int(predicted_class),
            'label': class_labels[predicted_class],
            'confidence': float(confidence),
            'stress_probability': float(stress_prob),
            'probabilities': {
                'Non-Stress': float(predictions[0]),
                'Stress': float(predictions[1]),
                'Neutral': float(predictions[2])
            }
        }
        
        return result


# ==============================================================================
# FUNCIÓN PRINCIPAL - PLAN DE 1 HORA
# ==============================================================================

def one_hour_improvement_plan():
    """
    Plan completo de mejora en 1 hora
    """
    print("="*60)
    print("⏱️  PLAN DE MEJORA DE 1 HORA")
    print("   Accuracy actual: 87%")
    print("   Problema: Confusión con clase Stress")
    print("="*60)
    
    print("\n📋 OPCIÓN 1: Optimización de Threshold (15 min)")
    print("   ✓ Rápido y efectivo")
    print("   ✓ Sin reentrenamiento")
    print("   ✓ Mejora esperada: +2-4%")
    print("   Uso: Para producción inmediata")
    
    print("\n📋 OPCIÓN 2: Fine-tuning Rápido (40 min)")
    print("   ✓ Mejora más sustancial")
    print("   ✓ Requiere reentrenamiento")
    print("   ✓ Mejora esperada: +3-7%")
    print("   Uso: Si puedes esperar un poco más")
    
    print("\n📋 OPCIÓN 3: Ambas (55 min)")
    print("   ✓ Mejor resultado posible")
    print("   ✓ Threshold + Fine-tuning")
    print("   ✓ Mejora esperada: +5-10%")
    print("   Uso: Si quieres máxima mejora")
    
    choice = input("\n➡️  ¿Qué opción prefieres? (1/2/3): ").strip()
    
    if choice == '1':
        # Solo threshold
        print("\n⏱️  Tiempo estimado: 15 minutos")
        best_threshold, results = optimize_threshold()
        
        # Crear predictor optimizado
        predictor = OptimizedStressPredictor(
            'models/stress_model_final.h5',
            stress_threshold=best_threshold
        )
        
        print("\n✅ Listo! Usa el predictor optimizado:")
        print("   from quick_fix import OptimizedStressPredictor")
        print(f"   predictor = OptimizedStressPredictor('models/stress_model_final.h5', {best_threshold:.2f})")
        
        return predictor
        
    elif choice == '2':
        # Solo fine-tuning
        print("\n⏱️  Tiempo estimado: 40 minutos")
        detector = quick_fine_tune(epochs=10)
        return detector
        
    elif choice == '3':
        # Ambas estrategias
        print("\n⏱️  Tiempo estimado: 55 minutos")
        print("\n🎯 PASO 1/2: Optimizando threshold...")
        best_threshold, _ = optimize_threshold()
        
        print("\n🎯 PASO 2/2: Fine-tuning rápido...")
        detector = quick_fine_tune(epochs=10)
        
        # Crear predictor con ambas optimizaciones
        predictor = OptimizedStressPredictor(
            'models/stress_model_quick_fixed.h5',
            stress_threshold=best_threshold
        )
        
        print("\n✅ ¡Mejora completa aplicada!")
        return predictor
    
    else:
        print("❌ Opción inválida")
        return None


# ==============================================================================
# TESTING RÁPIDO
# ==============================================================================

def quick_test(predictor, test_images_dir='data2/test'):
    """
    Prueba rápida con imágenes de test
    """
    import glob
    
    print("\n🧪 PRUEBA RÁPIDA")
    print("-" * 60)
    
    # Buscar algunas imágenes de test
    test_images = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        test_images.extend(glob.glob(os.path.join(test_images_dir, '**', ext), recursive=True))
    
    if len(test_images) == 0:
        print("⚠️  No se encontraron imágenes de prueba")
        return
    
    # Probar con 5 imágenes aleatorias
    import random
    sample_images = random.sample(test_images, min(5, len(test_images)))
    
    for img_path in sample_images:
        result = predictor.predict_stress(img_path)
        print(f"\n📸 {os.path.basename(img_path)}")
        print(f"   Predicción: {result['label']}")
        print(f"   Confianza: {result['confidence']:.2%}")
        print(f"   Prob Stress: {result['stress_probability']:.2%}")


if __name__ == "__main__":
    # Ejecutar plan de 1 hora
    predictor = one_hour_improvement_plan()
    
    # Probar si hay un predictor
    if predictor is not None:
        print("\n💡 ¿Quieres probar el modelo mejorado? (s/n)")
        test = input("➡️  ").strip().lower()
        if test == 's':
            quick_test(predictor)