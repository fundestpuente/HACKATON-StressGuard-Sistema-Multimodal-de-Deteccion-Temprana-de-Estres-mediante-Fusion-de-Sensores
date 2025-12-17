"""
Gestor de Chatbot - Control de Instancia Única
Maneja la apertura del chatbot desde señales de estrés o manualmente
Previene la duplicación de instancias
"""

import os
import sys
import subprocess
import psutil
import time
from pathlib import Path

# Ruta del archivo de control de instancia
LOCK_FILE = Path(__file__).parent / ".chatbot_instance.lock"
CHATBOT_SCRIPT = Path(__file__).parent.parent / "Chatbot" / "inter_chatbot.py"


def esta_chatbot_ejecutandose():
    """
    Verifica si el chatbot ya está en ejecución
    Retorna True si encuentra una instancia activa
    """
    if not LOCK_FILE.exists():
        return False
    
    try:
        # Leer el PID del archivo de bloqueo
        with open(LOCK_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Verificar si el proceso existe
        if psutil.pid_exists(pid):
            try:
                proceso = psutil.Process(pid)
                # Verificar que sea realmente Python ejecutando el chatbot
                cmdline = ' '.join(proceso.cmdline())
                if 'inter_chatbot.py' in cmdline or 'python' in cmdline.lower():
                    print(f"✓ Chatbot ya está ejecutándose (PID: {pid})")
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Si llegamos aquí, el PID no es válido - limpiar archivo
        LOCK_FILE.unlink(missing_ok=True)
        return False
        
    except (ValueError, FileNotFoundError):
        # Archivo corrupto, eliminarlo
        LOCK_FILE.unlink(missing_ok=True)
        return False


def abrir_chatbot(modo='manual'):
    """
    Abre el chatbot si no está ya ejecutándose
    
    Args:
        modo (str): 'automatico' si se abre por señal de estrés,
                   'manual' si se abre por el usuario
    
    Returns:
        bool: True si se abrió exitosamente, False si ya estaba abierto
    """
    # Verificar si ya está ejecutándose
    if esta_chatbot_ejecutandose():
        print(f"⚠️  No se abrió chatbot nuevo - Ya existe una instancia activa")
        return False
    
    # Verificar que el script existe
    if not CHATBOT_SCRIPT.exists():
        print(f"❌ Error: No se encontró {CHATBOT_SCRIPT}")
        return False
    
    try:
        # Abrir el chatbot como proceso independiente
        print(f"🚀 Abriendo chatbot en modo: {modo.upper()}")
        
        # CREAR ARCHIVO DE BLOQUEO ANTES DE LANZAR EL PROCESO
        # Esto previene que múltiples intentos simultáneos creen duplicados
        with open(LOCK_FILE, 'w') as f:
            f.write("0")  # PID temporal
        
        # En Windows, abrir con ventana visible para debugging
        if sys.platform == 'win32':
            # Crear proceso con ventana nueva (sin DETACHED para que se vea)
            proceso = subprocess.Popen(
                [sys.executable, str(CHATBOT_SCRIPT), f"--modo={modo}"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=str(CHATBOT_SCRIPT.parent)
            )
        else:
            # En Linux/Mac
            proceso = subprocess.Popen(
                [sys.executable, str(CHATBOT_SCRIPT), f"--modo={modo}"],
                cwd=str(CHATBOT_SCRIPT.parent),
                start_new_session=True
            )
        
        # Dar tiempo para que el proceso inicie
        time.sleep(1.5)  # Aumentado para dar tiempo a Flet
        
        # Verificar que el proceso inició correctamente
        if proceso.poll() is None:  # None significa que sigue corriendo
            # Actualizar el archivo de bloqueo con el PID real
            with open(LOCK_FILE, 'w') as f:
                f.write(str(proceso.pid))
            
            print(f"✓ Chatbot iniciado exitosamente (PID: {proceso.pid})")
            print(f"   Si no se abre la ventana, revisa la consola del chatbot")
            return True
        else:
            print(f"❌ Error: El chatbot se cerró inmediatamente")
            # Limpiar archivo de bloqueo si falló
            LOCK_FILE.unlink(missing_ok=True)
            return False
            
    except Exception as e:
        print(f"❌ Error al abrir chatbot: {e}")
        return False


def limpiar_lock():
    """
    Limpia el archivo de bloqueo (llamar al cerrar el chatbot)
    """
    LOCK_FILE.unlink(missing_ok=True)
    print("🧹 Archivo de bloqueo eliminado")


def abrir_chatbot_por_estres():
    """
    Función específica para abrir el chatbot cuando se detecta estrés
    """
    return abrir_chatbot(modo='automatico')


def abrir_chatbot_manual():
    """
    Función específica para abrir el chatbot manualmente
    """
    return abrir_chatbot(modo='manual')


# ================================
# TESTING (ejecutar este archivo directamente)
# ================================
if __name__ == "__main__":
    print("="*60)
    print("🧪 PROBANDO GESTOR DE CHATBOT")
    print("="*60)
    
    print("\n1. Verificando estado inicial...")
    if esta_chatbot_ejecutandose():
        print("   → Hay una instancia activa")
    else:
        print("   → No hay instancia activa")
    
    print("\n2. Intentando abrir chatbot en modo automático...")
    resultado = abrir_chatbot_por_estres()
    print(f"   → Resultado: {'ABIERTO' if resultado else 'YA ESTABA ABIERTO'}")
    
    print("\n3. Intentando abrir otra instancia...")
    time.sleep(2)
    resultado2 = abrir_chatbot_por_estres()
    print(f"   → Resultado: {'ABIERTO' if resultado2 else 'YA ESTABA ABIERTO'}")
    
    print("\n" + "="*60)
    print("Prueba completada. El chatbot debería estar ejecutándose.")
    print("Ciérralo manualmente para probar la reapertura.")
    print("="*60)
