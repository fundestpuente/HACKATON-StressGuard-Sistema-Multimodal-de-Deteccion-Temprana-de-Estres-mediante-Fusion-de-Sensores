"""
Script de verificación del sistema StressGuard
Verifica que todos los componentes necesarios estén instalados y funcionando
"""

import sys

def verificar_dependencias():
    """Verifica que todas las dependencias de Python estén instaladas"""
    print("="*60)
    print("📦 VERIFICANDO DEPENDENCIAS DE PYTHON")
    print("="*60)
    
    dependencias = {
        'flet': 'Interfaz gráfica',
        'sklearn': 'Machine Learning (scikit-learn)',
        'xgboost': 'Modelo XGBoost',
        'psutil': 'Gestión de procesos',
        'pyttsx3': 'Texto a voz',
        'speech_recognition': 'Reconocimiento de voz',
        'requests': 'Cliente HTTP'
    }
    
    faltantes = []
    
    for modulo, descripcion in dependencias.items():
        try:
            __import__(modulo)
            print(f"✅ {modulo:20} - {descripcion}")
        except ImportError:
            print(f"❌ {modulo:20} - {descripcion} (NO INSTALADO)")
            faltantes.append(modulo)
    
    print()
    if faltantes:
        print(f"⚠️  Faltan {len(faltantes)} dependencias")
        print(f"Ejecuta: pip install {' '.join(faltantes)}")
        return False
    else:
        print("✅ Todas las dependencias están instaladas")
        return True


def verificar_ollama():
    """Verifica que Ollama esté funcionando y tenga el modelo descargado"""
    print("\n" + "="*60)
    print("🤖 VERIFICANDO OLLAMA")
    print("="*60)
    
    import requests
    
    try:
        # Verificar que el servidor Ollama responde
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        
        if response.status_code == 200:
            print("✅ Servidor Ollama está ejecutándose")
            
            # Verificar modelos instalados
            modelos = response.json().get('models', [])
            nombres_modelos = [m['name'] for m in modelos]
            
            print(f"\n📚 Modelos instalados ({len(nombres_modelos)}):")
            for nombre in nombres_modelos:
                print(f"   - {nombre}")
            
            # Verificar si llama3.2 está instalado (cualquier versión)
            if any('llama3.2' in nombre for nombre in nombres_modelos):
                modelo_encontrado = [n for n in nombres_modelos if 'llama3.2' in n][0]
                print(f"\n✅ Modelo llama3.2 está disponible: {modelo_encontrado}")
                print(f"💡 Usar en el código: MODELO_OLLAMA = \"{modelo_encontrado}\"")
                return True
            else:
                print("\n⚠️  Modelo llama3.2 NO está instalado")
                print("Ejecuta: ollama pull llama3.2")
                return False
        else:
            print(f"⚠️  Servidor Ollama respondió con código {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar con Ollama")
        print("\nSOLUCIONES:")
        print("1. Verifica que Ollama esté instalado")
        print("2. Inicia el servidor: ollama serve")
        print("3. Descarga el modelo: ollama pull llama3.2")
        return False
    except Exception as e:
        print(f"❌ Error al verificar Ollama: {e}")
        return False


def verificar_archivos():
    """Verifica que todos los archivos necesarios existan"""
    print("\n" + "="*60)
    print("📁 VERIFICANDO ARCHIVOS DEL PROYECTO")
    print("="*60)
    
    from pathlib import Path
    
    base_dir = Path(__file__).parent
    
    archivos_requeridos = {
        'launcher.py': 'Launcher principal',
        'Chatbot/inter_chatbot.py': 'Chatbot con Ollama',
        'Chatbot/prompts.py': 'Prompts del sistema',
        'MachineLearning/simu_reloj.py': 'Simulador de reloj',
        'MachineLearning/receptor_datos.py': 'Receptor de datos',
        'MachineLearning/chatbot_manager.py': 'Gestor de chatbot',
        'MachineLearning/stress_model.py': 'Modelo de ML',
    }
    
    faltantes = []
    
    for archivo, descripcion in archivos_requeridos.items():
        ruta = base_dir / archivo
        if ruta.exists():
            print(f"✅ {archivo:35} - {descripcion}")
        else:
            print(f"❌ {archivo:35} - {descripcion} (NO ENCONTRADO)")
            faltantes.append(archivo)
    
    print()
    if faltantes:
        print(f"⚠️  Faltan {len(faltantes)} archivos")
        return False
    else:
        print("✅ Todos los archivos necesarios están presentes")
        return True


def verificar_modelo_ml():
    """Verifica que el modelo de Machine Learning exista"""
    print("\n" + "="*60)
    print("🧠 VERIFICANDO MODELO DE MACHINE LEARNING")
    print("="*60)
    
    from pathlib import Path
    
    base_dir = Path(__file__).parent
    modelo_path = base_dir / 'MachineLearning' / 'best_wesad_xgboost_no_smote_model.pkl'
    
    if modelo_path.exists():
        print(f"✅ Modelo encontrado: {modelo_path.name}")
        
        # Intentar cargar el modelo
        try:
            import joblib
            pipeline = joblib.load(modelo_path)
            print("✅ Modelo se carga correctamente")
            return True
        except Exception as e:
            print(f"⚠️  Error al cargar modelo: {e}")
            return False
    else:
        print("⚠️  Modelo NO encontrado")
        print(f"Se esperaba en: {modelo_path}")
        print("\nEl simulador funcionará pero no podrá predecir estrés.")
        return False


def main():
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DEL SISTEMA STRESSGUARD")
    print("="*60)
    print()
    
    resultados = []
    
    # Verificar dependencias
    resultados.append(("Dependencias Python", verificar_dependencias()))
    
    # Verificar archivos
    resultados.append(("Archivos del proyecto", verificar_archivos()))
    
    # Verificar Ollama
    resultados.append(("Servidor Ollama", verificar_ollama()))
    
    # Verificar modelo ML
    resultados.append(("Modelo ML", verificar_modelo_ml()))
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60)
    
    for nombre, resultado in resultados:
        estado = "✅ OK" if resultado else "❌ FALTA"
        print(f"{estado:10} - {nombre}")
    
    print()
    
    todos_ok = all(r[1] for r in resultados)
    
    if todos_ok:
        print("="*60)
        print("🎉 ¡TODO ESTÁ LISTO!")
        print("="*60)
        print("\nPuedes ejecutar el sistema con:")
        print("  python launcher.py")
        print("\nO con el archivo batch:")
        print("  INICIAR_STRESSGUARD.bat")
    else:
        print("="*60)
        print("⚠️  HAY PROBLEMAS QUE RESOLVER")
        print("="*60)
        print("\nRevisa los mensajes anteriores para ver qué falta.")
    
    print()


if __name__ == "__main__":
    main()
