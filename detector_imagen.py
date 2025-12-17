"""
Detector de Estrés por Imágenes - Interfaz Flet
Usa Deep Learning para detectar estrés en fotografías faciales
Si detecta estrés, abre el chatbot automáticamente
"""

import flet as ft
import os
import sys
import subprocess
from pathlib import Path

# Verificar dependencias críticas antes de continuar
TENSORFLOW_DISPONIBLE = False
OPENCV_DISPONIBLE = False

try:
    import tensorflow as tf
    TENSORFLOW_DISPONIBLE = True
except ImportError:
    pass

try:
    import cv2
    OPENCV_DISPONIBLE = True
except ImportError:
    pass

# Agregar DeepLearning al path
base_dir = os.path.dirname(os.path.abspath(__file__))
deeplearning_dir = os.path.join(base_dir, 'DeepLearning')
if deeplearning_dir not in sys.path:
    sys.path.insert(0, deeplearning_dir)

# Importar StressDetector solo si TensorFlow está disponible
StressDetector = None
if TENSORFLOW_DISPONIBLE:
    try:
        from stress_detector_model import StressDetector
    except Exception as e:
        print(f"Advertencia: No se pudo importar StressDetector: {e}")

# Ruta del modelo entrenado (buscar múltiples ubicaciones)
MODEL_PATH = None
possible_paths = [
    os.path.join(base_dir, 'DeepLearning', 'stress_model.h5'),
    os.path.join(base_dir, 'DeepLearning', 'best_stress_model.h5'),
    os.path.join(base_dir, 'DeepLearning', 'stress_model.keras'),
]

for path in possible_paths:
    if os.path.exists(path):
        MODEL_PATH = path
        break

# Si no se encuentra, usar el path por defecto
if MODEL_PATH is None:
    MODEL_PATH = possible_paths[0]

