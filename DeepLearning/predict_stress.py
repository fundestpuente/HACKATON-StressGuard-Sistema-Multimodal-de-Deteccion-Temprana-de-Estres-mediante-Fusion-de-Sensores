"""
Script para hacer predicciones con el modelo entrenado
"""

from stress_detector_model import StressDetector
import cv2
import matplotlib.pyplot as plt
import numpy as np
from quick_fix import OptimizedStressPredictor

def predict_single_image(model_path, image_path):
    """
    Predice el estrés en una sola imagen
    """
    # Cargar modelo
    detector = StressDetector()
    detector.load_model(model_path)
    
    # Hacer predicción
    result = detector.predict_stress(image_path)
    
    print("\n" + "="*50)
    print("RESULTADO DE LA PREDICCIÓN")
    print("="*50)
    print(f"Imagen: {image_path}")
    print(f"Clase predicha: {result['class']}")
    print(f"Confianza: {result['confidence']:.2%}")
    print(f"\nProbabilidades por clase:")
    print(f"  Non-Stress: {result['probabilities']['Non-Stress']:.2%}")
    print(f"  Stress:     {result['probabilities']['Stress']:.2%}")
    print(f"  Neutral:    {result['probabilities']['Neutral']:.2%}")
    print("="*50)
    
    # Mostrar imagen con resultado
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(10, 6))
    plt.imshow(img)
    plt.axis('off')
    
    # Color según clase
    if result['class'] == 'Non-Stress':
        color = 'green'
    elif result['class'] == 'Stress':
        color = 'red'
    else:
        color = 'orange'
    
    plt.title(f"{result['class']} (Confianza: {result['confidence']:.2%})",
             fontsize=16, color=color, fontweight='bold')
    plt.tight_layout()
    plt.savefig('resultados/prediction_result.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return result


def predict_with_faces(model_path, image_path):
    """
    Detecta rostros y predice estrés en cada uno
    """
    # Cargar modelo
    detector = StressDetector()
    detector.load_model(model_path)
    
    # Hacer predicción con detección de rostros
    results, annotated_img = detector.predict_with_face_detection(image_path)
    
    print("\n" + "="*50)
    print("DETECCIÓN DE ROSTROS Y ESTRÉS")
    print("="*50)
    print(f"Imagen: {image_path}")
    print(f"Rostros detectados: {len(results)}")
    
    for i, result in enumerate(results, 1):
        print(f"\nRostro {i}:")
        print(f"  - Clase: {result['class']}")
        print(f"  - Confianza: {result['confidence']:.2%}")
        print(f"  - Probabilidades:")
        print(f"    · Non-Stress: {result['probabilities']['Non-Stress']:.2%}")
        print(f"    · Stress:     {result['probabilities']['Stress']:.2%}")
        print(f"    · Neutral:    {result['probabilities']['Neutral']:.2%}")
        print(f"  - Ubicación: {result['bbox']}")
    
    print("="*50)
    
    # Mostrar imagen anotada
    annotated_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(12, 8))
    plt.imshow(annotated_rgb)
    plt.axis('off')
    plt.title(f"Rostros detectados: {len(results)}", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('resultados/face_detection_result.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return results, annotated_img


def batch_predict(model_path, image_folder):
    """
    Hace predicciones en múltiples imágenes
    """
    import os
    from pathlib import Path
    
    # Cargar modelo
    detector = StressDetector()
    detector.load_model(model_path)
    
    # Obtener todas las imágenes
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(Path(image_folder).glob(f'*{ext}'))
        image_files.extend(Path(image_folder).glob(f'*{ext.upper()}'))
    
    print(f"\n Encontradas {len(image_files)} imágenes en {image_folder}")
    
    results = []
    
    for img_path in image_files:
        try:
            result = detector.predict_stress(str(img_path))
            result['filename'] = img_path.name
            results.append(result)
            
            # Emoji según clase
            if result['class'] == 'Non-Stress':
                status = "✅"
            elif result['class'] == 'Stress':
                status = "⚠️"
            else:
                status = "🔶"
            
            print(f"{status} {img_path.name}: {result['class']} ({result['confidence']:.2%})")
            
        except Exception as e:
            print(f" Error con {img_path.name}: {e}")
    
    # Resumen
    print("\n" + "="*50)
    print("RESUMEN DE PREDICCIONES")
    print("="*50)
    
    total = len(results)
    non_stress_count = sum(1 for r in results if r['class'] == 'Non-Stress')
    stress_count = sum(1 for r in results if r['class'] == 'Stress')
    neutral_count = sum(1 for r in results if r['class'] == 'Neutral')
    
    print(f"Total de imágenes: {total}")
    print(f"Non-Stress: {non_stress_count} ({non_stress_count/total*100:.1f}%)")
    print(f"Stress: {stress_count} ({stress_count/total*100:.1f}%)")
    print(f"Neutral: {neutral_count} ({neutral_count/total*100:.1f}%)")
    print(f"Confianza promedio: {np.mean([r['confidence'] for r in results]):.2%}")
    
    return results


# Ejemplo de uso
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python predict_stress.py <ruta_a_imagen>")
        print("  python predict_stress.py --faces <ruta_a_imagen>")
        print("  python predict_stress.py --batch <carpeta_con_imagenes>")
        sys.exit(1)
    
    model_path = 'models/stress_model_final.h5'
    
    if sys.argv[1] == '--faces':
        # Predicción con detección de rostros
        if len(sys.argv) < 3:
            print("Error: Especifica la ruta de la imagen")
            sys.exit(1)
        predict_with_faces(model_path, sys.argv[2])
        
    elif sys.argv[1] == '--batch':
        # Predicción en lote
        if len(sys.argv) < 3:
            print("Error: Especifica la carpeta con imágenes")
            sys.exit(1)
        batch_predict(model_path, sys.argv[2])
        
    else:
        # Predicción simple
        predict_single_image(model_path, sys.argv[1])
    