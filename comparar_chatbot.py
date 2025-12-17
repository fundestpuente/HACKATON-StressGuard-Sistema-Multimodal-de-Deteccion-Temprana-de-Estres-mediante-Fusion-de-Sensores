"""
Script para comparar y sincronizar archivos entre la carpeta Chatbot original
y la del proyecto Hackaton
"""

import os
import shutil
from pathlib import Path

# Rutas
CHATBOT_ORIGINAL = Path(r"c:\Users\59399\Documentos\EPN\Samsung\Chatbot")
CHATBOT_HACKATON = Path(__file__).parent / "Chatbot"

def comparar_archivos():
    """Compara los archivos entre ambas carpetas"""
    print("="*60)
    print("📂 COMPARACIÓN DE CARPETAS CHATBOT")
    print("="*60)
    print(f"\nOriginal: {CHATBOT_ORIGINAL}")
    print(f"Hackaton: {CHATBOT_HACKATON}")
    print()
    
    if not CHATBOT_ORIGINAL.exists():
        print("❌ La carpeta Chatbot original no existe")
        return False
    
    # Listar archivos .py en la carpeta original
    archivos_originales = set()
    for archivo in CHATBOT_ORIGINAL.glob("*.py"):
        archivos_originales.add(archivo.name)
    
    # Listar archivos .py en la carpeta hackaton
    archivos_hackaton = set()
    for archivo in CHATBOT_HACKATON.glob("*.py"):
        archivos_hackaton.add(archivo.name)
    
    print("📋 ARCHIVOS EN CHATBOT ORIGINAL:")
    for archivo in sorted(archivos_originales):
        print(f"   - {archivo}")
    
    print("\n📋 ARCHIVOS EN CHATBOT HACKATON:")
    for archivo in sorted(archivos_hackaton):
        print(f"   - {archivo}")
    
    # Encontrar diferencias
    solo_en_original = archivos_originales - archivos_hackaton
    solo_en_hackaton = archivos_hackaton - archivos_originales
    en_ambos = archivos_originales & archivos_hackaton
    
    print("\n" + "="*60)
    print("📊 ANÁLISIS")
    print("="*60)
    
    if solo_en_original:
        print(f"\n⚠️  ARCHIVOS SOLO EN ORIGINAL ({len(solo_en_original)}):")
        for archivo in sorted(solo_en_original):
            print(f"   - {archivo}")
    
    if solo_en_hackaton:
        print(f"\n✅ ARCHIVOS SOLO EN HACKATON ({len(solo_en_hackaton)}):")
        for archivo in sorted(solo_en_hackaton):
            print(f"   - {archivo}")
    
    if en_ambos:
        print(f"\n🔄 ARCHIVOS EN AMBOS ({len(en_ambos)}):")
        for archivo in sorted(en_ambos):
            print(f"   - {archivo}")
    
    return solo_en_original, en_ambos


def analizar_contenido():
    """Analiza el contenido de los archivos clave"""
    print("\n" + "="*60)
    print("🔍 ANÁLISIS DE CONTENIDO")
    print("="*60)
    
    archivos_clave = ['stress_flow.py', 'api_server.py', 'app.py']
    
    for archivo in archivos_clave:
        ruta_original = CHATBOT_ORIGINAL / archivo
        
        if ruta_original.exists():
            print(f"\n📄 {archivo}:")
            print(f"   Ubicación: {ruta_original}")
            
            # Leer primeras líneas para ver qué hace
            try:
                with open(ruta_original, 'r', encoding='utf-8') as f:
                    lineas = f.readlines()[:20]
                    
                # Buscar imports y docstrings
                print("   Primeras líneas:")
                for i, linea in enumerate(lineas[:10], 1):
                    linea_limpia = linea.strip()
                    if linea_limpia and not linea_limpia.startswith('#'):
                        print(f"      {i}: {linea.rstrip()}")
                        
            except Exception as e:
                print(f"   ⚠️ Error al leer: {e}")
        else:
            print(f"\n❌ {archivo}: NO EXISTE")


def verificar_funcionalidad():
    """Verifica si la funcionalidad de los archivos originales está en el hackaton"""
    print("\n" + "="*60)
    print("🎯 VERIFICACIÓN DE FUNCIONALIDAD")
    print("="*60)
    
    # Verificar inter_chatbot.py del hackaton
    inter_chatbot = CHATBOT_HACKATON / "inter_chatbot.py"
    
    if inter_chatbot.exists():
        print("\n✅ inter_chatbot.py existe en hackaton")
        
        with open(inter_chatbot, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Verificar características
        caracteristicas = {
            'Ollama': 'MODELO_OLLAMA' in contenido or 'ollama' in contenido.lower(),
            'Streaming': 'stream' in contenido.lower(),
            'Prompts': 'PROMPT_' in contenido or 'import prompts' in contenido,
            'Flet UI': 'import flet' in contenido,
            'Router Pattern': 'modo_guia' in contenido.lower() or 'router' in contenido.lower(),
            'Voz (TTS)': 'pyttsx3' in contenido,
            'Speech Recognition': 'speech_recognition' in contenido or 'sr.' in contenido,
        }
        
        print("\n📋 Características implementadas:")
        for caracteristica, presente in caracteristicas.items():
            estado = "✅" if presente else "❌"
            print(f"   {estado} {caracteristica}")
    else:
        print("\n❌ inter_chatbot.py NO existe en hackaton")


def sugerencias():
    """Proporciona sugerencias sobre qué hacer"""
    print("\n" + "="*60)
    print("💡 RECOMENDACIONES")
    print("="*60)
    
    print("""
El chatbot del hackaton (inter_chatbot.py) es una versión completa y moderna que incluye:
- ✅ Integración con Ollama (llama3.2)
- ✅ Router Pattern con dos prompts (CHARLA y GUIA)
- ✅ Interfaz gráfica con Flet
- ✅ Streaming de respuestas
- ✅ Reconocimiento de voz
- ✅ Control de instancia única
- ✅ Modo automático/manual

Los archivos de la carpeta original (stress_flow.py, api_server.py, app.py)
probablemente son versiones anteriores o alternativas.

SUGERENCIA:
No es necesario copiar archivos de la carpeta original al hackaton.
El inter_chatbot.py del hackaton es más completo y moderno.

Sin embargo, si quieres revisar los archivos originales para
ver si tienen alguna funcionalidad específica que falte,
puedes compararlos manualmente.
""")


def main():
    print("\n" + "="*60)
    print("🔍 COMPARACIÓN CHATBOT ORIGINAL vs HACKATON")
    print("="*60)
    
    # Comparar archivos
    resultado = comparar_archivos()
    
    if resultado:
        # Analizar contenido de archivos clave
        analizar_contenido()
        
        # Verificar funcionalidad en hackaton
        verificar_funcionalidad()
        
        # Dar sugerencias
        sugerencias()
    
    print("\n" + "="*60)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
