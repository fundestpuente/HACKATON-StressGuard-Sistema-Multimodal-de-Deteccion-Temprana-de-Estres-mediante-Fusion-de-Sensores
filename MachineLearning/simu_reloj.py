import flet as ft
import asyncio
import socket
import json
import math
from stress_model import load_model, predict_stress

# Configuración de red
HOST = '127.0.0.1'
PORT = 65432

async def main(page: ft.Page):
    page.title = "Simulador de Estrés - Empatica E4"
    page.vertical_alignment = "start"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT

    # Cargar modelo al inicio
    print("Cargando modelo de Machine Learning...")
    pipeline = load_model()
    print("Modelo cargado exitosamente.")

    configuracion_sensores = [
        {"nombre": "bvp",   "min": -100.0, "max": 100.0, "res": 0.01,     "inicio": 0.9034},
        {"nombre": "eda",   "min": 0.0,    "max": 10.0,  "res": 0.01,     "inicio": 2.1356},
        {"nombre": "temp",  "min": 28.0,   "max": 36.0,  "res": 0.01,     "inicio": 32.7739}
    ]

    valores = {}
    
    # Indicador de estado de estrés
    estado_texto = ft.Text("Calculando...", size=24, weight="bold", color=ft.Colors.BLUE)
    estado_icono = ft.Icon(ft.Icons.FAVORITE, size=60, color=ft.Colors.BLUE)
    estado_container = ft.Container(
        content=ft.Column([
            estado_icono,
            estado_texto,
            ft.Text("Predicción en tiempo real", size=14, color=ft.Colors.GREY)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=ft.Colors.BLUE_50,
        border_radius=15,
        padding=20,
        alignment=ft.alignment.center
    )

    contenedor = ft.Column(spacing=15)
    
    page.add(
        ft.Column([
            ft.Text("🧪 Simulador de Detección de Estrés", size=26, weight="bold"),
            ft.Text("Ajusta los parámetros y observa la predicción en tiempo real", size=14, color=ft.Colors.GREY),
            ft.Divider(height=20),
            estado_container,
            ft.Divider(height=20),
            ft.Text("Control de Sensores", size=18, weight="bold"),
            contenedor
        ], spacing=10, scroll=ft.ScrollMode.AUTO)
    )

    # Actualiza valores de sliders visualmente y recalcula predicción
    def actualizar_valor(nombre, valor):
        valores[nombre].value = f"{valor:.6f}"
        valores[nombre].update()
        calcular_prediccion()

    # Función para calcular predicción
    def calcular_prediccion():
        try:
            # Obtener valores actuales
            bvp = float(valores["bvp"].value)
            eda = float(valores["eda"].value)
            temp = float(valores["temp"].value)
            
            # Predecir
            prediccion = predict_stress(bvp, temp, eda, pipeline)
            
            # Actualizar UI según resultado
            if prediccion == 1:
                estado_texto.value = "⚠️ ESTRESADO"
                estado_texto.color = ft.Colors.RED
                estado_icono.name = ft.Icons.WARNING_AMBER
                estado_icono.color = ft.Colors.RED
                estado_container.bgcolor = ft.Colors.RED_50
            else:
                estado_texto.value = "✓ SIN ESTRÉS"
                estado_texto.color = ft.Colors.GREEN
                estado_icono.name = ft.Icons.FAVORITE
                estado_icono.color = ft.Colors.GREEN
                estado_container.bgcolor = ft.Colors.GREEN_50
            
            # Actualizar elementos individuales
            estado_texto.update()
            estado_icono.update()
            estado_container.update()
            page.update()
            
            return prediccion
        except Exception as e:
            print(f"Error en predicción: {e}")
            return 0

    # Crear sliders dinámicos
    for conf in configuracion_sensores:
        valores[conf["nombre"]] = ft.Text(str(conf["inicio"]), size=14)

        slider = ft.Slider(
            min=conf["min"],
            max=conf["max"],
            value=conf["inicio"],
            label="{value}",
            on_change=lambda e, n=conf["nombre"]: actualizar_valor(n, e.control.value),
        )

        contenedor.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(conf["nombre"], size=15, weight="bold"),
                        valores[conf["nombre"]],
                    ], alignment="spaceBetween"), 
                    slider
                ]),
                bgcolor=ft.Colors.GREY_100,
                border_radius=10,
                padding=15
            )
        )
    
    page.update()
    
    # Calcular predicción inicial
    calcular_prediccion()

    # ================================
    #  🔥 ENVÍO DE DATOS POR PUERTO 🔥
    # ================================
    async def auto_guardado():
        contador = 0
        while True: 
            try:
                # 1. Recopilar datos
                datos = {n: float(v.value) for n, v in valores.items()}
                
                # 2. Calcular predicción
                prediccion = predict_stress(datos['bvp'], datos['temp'], datos['eda'], pipeline)
                
                # 3. SOLO ENVIAR SI HAY ESTRÉS
                if prediccion == 1:
                    print(f"⚠️ ESTRÉS DETECTADO - Enviando alerta #{contador}...")
                    
                    try:
                        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                            s.settimeout(0.5)
                            s.connect((HOST, PORT))
                            
                            mensaje_bytes = json.dumps(datos).encode('utf-8')
                            s.sendall(mensaje_bytes)
                            print(" ✓ Alerta enviada con éxito.")
                    
                    except ConnectionRefusedError:
                        print(" ✗ Error: Servidor receptor no disponible.")
                    except Exception as ex:
                        print(f" ✗ Error de red: {ex}")
                else:
                    print(f"✓ Monitoreo #{contador} - Estado: Normal")

                contador += 1
                await asyncio.sleep(2)   # Esperar 2 segundos

            except Exception as e:
                print(f"Error crítico en loop: {e}")
                break

    asyncio.create_task(auto_guardado())

ft.app(target=main, view=ft.WEB_BROWSER)