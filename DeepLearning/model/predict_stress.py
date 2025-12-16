"""
Script para hacer predicciones con el modelo entrenado
"""

from model.stress_detector_model import StressDetector
import cv2
import matplotlib.pyplot as plt
import numpy as np

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
    print(f"Predicción: {result['label']}")
    print(f"Estrés detectado: {'SÍ' if result['stress_detected'] else 'NO'}")
    print(f"Confianza: {result['confidence']:.2%}")
    print(f"Score crudo: {result['raw_score']:.4f}")
    print("="*50)
    
    # Mostrar imagen con resultado
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(10, 6))
    plt.imshow(img)
    plt.axis('off')
    
    color = 'red' if result['stress_detected'] else 'green'
    plt.title(f"{result['label']} (Confianza: {result['confidence']:.2%})",
             fontsize=16, color=color, fontweight='bold')
    plt.tight_layout()
    plt.savefig('prediction_result.png', dpi=300, bbox_inches='tight')
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
        print(f"  - Predicción: {result['label']}")
        print(f"  - Estrés detectado: {'SÍ' if result['stress_detected'] else 'NO'}")
        print(f"  - Confianza: {result['confidence']:.2%}")
        print(f"  - Ubicación: {result['bbox']}")
    
    print("="*50)
    
    # Mostrar imagen anotada
    annotated_rgb = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
    
    plt.figure(figsize=(12, 8))
    plt.imshow(annotated_rgb)
    plt.axis('off')
    plt.title(f"Rostros detectados: {len(results)}", fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('face_detection_result.png', dpi=300, bbox_inches='tight')
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
            
            status = "✅" if not result['stress_detected'] else "⚠️"
            print(f"{status} {img_path.name}: {result['label']} ({result['confidence']:.2%})")
            
        except Exception as e:
            print(f" Error con {img_path.name}: {e}")
    
    # Resumen
    print("\n" + "="*50)
    print("RESUMEN DE PREDICCIONES")
    print("="*50)
    
    total = len(results)
    stress_count = sum(1 for r in results if r['stress_detected'])
    non_stress_count = total - stress_count
    
    print(f"Total de imágenes: {total}")
    print(f"Con estrés: {stress_count} ({stress_count/total*100:.1f}%)")
    print(f"Sin estrés: {non_stress_count} ({non_stress_count/total*100:.1f}%)")
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
    
    model_path = 'stress_model_final.h5'
    
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