"""
Script para analizar en profundidad los archivos del Chatbot original
y copiar lo necesario al proyecto Hackaton
"""

import os
import shutil
from pathlib import Path

CHATBOT_ORIGINAL = Path(r"c:\Users\59399\Documentos\EPN\Samsung\Chatbot")
CHATBOT_HACKATON = Path(__file__).parent / "Chatbot"

def leer_archivo_completo(archivo):
    """Lee y muestra el contenido completo de un archivo"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error al leer: {e}"

def analizar_stress_flow():
    """Analiza stress_flow.py para ver qué hace"""
    print("="*60)
    print("📄 ANALIZANDO stress_flow.py")
    print("="*60)
    
    archivo = CHATBOT_ORIGINAL / "stress_flow.py"
    if not archivo.exists():
        print("❌ Archivo no existe")
        return
    
    contenido = leer_archivo_completo(archivo)
    
    # Buscar funciones principales
    import re
    funciones = re.findall(r'^def\s+(\w+)\s*\(', contenido, re.MULTILINE)
    
    print(f"\n📋 Funciones encontradas ({len(funciones)}):")
    for func in funciones:
        print(f"   - {func}()")
    
    # Buscar imports importantes
    lineas = contenido.split('\n')
    imports = [l.strip() for l in lineas if l.strip().startswith('import') or l.strip().startswith('from')]
    
    print(f"\n📦 Imports ({len(imports)}):")
    for imp in imports[:10]:  # Primeros 10
        print(f"   {imp}")
    
    # Verificar si hay manejo especial de Ollama
    if 'ollama' in contenido.lower():
        print("\n✅ Contiene código relacionado con Ollama")
    
    if 'system' in contenido or 'prompt' in contenido:
        print("✅ Contiene manejo de prompts/system")
    
    return contenido

def analizar_app():
    """Analiza app.py para ver cómo se usa stress_flow"""
    print("\n" + "="*60)
    print("📄 ANALIZANDO app.py")
    print("="*60)
    
    archivo = CHATBOT_ORIGINAL / "app.py"
    if not archivo.exists():
        print("❌ Archivo no existe")
        return
    
    contenido = leer_archivo_completo(archivo)
    
    # Mostrar las primeras 50 líneas
    lineas = contenido.split('\n')
    print(f"\n📝 Primeras 50 líneas:")
    for i, linea in enumerate(lineas[:50], 1):
        if linea.strip():
            print(f"{i:3}: {linea}")
    
    return contenido

def buscar_diferencias_clave():
    """Busca diferencias clave en cómo se maneja Ollama"""
    print("\n" + "="*60)
    print("🔍 BUSCANDO DIFERENCIAS CLAVE")
    print("="*60)
    
    # Leer app.py
    app_file = CHATBOT_ORIGINAL / "app.py"
    if app_file.exists():
        with open(app_file, 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # Buscar cómo se llama a Ollama
        import re
        
        # Buscar llamadas a ollama
        ollama_calls = re.findall(r'ollama\.\w+\([^)]+\)', app_content, re.MULTILINE)
        
        if ollama_calls:
            print("\n📞 Llamadas a Ollama encontradas:")
            for call in ollama_calls[:5]:
                print(f"   {call}")
        
        # Buscar si usa 'chat' en lugar de 'generate'
        if 'ollama.chat' in app_content:
            print("\n⚠️  IMPORTANTE: El original usa ollama.chat()")
            print("   El hackaton usa requests a /api/generate")
            print("   Esta puede ser la diferencia clave!")
        
        if 'ollama.generate' in app_content:
            print("\n✅ El original usa ollama.generate()")

def copiar_archivos_necesarios():
    """Pregunta si se deben copiar archivos"""
    print("\n" + "="*60)
    print("📋 ARCHIVOS QUE PODRÍAN COPIARSE")
    print("="*60)
    
    archivos_utiles = {
        'stress_flow.py': 'Manejo del flujo de conversación',
    }
    
    for archivo, desc in archivos_utiles.items():
        origen = CHATBOT_ORIGINAL / archivo
        destino = CHATBOT_HACKATON / archivo
        
        if origen.exists():
            if destino.exists():
                print(f"⚠️  {archivo}: Ya existe en hackaton")
            else:
                print(f"💾 {archivo}: Podría copiarse ({desc})")
                print(f"   Origen: {origen}")
                print(f"   Destino: {destino}")
        else:
            print(f"❌ {archivo}: No existe en original")

def main():
    print("\n" + "="*70)
    print("🔬 ANÁLISIS PROFUNDO: CHATBOT ORIGINAL vs HACKATON")
    print("="*70)
    
    # Analizar archivos
    stress_flow_content = analizar_stress_flow()
    app_content = analizar_app()
    
    # Buscar diferencias clave
    buscar_diferencias_clave()
    
    # Sugerir archivos a copiar
    copiar_archivos_necesarios()
    
    print("\n" + "="*70)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*70)

if __name__ == "__main__":
    main()
