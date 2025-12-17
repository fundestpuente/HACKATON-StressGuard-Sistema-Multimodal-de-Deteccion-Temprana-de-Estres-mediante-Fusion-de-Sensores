"""
Script de prueba para verificar si el chatbot se puede abrir
"""
import sys

print("="*60)
print("🧪 PROBANDO CHATBOT")
print("="*60)

# Paso 1: Imports
print("\n1. Probando imports...")
try:
    import flet as ft
    print("   ✅ flet")
except Exception as e:
    print(f"   ❌ flet: {e}")
    sys.exit(1)

try:
    import ollama
    print("   ✅ ollama")
except Exception as e:
    print(f"   ⚠️  ollama: {e} (continuando...)")

try:
    import pyttsx3
    print("   ✅ pyttsx3")
except Exception as e:
    print(f"   ⚠️  pyttsx3: {e} (continuando...)")

# Paso 2: Importar inter_chatbot
print("\n2. Importando inter_chatbot.py...")
try:
    import inter_chatbot
    print("   ✅ inter_chatbot importado correctamente")
except Exception as e:
    print(f"   ❌ Error al importar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Paso 3: Verificar función main
print("\n3. Verificando función main...")
if hasattr(inter_chatbot, 'main'):
    print("   ✅ Función main existe")
else:
    print("   ❌ Función main NO existe")
    sys.exit(1)

# Paso 4: Intentar ejecutar
print("\n4. Ejecutando chatbot...")
print("   Forzando modo ventana (view=ft.AppView.FLET_APP)")
print("   (Si no se abre, presiona Ctrl+C)")
print()

try:
    ft.app(target=inter_chatbot.main, view=ft.AppView.FLET_APP)
except Exception as e:
    print(f"\n❌ Error al ejecutar: {e}")
    import traceback
    traceback.print_exc()
