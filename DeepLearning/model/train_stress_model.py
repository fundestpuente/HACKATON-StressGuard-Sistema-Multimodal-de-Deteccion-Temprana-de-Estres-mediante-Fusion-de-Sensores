"""
Script principal para entrenar el modelo de detección de estrés
"""

from stress_detector_model import StressDetector, load_all_datasets
import numpy as np

def main():
    print("="*60)
    print(" ENTRENAMIENTO DE MODELO DE DETECCIÓN DE ESTRÉS")
    print("="*60)
    
    # 1. Cargar datasets
    print("\n PASO 1: Cargando datasets...")
    (X_train, y_train), (X_val, y_val), (X_test, y_test) = load_all_datasets('../data2')
    
    # 2. Crear detector
    print("\n  PASO 2: Construyendo modelo...")
    detector = StressDetector(img_size=(224, 224))
    
    # Opción 1: Transfer Learning (RECOMENDADO - más rápido y preciso)
    detector.build_model(use_transfer_learning=True)
    
    # Opción 2: CNN desde cero (descomenta si prefieres esto)
    # detector.build_model(use_transfer_learning=False)
    
    # 3. Compilar modelo
    print("\n⚙️  PASO 3: Compilando modelo...")
    detector.compile_model(learning_rate=0.001)
    
    # 4. Entrenar
    print("\n PASO 4: Entrenando modelo...")
    history = detector.train(
        X_train, y_train,
        X_val, y_val,
        epochs=50,
        batch_size=32,
        checkpoint_path='best_stress_model.h5'
    )
    
    # 5. Visualizar historial de entrenamiento
    print("\n PASO 5: Generando gráficas de entrenamiento...")
    detector.plot_training_history(save_path='training_history.png')
    
    # 6. Evaluar en test set
    print("\n PASO 6: Evaluando en conjunto de prueba...")
    y_pred, predictions = detector.evaluate(
        X_test, y_test,
        save_path='confusion_matrix.png'
    )
    
    # 7. Guardar modelo final
    print("\n PASO 7: Guardando modelo...")
    detector.save_model('stress_model_final.h5')
    
    print("\n" + "="*60)
    print(" ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
    print("="*60)
    print("\n Archivos generados:")
    print("   - best_stress_model.h5 (mejor modelo durante entrenamiento)")
    print("   - stress_model_final.h5 (modelo final)")
    print("   - training_history.png (gráficas de entrenamiento)")
    print("   - confusion_matrix.png (matriz de confusión)")
    
    # 8. Resumen de métricas finales
    test_acc = np.mean(y_test == y_pred)
    print(f"\n Accuracy final en test: {test_acc:.4f}")
    
    return detector


if __name__ == "__main__":
    detector = main()