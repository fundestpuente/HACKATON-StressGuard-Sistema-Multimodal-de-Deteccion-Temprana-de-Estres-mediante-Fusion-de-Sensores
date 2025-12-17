"""
🚀 STRESSGUARD - LAUNCHER PRINCIPAL
Sistema Multimodal de Detección Temprana de Estrés

Interfaz gráfica para acceder a todos los módulos del sistema
"""

import flet as ft
import subprocess
import sys
import os
from pathlib import Path
import psutil
import time
import threading

# Rutas de los módulos
BASE_DIR = Path(__file__).parent
CHATBOT_DIR = BASE_DIR / "Chatbot"
ML_DIR = BASE_DIR / "MachineLearning"

CHATBOT_SCRIPT = CHATBOT_DIR / "inter_chatbot.py"
SIMULADOR_SCRIPT = ML_DIR / "simu_reloj.py"
RECEPTOR_SCRIPT = ML_DIR / "receptor_datos.py"
DETECTOR_IMAGEN_SCRIPT = BASE_DIR / "detector_imagen.py"

# Control de procesos
procesos_activos = {
    "receptor": None,
    "simulador": None,
    "chatbot": None
}


def ejecutar_proceso(script_path, nombre, creationflags=None):
    """
    Ejecuta un script Python como proceso independiente
    
    Args:
        script_path: Ruta al script
        nombre: Nombre descriptivo del proceso
        creationflags: Flags específicos de Windows
    
    Returns:
        Proceso iniciado o None si hay error
    """
    try:
        if not script_path.exists():
            print(f"❌ Error: No se encontró {script_path}")
            return None
        
        if sys.platform == 'win32':
            if creationflags is None:
                # Crear nueva ventana de consola visible
                creationflags = subprocess.CREATE_NEW_CONSOLE
            
            proceso = subprocess.Popen(
                [sys.executable, str(script_path)],
                creationflags=creationflags,
                cwd=str(script_path.parent)
            )
        else:
            proceso = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(script_path.parent),
                start_new_session=True
            )
        
        print(f"✅ {nombre} iniciado (PID: {proceso.pid})")
        return proceso
        
    except Exception as e:
        print(f"❌ Error al iniciar {nombre}: {e}")
        return None


def esta_proceso_activo(proceso):
    """Verifica si un proceso está activo"""
    if proceso is None:
        return False
    try:
        return proceso.poll() is None
    except:
        return False


def terminar_proceso(proceso, nombre):
    """Termina un proceso de forma segura"""
    if proceso and esta_proceso_activo(proceso):
        try:
            # Intentar terminar normalmente
            proceso.terminate()
            try:
                proceso.wait(timeout=3)
                print(f"🛑 {nombre} terminado correctamente")
            except subprocess.TimeoutExpired:
                # Forzar cierre si no responde
                proceso.kill()
                print(f"🔨 {nombre} forzado a cerrar")
        except Exception as e:
            print(f"⚠️ Error al terminar {nombre}: {e}")


