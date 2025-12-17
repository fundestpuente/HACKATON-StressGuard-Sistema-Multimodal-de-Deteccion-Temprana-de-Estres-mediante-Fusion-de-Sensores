import socket
import json
from datetime import datetime
import chatbot_manager  # Gestor de chatbot
import signal
import sys

HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Puerto de escucha

# Variable para controlar el bucle
servidor_activo = True

def signal_handler(sig, frame):
    """Maneja la señal Ctrl+C para cerrar el servidor correctamente"""
    global servidor_activo
    print("\n\n" + "="*60)
    print("🛑 Señal de interrupción recibida (Ctrl+C)")
    print("🧹 Cerrando servidor de forma segura...")
    print("="*60)
    servidor_activo = False

# Registrar el manejador de señales
signal.signal(signal.SIGINT, signal_handler)

print("="*60)
print("🚨 SISTEMA DE ALERTAS DE ESTRÉS - RECEPTOR ACTIVO 🚨")
print(f"Escuchando en {HOST}:{PORT}")
print("="*60)
print("💡 Presiona Ctrl+C para detener el servidor")
print("\n⏳ Esperando alertas de estrés...\n")

# Crear el socket servidor
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilizar puerto
        s.settimeout(1.0)  # Timeout de 1 segundo para permitir verificar la señal
        s.bind((HOST, PORT))
        s.listen()
        
        alerta_count = 0
        while servidor_activo:
            try:
                # Esperar conexión del Flet (con timeout)
                conn, addr = s.accept()
                with conn:
                    # Recibimos los datos
                    data = conn.recv(4096)
                    if data:
                        try:
                            # Convertimos de bytes a texto y luego a Diccionario
                            mensaje = json.loads(data.decode('utf-8'))
                            alerta_count += 1
                            
                            timestamp = datetime.now().strftime("%H:%M:%S")
                            print("\n" + "="*60)
                            print(f"⚠️  ALERTA #{alerta_count} - USUARIO ESTRESADO - [{timestamp}] ⚠️")
                            print("="*60)
                            print(f" > BVP:            {mensaje.get('bvp'):.6f}")
                            print(f" > EDA:            {mensaje.get('eda'):.6f}")
                            print(f" > Temperatura:    {mensaje.get('temp'):.6f}")
                            print(f"\n📊 Datos completos: {mensaje}")
                            print("="*60)
                            
                            # 🚀 ABRIR CHATBOT AUTOMÁTICAMENTE AL DETECTAR ESTRÉS
                            print("\n🤖 Verificando estado del chatbot...")
                            chatbot_manager.abrir_chatbot_por_estres()
                            print()
                            
                        except json.JSONDecodeError:
                            print("❌ Error al decodificar JSON")
            
            except socket.timeout:
                # Timeout normal, continuar esperando
                continue
            except OSError as e:
                if servidor_activo:
                    print(f"⚠️ Error de socket: {e}")
                break

except KeyboardInterrupt:
    print("\n🛑 Interrupción detectada")
except Exception as e:
    print(f"\n❌ Error crítico: {e}")
finally:
    print("\n✅ Servidor cerrado correctamente")
    print("👋 Hasta luego\n")
    sys.exit(0)