"""
Script de diagnóstico completo del dataset de Roboflow
Detecta problemas y ofrece soluciones
"""

import pandas as pd
import os
import sys

def check_roboflow_export(data_root='data2'):
    """
    Verifica el export de Roboflow y detecta problemas
    """
    print("="*70)
    print("🔍 DIAGNÓSTICO COMPLETO DEL DATASET DE ROBOFLOW")
    print("="*70)
    
    all_data = {}
    
    for subset in ['train', 'valid', 'test']:
        csv_path = os.path.join(data_root, subset, '_classes.csv')
        
        if not os.path.exists(csv_path):
            print(f"\n❌ No existe: {csv_path}")
            continue
        
        df = pd.read_csv(csv_path)
        all_data[subset] = df
        
        print(f"\n{'='*70}")
        print(f"📊 {subset.upper()}")
        print(f"{'='*70}")
        print(f"Total de imágenes: {len(df)}")
        print(f"Columnas: {list(df.columns)}")
        
        # Ver valores únicos
        print(f"\nValores únicos en 'Non': {df['Non'].unique()}")
        print(f"Valores únicos en 'Stress': {df['Stress'].unique()}")
        
        # Contar combinaciones
        print(f"\n📈 Distribución de combinaciones:")
        combos = df.groupby(['Non', 'Stress']).size().reset_index(name='count')
        for _, row in combos.iterrows():
            pct = row['count'] / len(df) * 100
            print(f"   Non={row['Non']}, Stress={row['Stress']}: {row['count']:4d} ({pct:5.1f}%)")
        
        # Primeras 10 filas
        print(f"\n📝 Primeras 10 filas:")
        print(df[['filename', 'Non', 'Stress']].head(10).to_string(index=False))
    
    # Análisis global
    print(f"\n{'='*70}")
    print("🔬 ANÁLISIS GLOBAL")
    print(f"{'='*70}")
    
    if not all_data:
        print("❌ No se pudo leer ningún CSV")
        return False
    
    # Combinar todos los datos
    all_df = pd.concat(all_data.values())
    
    total = len(all_df)
    stress_only = len(all_df[(all_df['Non'] == 0) & (all_df['Stress'] == 1)])
    non_stress_only = len(all_df[(all_df['Non'] == 1) & (all_df['Stress'] == 0)])
    both = len(all_df[(all_df['Non'] == 1) & (all_df['Stress'] == 1)])
    neither = len(all_df[(all_df['Non'] == 0) & (all_df['Stress'] == 0)])
    
    print(f"\nTotal de imágenes: {total}")
    print(f"\n📊 Distribución global:")
    print(f"   Solo Stress (Non=0, Stress=1):     {stress_only:4d} ({stress_only/total*100:5.1f}%)")
    print(f"   Solo Non-Stress (Non=1, Stress=0): {non_stress_only:4d} ({non_stress_only/total*100:5.1f}%)")
    print(f"   Ambos (Non=1, Stress=1):           {both:4d} ({both/total*100:5.1f}%) ⚠️")
    print(f"   Ninguno (Non=0, Stress=0):         {neither:4d} ({neither/total*100:5.1f}%) ⚠️")
    
    # Diagnóstico
    print(f"\n{'='*70}")
    print("🩺 DIAGNÓSTICO")
    print(f"{'='*70}")
    
    issues = []
    
    # Problema 1: Solo una clase
    if non_stress_only == 0 and stress_only > 0:
        print("\n❌ PROBLEMA CRÍTICO #1: Solo hay clase 'Stress'")
        print("   No hay ejemplos de 'Non-Stress'")
        issues.append("missing_class")
        
        print("\n💡 POSIBLES CAUSAS:")
        print("   1. El dataset de Roboflow solo tiene imágenes con estrés")
        print("   2. El export está mal configurado")
        print("   3. Las clases se llaman diferente en Roboflow")
        
        print("\n✅ SOLUCIONES:")
        print("   A. En Roboflow:")
        print("      - Verifica que tu proyecto tenga 2 clases")
        print("      - Re-exporta el dataset en formato 'Classification'")
        print("      - Asegúrate de incluir ambas clases en el export")
        print("\n   B. Conseguir un dataset diferente:")
        print("      - Busca un dataset balanceado con ambas clases")
        print("      - Ejemplos: datasets de detección de estrés en Kaggle")
        print("\n   C. Cambiar el objetivo del proyecto:")
        print("      - Usar detección de emociones (7 clases) en lugar de estrés")
        print("      - Dataset FER2013 tiene 7 emociones balanceadas")
    
    # Problema 2: Casos ambiguos
    if both > 0:
        print(f"\n⚠️ PROBLEMA #2: {both} casos ambiguos (Non=1, Stress=1)")
        print("   Una imagen no puede ser ambas clases simultáneamente")
        issues.append("ambiguous")
        
        print("\n💡 POSIBLE CAUSA:")
        print("   - Error en el etiquetado de Roboflow")
        print("   - Formato one-hot encoding incorrecto")
        
        print("\n✅ SOLUCIÓN:")
        print("   Crear script de limpieza para corregir estos casos")
    
    # Problema 3: Sin clasificar
    if neither > 0:
        print(f"\n⚠️ PROBLEMA #3: {neither} casos sin clasificar (Non=0, Stress=0)")
        issues.append("unclassified")
        
        print("\n✅ SOLUCIÓN:")
        print("   Eliminar o re-etiquetar estos casos")
    
    # Si está OK
    if not issues:
        print("\n✅ Dataset correcto y balanceado")
        print(f"   Ratio Stress:Non-Stress = {stress_only/max(non_stress_only,1):.2f}:1")
        return True
    
    # Mostrar ejemplo del CSV para debugging
    print(f"\n{'='*70}")
    print("🔍 MUESTRA DEL CSV (para debugging)")
    print(f"{'='*70}")
    print("\nPrimeras 20 filas del train set:")
    if 'train' in all_data:
        print(all_data['train'][['filename', 'Non', 'Stress']].head(20).to_string(index=False))
    
    return False