def main(page: ft.Page):
    page.title = "StressGuard - Launcher"
    page.window_width = 600
    page.window_height = 850
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # ==========================================
    # ESTADOS Y VARIABLES
    # ==========================================
    
    # Indicadores de estado
    estado_receptor = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CIRCLE, size=12, color=ft.Colors.GREY_400),
            ft.Text("Receptor: Detenido", size=12, color=ft.Colors.GREY_600)
        ], tight=True),
        padding=5
    )
    
    estado_simulador = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CIRCLE, size=12, color=ft.Colors.GREY_400),
            ft.Text("Simulador: Detenido", size=12, color=ft.Colors.GREY_600)
        ], tight=True),
        padding=5
    )
    
    # ==========================================
    # FUNCIONES DE CONTROL
    # ==========================================
    
    def actualizar_estado_receptor(activo):
        """Actualiza el indicador visual del receptor"""
        if activo:
            estado_receptor.content.controls[0].color = ft.Colors.GREEN_500
            estado_receptor.content.controls[1].value = "Receptor: Activo"
            estado_receptor.content.controls[1].color = ft.Colors.GREEN_700
        else:
            estado_receptor.content.controls[0].color = ft.Colors.GREY_400
            estado_receptor.content.controls[1].value = "Receptor: Detenido"
            estado_receptor.content.controls[1].color = ft.Colors.GREY_600
        estado_receptor.update()
    
    def actualizar_estado_simulador(activo):
        """Actualiza el indicador visual del simulador"""
        if activo:
            estado_simulador.content.controls[0].color = ft.Colors.BLUE_500
            estado_simulador.content.controls[1].value = "Simulador: Activo"
            estado_simulador.content.controls[1].color = ft.Colors.BLUE_700
        else:
            estado_simulador.content.controls[0].color = ft.Colors.GREY_400
            estado_simulador.content.controls[1].value = "Simulador: Detenido"
            estado_simulador.content.controls[1].color = ft.Colors.GREY_600
        estado_simulador.update()
    
    def monitorear_procesos():
        """Monitorea el estado de los procesos en segundo plano"""
        while True:
            time.sleep(2)
            
            # Verificar receptor
            if esta_proceso_activo(procesos_activos["receptor"]):
                actualizar_estado_receptor(True)
            else:
                if procesos_activos["receptor"] is not None:
                    # Se cerró, actualizar estado
                    procesos_activos["receptor"] = None
                    actualizar_estado_receptor(False)
            
            # Verificar simulador
            if esta_proceso_activo(procesos_activos["simulador"]):
                actualizar_estado_simulador(True)
            else:
                if procesos_activos["simulador"] is not None:
                    # Se cerró, actualizar estado
                    procesos_activos["simulador"] = None
                    actualizar_estado_simulador(False)
    
    # Iniciar monitoreo en segundo plano
    threading.Thread(target=monitorear_procesos, daemon=True).start()
    
    def abrir_chatbot_manual(e):
        """Abre el chatbot en modo manual (usuario inicia conversación)"""
        print("\n" + "="*60)
        print("🤖 ABRIENDO CHATBOT EN MODO MANUAL")
        print("="*60)
        
        # Importar el gestor del chatbot
        sys.path.insert(0, str(ML_DIR))
        try:
            import chatbot_manager
            resultado = chatbot_manager.abrir_chatbot_manual()
            
            if resultado:
                mostrar_snackbar("✅ Chatbot abierto correctamente", ft.Colors.GREEN_700)
            else:
                mostrar_snackbar("⚠️ El chatbot ya está abierto", ft.Colors.ORANGE_700)
        except Exception as ex:
            print(f"❌ Error: {ex}")
            mostrar_snackbar(f"❌ Error al abrir chatbot: {ex}", ft.Colors.RED_700)
    
    def abrir_detector_imagen(e):
        """Abre el detector de estrés por imagen"""
        print("\n" + "="*60)
        print("📷 ABRIENDO DETECTOR DE ESTRÉS POR IMAGEN")
        print("="*60)
        
        try:
            # Usar Python 3.12 específicamente (tiene TensorFlow)
            if sys.platform == 'win32':
                proceso = subprocess.Popen(
                    ['py', '-3.12', str(DETECTOR_IMAGEN_SCRIPT)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=str(DETECTOR_IMAGEN_SCRIPT.parent)
                )
            else:
                proceso = subprocess.Popen(
                    ['python3.12', str(DETECTOR_IMAGEN_SCRIPT)],
                    cwd=str(DETECTOR_IMAGEN_SCRIPT.parent),
                    start_new_session=True
                )
            
            print(f"✅ Detector de Imagen iniciado (PID: {proceso.pid})")
            mostrar_snackbar("✅ Detector de imagen abierto (Python 3.12)", ft.Colors.GREEN_700)
                
        except Exception as ex:
            print(f"❌ Error: {ex}")
            mostrar_snackbar(f"❌ Error: {ex}", ft.Colors.RED_700)
    
    def iniciar_sistema_completo(e):
        """Inicia el sistema completo: Receptor + Simulador"""
        print("\n" + "="*60)
        print("🚀 INICIANDO SISTEMA COMPLETO DE DETECCIÓN DE ESTRÉS")
        print("="*60)
        
        # 1. Iniciar receptor si no está activo
        if not esta_proceso_activo(procesos_activos["receptor"]):
            print("📡 Iniciando receptor de datos...")
            procesos_activos["receptor"] = ejecutar_proceso(
                RECEPTOR_SCRIPT, 
                "Receptor de Datos"
            )
            time.sleep(1)  # Dar tiempo para que inicie
            actualizar_estado_receptor(True)
        else:
            print("✓ Receptor ya está activo")
        
        # 2. Iniciar simulador si no está activo
        if not esta_proceso_activo(procesos_activos["simulador"]):
            print("⌚ Iniciando simulador de reloj...")
            procesos_activos["simulador"] = ejecutar_proceso(
                SIMULADOR_SCRIPT, 
                "Simulador de Reloj"
            )
            actualizar_estado_simulador(True)
            mostrar_snackbar("✅ Sistema iniciado correctamente", ft.Colors.GREEN_700)
        else:
            print("✓ Simulador ya está activo")
            mostrar_snackbar("⚠️ El simulador ya está ejecutándose", ft.Colors.ORANGE_700)
        
        print("="*60)
        print("✅ SISTEMA LISTO")
        print("   - Ajusta los sensores para simular estrés")
        print("   - El chatbot se abrirá automáticamente")
        print("="*60)
    
    def detener_sistema(e):
        """Detiene todos los procesos activos"""
        print("\n🛑 Deteniendo sistema...")
        
        terminar_proceso(procesos_activos["simulador"], "Simulador")
        procesos_activos["simulador"] = None
        actualizar_estado_simulador(False)
        
        terminar_proceso(procesos_activos["receptor"], "Receptor")
        procesos_activos["receptor"] = None
        actualizar_estado_receptor(False)
        
        mostrar_snackbar("🛑 Sistema detenido", ft.Colors.BLUE_GREY_700)
        print("✅ Sistema detenido\n")
    
    def mostrar_snackbar(mensaje, color=ft.Colors.BLUE_700):
        """Muestra una notificación temporal"""
        page.snack_bar = ft.SnackBar(
            content=ft.Text(mensaje, color=ft.Colors.WHITE),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()
    
    def salir_aplicacion(e):
        """Cierra la aplicación y todos los procesos"""
        detener_sistema(None)
        page.window_close()
    
    # ==========================================
    # INTERFAZ GRÁFICA
    # ==========================================
    
    # Header
    header = ft.Container(
        content=ft.Column([
            ft.Container(height=20),
            ft.Icon(ft.Icons.HEALTH_AND_SAFETY, size=70, color=ft.Colors.WHITE),
            ft.Text(
                "StressGuard",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            ft.Text(
                "Sistema Multimodal de Detección de Estrés",
                size=14,
                color=ft.Colors.WHITE70,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=10),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_center,
            end=ft.alignment.bottom_center,
            colors=[ft.Colors.BLUE_800, ft.Colors.BLUE_600]
        ),
        padding=20
    )
    
    # Tarjeta de Chatbot
    card_chatbot = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CHAT_BUBBLE, size=40, color=ft.Colors.BLUE_600),
                ft.Column([
                    ft.Text("Chatbot Asistente", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Conversa con StressWard", size=12, color=ft.Colors.GREY_600)
                ], spacing=2, expand=True)
            ], spacing=15),
            ft.Container(height=10),
            ft.Text(
                "Abre el chatbot para conversar libremente. El chatbot no conocerá tu estado inicial de estrés.",
                size=13,
                color=ft.Colors.GREY_700
            ),
            ft.Container(height=15),
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.OPEN_IN_NEW, size=18),
                    ft.Text("Abrir Chatbot", size=15)
                ], tight=True, spacing=8),
                style=ft.ButtonStyle(
                    bgcolor={"": ft.Colors.BLUE_600},
                    color={"": ft.Colors.WHITE},
                    padding=15
                ),
                width=250,
                on_click=abrir_chatbot_manual
            )
        ], spacing=5),
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.BLUE_200),
        border_radius=15,
        padding=20,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.BLACK12
        )
    )
    
    # Tarjeta de Detector de Imagen
    card_detector_imagen = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CAMERA_ALT, size=40, color=ft.Colors.PURPLE_600),
                ft.Column([
                    ft.Text("Detector por Imagen", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Deep Learning facial", size=12, color=ft.Colors.GREY_600)
                ], spacing=2, expand=True)
            ], spacing=15),
            ft.Container(height=10),
            ft.Text(
                "Sube una fotografía facial para detectar estrés usando Deep Learning. El chatbot se abrirá si se detecta estrés.",
                size=13,
                color=ft.Colors.GREY_700
            ),
            ft.Container(height=15),
            ft.ElevatedButton(
                content=ft.Row([
                    ft.Icon(ft.Icons.PHOTO_CAMERA, size=18),
                    ft.Text("Abrir Detector", size=15)
                ], tight=True, spacing=8),
                style=ft.ButtonStyle(
                    bgcolor={"": ft.Colors.PURPLE_600},
                    color={"": ft.Colors.WHITE},
                    padding=15
                ),
                width=250,
                on_click=abrir_detector_imagen
            )
        ], spacing=5),
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.PURPLE_200),
        border_radius=15,
        padding=20,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.BLACK12
        )
    )
    
    # Tarjeta de Sistema de Detección
    card_sistema = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.MONITOR_HEART, size=40, color=ft.Colors.GREEN_600),
                ft.Column([
                    ft.Text("Sistema de Detección", size=20, weight=ft.FontWeight.BOLD),
                    ft.Text("Simulador + Detección automática", size=12, color=ft.Colors.GREY_600)
                ], spacing=2, expand=True)
            ], spacing=15),
            ft.Container(height=10),
            ft.Text(
                "Inicia el simulador de reloj Samsung. Cuando se detecte estrés, el chatbot se abrirá automáticamente.",
                size=13,
                color=ft.Colors.GREY_700
            ),
            ft.Container(height=15),
            ft.Row([
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PLAY_ARROW, size=18),
                        ft.Text("Iniciar Sistema", size=15)
                    ], tight=True, spacing=8),
                    style=ft.ButtonStyle(
                        bgcolor={"": ft.Colors.GREEN_600},
                        color={"": ft.Colors.WHITE},
                        padding=15
                    ),
                    expand=True,
                    on_click=iniciar_sistema_completo
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.STOP, size=18),
                        ft.Text("Detener", size=15)
                    ], tight=True, spacing=8),
                    style=ft.ButtonStyle(
                        bgcolor={"": ft.Colors.RED_600},
                        color={"": ft.Colors.WHITE},
                        padding=15
                    ),
                    expand=True,
                    on_click=detener_sistema
                ),
            ], spacing=10)
        ], spacing=5),
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(1, ft.Colors.GREEN_200),
        border_radius=15,
        padding=20,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=10,
            color=ft.Colors.BLACK12
        )
    )
    
    # Panel de estado
    panel_estado = ft.Container(
        content=ft.Column([
            ft.Text("Estado del Sistema", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
            ft.Divider(height=10),
            estado_receptor,
            estado_simulador,
        ], spacing=5),
        bgcolor=ft.Colors.GREY_50,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        padding=15
    )
    
    # Botón de salir
    btn_salir = ft.TextButton(
        content=ft.Row([
            ft.Icon(ft.Icons.EXIT_TO_APP, size=16),
            ft.Text("Salir", size=14)
        ], tight=True, spacing=5),
        on_click=salir_aplicacion
    )
    
    # Layout principal
    page.add(
        ft.Column([
            header,
            ft.Container(
                content=ft.Column([
                    card_chatbot,
                    ft.Container(height=15),
                    card_detector_imagen,
                    ft.Container(height=15),
                    card_sistema,
                    ft.Container(height=15),
                    panel_estado,
                    ft.Container(height=15),
                    ft.Container(
                        content=btn_salir,
                        alignment=ft.alignment.center
                    )
                ], spacing=0, scroll=ft.ScrollMode.AUTO),
                padding=20,
                expand=True
            )
        ], spacing=0, expand=True)
    )


if __name__ == "__main__":
    print("="*60)
    print("🚀 STRESSGUARD - LAUNCHER PRINCIPAL")
    print("="*60)
    print("Iniciando interfaz gráfica...")
    print()
    
    ft.app(target=main)
