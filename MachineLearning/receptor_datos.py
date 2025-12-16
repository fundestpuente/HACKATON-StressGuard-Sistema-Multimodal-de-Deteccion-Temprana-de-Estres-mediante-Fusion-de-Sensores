import socket
import json
from datetime import datetime

HOST = '127.0.0.1'  # Localhost
PORT = 65432        # Puerto de escucha

print("="*60)
print("🚨 SISTEMA DE ALERTAS DE ESTRÉS - RECEPTOR ACTIVO 🚨")
print(f"Escuchando en {HOST}:{PORT}")
print("="*60)
print("\n⏳ Esperando alertas de estrés...\n")

# Crear el socket servidor
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    
    alerta_count = 0
    while True:
        # Esperar conexión del Flet
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
                    
                except json.JSONDecodeError:
                    print("❌ Error al decodificar JSON")