def suggest_next_steps(success):
    """
    Sugiere los siguientes pasos según el resultado
    """
    print(f"\n{'='*70}")
    print("📋 PRÓXIMOS PASOS")
    print(f"{'='*70}")
    
    if success:
        print("\n✅ Tu dataset está listo para entrenar!")
        print("\n🚀 Ejecuta:")
        print("   python train_stress_model.py")
    else:
        print("\n❌ Tu dataset tiene problemas que deben corregirse primero")
        print("\n🔍 VERIFICA EN ROBOFLOW:")
        print("   1. Abre tu proyecto en Roboflow")
        print("   2. Ve a la sección 'Classes' o 'Labels'")
        print("   3. Verifica que tienes 2 clases:")
        print("      - 'Stress' (o similar)")
        print("      - 'Non-Stress' / 'No-Stress' / 'Normal' (o similar)")
        print("   4. Verifica que ambas clases tienen imágenes asignadas")
        print("\n📤 RE-EXPORTA EL DATASET:")
        print("   1. En Roboflow, ve a 'Export'")
        print("   2. Selecciona formato 'Classification' (CSV)")
        print("   3. Descarga y reemplaza tu carpeta 'data2'")
        print("\n💬 O COMPARTE:")
        print("   - Cuéntame cuántas clases tiene tu proyecto en Roboflow")
        print("   - Muéstrame los nombres de las clases")
        print("   - Y te ayudo a adaptar el código")

if __name__ == "__main__":
    data_root = sys.argv[1] if len(sys.argv) > 1 else 'data2'
    
    print(f"\n📂 Analizando dataset en: {os.path.abspath(data_root)}\n")
    
    success = check_roboflow_export(data_root)
    suggest_next_steps(success)
    
    sys.exit(0 if success else 1)