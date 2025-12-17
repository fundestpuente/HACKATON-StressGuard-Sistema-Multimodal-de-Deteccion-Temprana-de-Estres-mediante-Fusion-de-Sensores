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

    # RANGOS REALES DEL DATASET WESAD (basados en análisis estadístico)
    # Valores iniciales = estado RELAJADO (verificado con 97% confianza sin estrés)
    # EDA < 0.5 = muy relajado, EDA > 2.0 = estrés
    # Temp muñeca normal: 32-33°C (más baja que temp corporal 36-37°C)
    configuracion_sensores = [
        {
            "nombre": "bvp",   
            "min": -20.0,  
            "max": 20.0,  
            "res": 0.1,      
            "inicio": 2.3,
            "zona_normal": {"min": -16.5, "max": 16.0},
            "zona_estres": {"min": -16.5, "max": 17.8}
        },
        {
            "nombre": "eda",   
            "min": 0.2,    
            "max": 5.0,   
            "res": 0.01,     
            "inicio": 0.4,
            "zona_normal": {"min": 0.32, "max": 1.0},
            "zona_estres": {"min": 2.0, "max": 3.87}
        },
        {
            "nombre": "temp",  
            "min": 31.0,   
            "max": 34.0,  
            "res": 0.1,      
            "inicio": 32.5,
            "zona_normal": {"min": 31.47, "max": 32.68},
            "zona_estres": {"min": 32.77, "max": 33.25}
        }
    ]

    valores = {}
    indicadores_zona = {}
    
    # Indicador de estado de estrés con probabilidades
    estado_texto = ft.Text("Calculando...", size=24, weight="bold", color=ft.Colors.BLUE)
    estado_icono = ft.Icon(ft.Icons.FAVORITE, size=60, color=ft.Colors.BLUE)
    probabilidad_texto = ft.Text("", size=16, color=ft.Colors.GREY_700, weight="bold")
    estado_container = ft.Container(
        content=ft.Column([
            estado_icono,
            estado_texto,
            probabilidad_texto,
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
        
        # Actualizar indicador de zona
        actualizar_indicador_zona(nombre, valor)
        
        calcular_prediccion()
    
    # Función para actualizar indicador de zona según el valor
    def actualizar_indicador_zona(nombre, valor):
        conf = next(c for c in configuracion_sensores if c["nombre"] == nombre)
        
        # Determinar en qué zona está el valor CON GUÍA CLARA
        if nombre == "eda":
            if valor < 1.0:
                zona_texto = "✅ ZONA NORMAL - Modelo predice: SIN estrés"
                zona_color = ft.Colors.GREEN
            elif valor < 2.0:
                zona_texto = "⚠️ ZONA INTERMEDIA - Puede variar"
                zona_color = ft.Colors.ORANGE
            else:
                zona_texto = "🔴 ZONA DE ESTRÉS - Modelo predice: CON estrés"
                zona_color = ft.Colors.RED
        elif nombre == "bvp":
            # BVP tiene menos impacto, pero valores extremos pueden afectar
            if -16.5 <= valor <= 16.0:
                zona_texto = "✅ Rango normal (impacto menor)"
                zona_color = ft.Colors.GREEN
            else:
                zona_texto = "⚠️ Fuera de rango típico"
                zona_color = ft.Colors.ORANGE
        else:  # temp
            # Temp tiene muy poco impacto
            if 31.5 <= valor <= 32.7:
                zona_texto = "✅ Normal (impacto mínimo en predicción)"
                zona_color = ft.Colors.GREEN
            elif 32.7 < valor <= 33.3:
                zona_texto = "⚠️ Algo elevada (impacto mínimo)"
                zona_color = ft.Colors.ORANGE
            else:
                zona_texto = "ℹ️ Fuera de rango típico"
                zona_color = ft.Colors.BLUE
        
        # Actualizar el indicador
        indicadores_zona[nombre].value = zona_texto
        indicadores_zona[nombre].color = zona_color
        indicadores_zona[nombre].update()

    # Función para calcular predicción
    def calcular_prediccion():
        try:
            # Obtener valores actuales
            bvp = float(valores["bvp"].value)
            eda = float(valores["eda"].value)
            temp = float(valores["temp"].value)
            
            # Predecir con probabilidades
            prediccion = predict_stress(bvp, temp, eda, pipeline)
            
            # Obtener probabilidades directamente del modelo
            import pandas as pd
            X = pd.DataFrame([[bvp, eda, temp]], columns=['bvp', 'eda', 'temp'])
            probabilidades = pipeline.predict_proba(X)[0]
            prob_sin_estres = probabilidades[0] * 100
            prob_con_estres = probabilidades[1] * 100
            
            # Actualizar UI según resultado
            if prediccion == 1:
                estado_texto.value = "⚠️ CON ESTRÉS"
                estado_texto.color = ft.Colors.RED
                estado_icono.name = ft.Icons.WARNING_AMBER
                estado_icono.color = ft.Colors.RED
                estado_container.bgcolor = ft.Colors.RED_50
                probabilidad_texto.value = f"🔴 Probabilidad de estrés: {prob_con_estres:.1f}%"
                probabilidad_texto.color = ft.Colors.RED_900
            else:
                estado_texto.value = "✓ SIN ESTRÉS"
                estado_texto.color = ft.Colors.GREEN
                estado_icono.name = ft.Icons.FAVORITE
                estado_icono.color = ft.Colors.GREEN
                estado_container.bgcolor = ft.Colors.GREEN_50
                probabilidad_texto.value = f"✅ Probabilidad sin estrés: {prob_sin_estres:.1f}%"
                probabilidad_texto.color = ft.Colors.GREEN_900
            
            # Actualizar elementos individuales
            estado_texto.update()
            estado_icono.update()
            probabilidad_texto.update()
            estado_container.update()
            page.update()
            
            return prediccion
        except Exception as e:
            print(f"Error en predicción: {e}")
            return 0

    # Crear sliders dinámicos con indicadores de zona
    for conf in configuracion_sensores:
        valores[conf["nombre"]] = ft.Text(str(conf["inicio"]), size=14, weight="bold")
        
        # Crear indicador de zona
        indicadores_zona[conf["nombre"]] = ft.Text(
            "✅ Zona Normal", 
            size=12, 
            color=ft.Colors.GREEN,
            weight="bold"
        )
        
        # Crear guía de rangos MÁS CLARA
        if conf["nombre"] == "eda":
            guia = ft.Text(
                "⭐ FACTOR PRINCIPAL: < 1.0 = SIN estrés | > 2.0 = CON estrés",
                size=11,
                color=ft.Colors.BLUE_900,
                weight="bold"
            )
        elif conf["nombre"] == "bvp":
            guia = ft.Text(
                "Factor secundario: Rango normal -16.5 a 16.0",
                size=10,
                color=ft.Colors.GREY_600,
                italic=True
            )
        else:  # temp
            guia = ft.Text(
                "Impacto mínimo: La temperatura casi no afecta la predicción",
                size=10,
                color=ft.Colors.GREY_600,
                italic=True
            )

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
                        ft.Text(conf["nombre"].upper(), size=15, weight="bold"),
                        valores[conf["nombre"]],
                    ], alignment="spaceBetween"), 
                    slider,
                    indicadores_zona[conf["nombre"]],
                    guia
                ], spacing=5),
                bgcolor=ft.Colors.GREY_100,
                border_radius=10,
                padding=15
            )
        )
    
    page.update()
    
    # Inicializar indicadores de zona
    for conf in configuracion_sensores:
        actualizar_indicador_zona(conf["nombre"], conf["inicio"])
    
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