def main(page: ft.Page):
    page.title = "StressGuard - Detector de Estrés por Imagen"
    page.vertical_alignment = "start"
    page.padding = 20
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 800
    page.window_height = 700
    page.scroll = ft.ScrollMode.AUTO
    
    # Verificar dependencias primero
    if not TENSORFLOW_DISPONIBLE or not OPENCV_DISPONIBLE:
        # Mostrar pantalla de error con instrucciones
        faltantes = []
        if not TENSORFLOW_DISPONIBLE:
            faltantes.append("TensorFlow")
        if not OPENCV_DISPONIBLE:
            faltantes.append("OpenCV")
        
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=80, color=ft.Colors.RED),
                    ft.Text(
                        "❌ Dependencias Faltantes",
                        size=32,
                        weight="bold",
                        color=ft.Colors.RED,
                        selectable=True
                    ),
                    ft.Divider(height=30),
                    ft.Text(
                        f"Faltan las siguientes librerías:",
                        size=18,
                        weight="bold",
                        selectable=True
                    ),
                    ft.Column([
                        ft.Text(f"• {lib}", size=16, color=ft.Colors.RED_700, selectable=True)
                        for lib in faltantes
                    ], spacing=5),
                    ft.Divider(height=30),
                    ft.Text(
                        "📋 Instrucciones de Instalación:",
                        size=18,
                        weight="bold",
                        color=ft.Colors.BLUE_900,
                        selectable=True
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("1. Abrir PowerShell/Terminal", size=14, selectable=True),
                            ft.Text("2. Ejecutar los siguientes comandos:", size=14, selectable=True),
                            ft.Container(
                                content=ft.SelectionArea(
                                    content=ft.Text(
                                        "pip install tensorflow opencv-python numpy Pillow",
                                        size=13,
                                        font_family="Courier New"
                                    )
                                ),
                                bgcolor=ft.Colors.GREY_900,
                                padding=10,
                                border_radius=5
                            ),
                            ft.Text("3. Esperar a que termine la instalación", size=14, selectable=True),
                            ft.Text("4. Volver a abrir este detector", size=14, selectable=True),
                        ], spacing=10),
                        bgcolor=ft.Colors.BLUE_50,
                        padding=15,
                        border_radius=10
                    ),
                    ft.Divider(height=20),
                    ft.ElevatedButton(
                        "Cerrar",
                        icon=ft.Icons.CLOSE,
                        on_click=lambda _: page.window_close(),
                        style=ft.ButtonStyle(
                            bgcolor={"": ft.Colors.RED_600},
                            color={"": ft.Colors.WHITE}
                        )
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=40,
                alignment=ft.alignment.center,
                expand=True
            )
        )
        return
    
    # Si StressDetector no se pudo importar
    if StressDetector is None:
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.WARNING, size=80, color=ft.Colors.ORANGE),
                    ft.Text(
                        "⚠️ Error al cargar módulo",
                        size=32,
                        weight="bold",
                        color=ft.Colors.ORANGE,
                        selectable=True
                    ),
                    ft.Text(
                        "No se pudo importar el modelo de Deep Learning",
                        size=16,
                        selectable=True
                    ),
                    ft.Text(
                        "Verifica que el archivo DeepLearning/stress_detector_model.py exista",
                        size=14,
                        color=ft.Colors.GREY_700,
                        selectable=True
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=40
            )
        )
        return
    
    # Estado
    imagen_seleccionada = {"path": None}
    detector = None
    modelo_cargado = False
    
    # Cargar modelo al inicio
    status_text = ft.Text("🔄 Cargando modelo...", size=14, color=ft.Colors.BLUE, selectable=True)
    page.add(status_text)
    page.update()
    
    try:
        detector = StressDetector()
        if os.path.exists(MODEL_PATH):
            detector.load_model(MODEL_PATH)
            # Verificar que el modelo realmente se cargó
            if detector.model is not None:
                status_text.value = "✅ Modelo cargado correctamente"
                status_text.color = ft.Colors.GREEN
                modelo_cargado = True
            else:
                status_text.value = f"⚠️ Modelo no se pudo cargar: {os.path.basename(MODEL_PATH)}"
                status_text.color = ft.Colors.ORANGE
        else:
            status_text.value = f"⚠️ Modelo no encontrado. Entrena el modelo primero."
            status_text.color = ft.Colors.ORANGE
    except Exception as e:
        status_text.value = f"❌ Error al cargar modelo: {str(e)[:100]}"
        status_text.color = ft.Colors.RED
        print(f"Error detallado al cargar modelo: {e}")
        import traceback
        traceback.print_exc()
    
    page.update()
    
    # Contenedor de resultados
    resultado_container = ft.Container(
        visible=False,
        bgcolor=ft.Colors.GREY_100,
        border_radius=15,
        padding=20,
        alignment=ft.alignment.center
    )
    
    # Vista previa de imagen
    imagen_preview = ft.Image(
        visible=False,
        width=400,
        height=400,
        fit=ft.ImageFit.CONTAIN,
        border_radius=10
    )
    
    def abrir_chatbot():
        """Abre el chatbot en una nueva ventana"""
        try:
            # Usar ruta absoluta para evitar problemas
            chatbot_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Chatbot', 'inter_chatbot.py'))
            print(f"🔍 Buscando chatbot en: {chatbot_path}")
            
            if os.path.exists(chatbot_path):
                # Abrir chatbot en proceso separado usando Python del sistema (no 3.12)
                # El chatbot usa Python 3.14 con sus dependencias
                if sys.platform == 'win32':
                    # Usar py sin versión (Python por defecto del sistema)
                    process = subprocess.Popen(
                        ['py', chatbot_path], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                        cwd=os.path.dirname(chatbot_path)  # Establecer directorio de trabajo
                    )
                    print(f"✅ Chatbot iniciado (PID: {process.pid})")
                else:
                    process = subprocess.Popen(
                        ['python3', chatbot_path],
                        cwd=os.path.dirname(chatbot_path)
                    )
                    print(f"✅ Chatbot iniciado (PID: {process.pid})")
            else:
                print(f"❌ No se encontró el chatbot en: {chatbot_path}")
        except Exception as e:
            print(f"❌ Error al abrir chatbot: {e}")
            import traceback
            traceback.print_exc()
    
    def analizar_imagen(e):
        """Analiza la imagen seleccionada"""
        if not imagen_seleccionada["path"]:
            return
        
        # Validar que el archivo existe
        if not os.path.exists(imagen_seleccionada["path"]):
            resultado_container.content = ft.Column([
                ft.Icon(ft.Icons.ERROR, size=60, color=ft.Colors.RED),
                ft.Text("❌ Imagen no encontrada", size=20, weight="bold", color=ft.Colors.RED, selectable=True),
                ft.Text(f"El archivo no existe: {imagen_seleccionada['path']}", size=12, selectable=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            resultado_container.visible = True
            page.update()
            return
        
        if not detector or not modelo_cargado or detector.model is None:
            resultado_container.content = ft.Column([
                ft.Icon(ft.Icons.ERROR, size=60, color=ft.Colors.RED),
                ft.Text("❌ Modelo no disponible", size=20, weight="bold", color=ft.Colors.RED, selectable=True),
                ft.Text("El modelo no está cargado. Entrena el modelo primero con:", size=14, selectable=True),
                ft.Container(
                    content=ft.SelectionArea(
                        content=ft.Text(
                            "py -3.12 DeepLearning/train_stress_model.py",
                            size=13,
                            font_family="Courier New",
                            color=ft.Colors.WHITE
                        )
                    ),
                    bgcolor=ft.Colors.GREY_900,
                    padding=10,
                    border_radius=5
                ),
                ft.Text("O usa el archivo ENTRENAR_MODELO.bat", size=12, color=ft.Colors.GREY_700, selectable=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            resultado_container.visible = True
            page.update()
            return
        
        # Mostrar cargando
        resultado_container.content = ft.Column([
            ft.ProgressRing(),
            ft.Text("🔍 Analizando imagen...", size=16, selectable=True)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        resultado_container.visible = True
        page.update()
        
        try:
            # Hacer predicción
            result = detector.predict_stress(imagen_seleccionada["path"])
            
            clase = result['class']
            confianza = result['confidence']
            prob_stress = result['probabilities']['Stress']
            prob_non_stress = result['probabilities']['Non-Stress']
            prob_neutral = result['probabilities'].get('Neutral', 0)
            
            # Determinar color e icono
            if clase == 'Stress':
                icono = ft.Icons.WARNING_AMBER
                color = ft.Colors.RED
                bg_color = ft.Colors.RED_50
                mensaje = "⚠️ ESTRÉS DETECTADO"
                accion_texto = "🤖 Abriendo chatbot de ayuda..."
            elif clase == 'Non-Stress':
                icono = ft.Icons.SENTIMENT_SATISFIED
                color = ft.Colors.GREEN
                bg_color = ft.Colors.GREEN_50
                mensaje = "✅ SIN ESTRÉS"
                accion_texto = None
            else:  # Neutral
                icono = ft.Icons.SENTIMENT_NEUTRAL
                color = ft.Colors.ORANGE
                bg_color = ft.Colors.ORANGE_50
                mensaje = "😐 ESTADO NEUTRAL"
                accion_texto = None
            
            # Crear resultado visual
            resultado_content = ft.Column([
                ft.Icon(icono, size=80, color=color),
                ft.Text(mensaje, size=28, weight="bold", color=color, selectable=True),
                ft.Text(f"Confianza: {confianza:.1%}", size=20, color=color, selectable=True),
                ft.Divider(height=20),
                ft.Text("📊 Probabilidades:", size=16, weight="bold", selectable=True),
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("😌 Sin Estrés", size=14, selectable=True),
                            ft.Text(f"{prob_non_stress:.1%}", size=20, weight="bold", color=ft.Colors.GREEN, selectable=True)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=ft.Colors.GREEN_50,
                        padding=15,
                        border_radius=10,
                        expand=True
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("😐 Neutral", size=14, selectable=True),
                            ft.Text(f"{prob_neutral:.1%}", size=20, weight="bold", color=ft.Colors.ORANGE, selectable=True)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=ft.Colors.ORANGE_50,
                        padding=15,
                        border_radius=10,
                        expand=True
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("😰 Estrés", size=14, selectable=True),
                            ft.Text(f"{prob_stress:.1%}", size=20, weight="bold", color=ft.Colors.RED, selectable=True)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        bgcolor=ft.Colors.RED_50,
                        padding=15,
                        border_radius=10,
                        expand=True
                    ),
                ], spacing=10)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
            
            # Si hay acción (estrés detectado)
            if accion_texto:
                resultado_content.controls.append(ft.Divider(height=20))
                resultado_content.controls.append(
                    ft.Text(accion_texto, size=16, color=ft.Colors.BLUE, weight="bold", selectable=True)
                )
            
            resultado_container.content = resultado_content
            resultado_container.bgcolor = bg_color
            resultado_container.visible = True
            page.update()
            
            # Si detectó estrés, abrir chatbot
            if clase == 'Stress':
                import time
                time.sleep(2)  # Esperar 2 segundos para que vea el resultado
                abrir_chatbot()
            
        except Exception as e:
            error_msg = str(e)
            # Mensajes de error más amigables
            if "No se pudo cargar la imagen" in error_msg or "src.empty()" in error_msg:
                error_msg = "La imagen no se pudo cargar. Verifica que el archivo sea una imagen válida (JPG, PNG, BMP)."
            elif "modelo" in error_msg.lower():
                error_msg = "Error con el modelo. Asegúrate de haberlo entrenado primero."
            
            resultado_container.content = ft.Column([
                ft.Icon(ft.Icons.ERROR, size=60, color=ft.Colors.RED),
                ft.Text("❌ Error al analizar", size=20, weight="bold", color=ft.Colors.RED, selectable=True),
                ft.Text(error_msg, size=12, color=ft.Colors.GREY_700, selectable=True),
                ft.Container(height=10),
                ft.Text("💡 Sugerencias:", size=14, weight="bold", selectable=True),
                ft.Text("• Verifica que la imagen sea válida", size=12, selectable=True),
                ft.Text("• Intenta con otra imagen", size=12, selectable=True),
                ft.Text("• Asegúrate de que el archivo no esté dañado", size=12, selectable=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            resultado_container.visible = True
            page.update()
    
    def seleccionar_imagen(e: ft.FilePickerResultEvent):
        """Maneja la selección de imagen"""
        if e.files:
            archivo = e.files[0]
            imagen_seleccionada["path"] = archivo.path
            
            # Mostrar preview
            imagen_preview.src = archivo.path
            imagen_preview.visible = True
            
            # Habilitar botón analizar
            btn_analizar.disabled = False
            
            # Actualizar texto
            texto_seleccion.value = f"📁 {os.path.basename(archivo.path)}"
            texto_seleccion.color = ft.Colors.GREEN
            
            # Ocultar resultado anterior
            resultado_container.visible = False
            
            page.update()
    
    # File picker
    file_picker = ft.FilePicker(on_result=seleccionar_imagen)
    page.overlay.append(file_picker)
    
    # UI Components
    texto_seleccion = ft.Text(
        "No hay imagen seleccionada", 
        size=14, 
        color=ft.Colors.GREY,
        selectable=True
    )
    
    btn_seleccionar = ft.ElevatedButton(
        "📷 Seleccionar Imagen",
        icon=ft.Icons.UPLOAD_FILE,
        on_click=lambda _: file_picker.pick_files(
            allowed_extensions=["jpg", "jpeg", "png", "bmp"],
            dialog_title="Selecciona una imagen facial"
        ),
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.BLUE
        )
    )
    
    btn_analizar = ft.ElevatedButton(
        "🔍 Analizar Estrés",
        icon=ft.Icons.PSYCHOLOGY,
        on_click=analizar_imagen,
        disabled=True,
        style=ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.GREEN
        )
    )
    
    # Layout principal
    page.clean()
    page.add(
        ft.Column([
            # Header
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "🧠 Detector de Estrés por Imagen",
                        size=32,
                        weight="bold",
                        color=ft.Colors.BLUE_900,
                        selectable=True
                    ),
                    ft.Text(
                        "Sube una fotografía facial para detectar señales de estrés",
                        size=16,
                        color=ft.Colors.GREY_700,
                        selectable=True
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20
            ),
            
            ft.Divider(height=20),
            
            # Controles
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        btn_seleccionar,
                        btn_analizar,
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                    texto_seleccion,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
                padding=20,
                bgcolor=ft.Colors.GREY_50,
                border_radius=15
            ),
            
            # Preview de imagen
            ft.Container(
                content=imagen_preview,
                alignment=ft.alignment.center,
                padding=20
            ),
            
            # Resultados
            resultado_container,
            
            # Info
            ft.Container(
                content=ft.Column([
                    ft.Text("ℹ️ Información", size=14, weight="bold", selectable=True),
                    ft.Text(
                        "• Si se detecta estrés, el chatbot se abrirá automáticamente",
                        size=12,
                        selectable=True
                    ),
                    ft.Text(
                        "• El modelo analiza expresiones faciales para detectar estrés",
                        size=12,
                        selectable=True
                    ),
                    ft.Text(
                        "• Formatos aceptados: JPG, PNG, BMP",
                        size=12,
                        selectable=True
                    ),
                ], spacing=5),
                padding=15,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10
            )
            
        ], spacing=20, scroll=ft.ScrollMode.ADAPTIVE)
    )

if __name__ == "__main__":
    try:
        print("="*60)
        print("📷 INICIANDO DETECTOR DE ESTRÉS POR IMAGEN")
        print("="*60)
        print()
        ft.app(target=main)
    except Exception as e:
        print(f"\n❌ ERROR AL INICIAR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
