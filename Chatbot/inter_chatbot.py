import flet as ft
import pyttsx3
import threading
import speech_recognition as sr
import ollama  # Usar librería de Ollama directamente
import json
import sys
import os
from pathlib import Path
import atexit
import time

# ================================
# IMPORTACIÓN DE PROMPTS Y MÓDULOS
# ================================
try:
    import prompts  # Importamos el archivo con los dos prompts
    print("✅ Prompts cargados correctamente.")
    # Verificar que los prompts existen
    if hasattr(prompts, 'PROMPT_CHARLA') and hasattr(prompts, 'PROMPT_GUIA'):
        print(f"   - PROMPT_CHARLA: {len(prompts.PROMPT_CHARLA)} caracteres")
        print(f"   - PROMPT_GUIA: {len(prompts.PROMPT_GUIA)} caracteres")
    else:
        print("⚠️ ADVERTENCIA: Los prompts no tienen los nombres correctos")
except ImportError as e:
    prompts = None
    print(f"❌ Advertencia: No se encontró prompts.py - {e}")

try:
    import aprender
    import tablaVerdad
    modulos_cargados = True
except ImportError:
    modulos_cargados = False

# ================================
# MODO DE APERTURA Y CONTROL DE INSTANCIA
# ================================
MODO_APERTURA = 'manual'  # Por defecto
LOCK_FILE = Path(__file__).parent.parent / "MachineLearning" / ".chatbot_instance.lock"

# Detectar si se pasó parámetro de modo
if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg.startswith('--modo='):
            MODO_APERTURA = arg.split('=')[1]
            print(f"🔧 Chatbot iniciado en modo: {MODO_APERTURA.upper()}")

# ================================
# CONFIGURACIÓN OLLAMA
# ================================
MODELO_OLLAMA = "llama3.2:3b-instruct-q8_0"  # Modelo específico instalado 

# ================================
# LIMPIEZA AL CERRAR
# ================================
def limpiar_al_cerrar():
    """Elimina el archivo de bloqueo cuando se cierra el chatbot"""
    if LOCK_FILE.exists():
        try:
            LOCK_FILE.unlink()
            print("🧹 Instancia de chatbot cerrada correctamente")
        except:
            pass

atexit.register(limpiar_al_cerrar)

# ================================
# GOOGLE SPEECH
# ================================
recognizer = sr.Recognizer()

def escuchar_google(callback):
    def _escuchar():
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source)

            texto = recognizer.recognize_google(audio, language="es-ES")
            callback(texto)

        except sr.UnknownValueError:
            callback("No entendí lo que dijiste")
        except sr.RequestError:
            callback("Error de conexión con Google Speech")
        except Exception as e:
            callback(f"Error de micrófono: {e}")

    threading.Thread(target=_escuchar, daemon=True).start()

# ================================
# TEXTO A VOZ
# ================================
def hablar(texto):
    def _hablar():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150) 
            
            voices = engine.getProperty("voices")
            for v in voices:
                if "spanish" in v.name.lower() or "es" in str(v.languages).lower():
                    engine.setProperty("voice", v.id)
                    break
            
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            print("Error TTS:", e)

    threading.Thread(target=_hablar, daemon=True).start()

# ================================
# APP PRINCIPAL
# ================================
def main(page: ft.Page):
        # ----------------
    # VARIABLES DE INICIATIVA
    # ----------------
    ultima_interaccion = time.time()

    page.title = "StressGuard_chat - Asistente Virtual"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 500
    page.window_height = 700

    # ----------------
    # VARIABLES DE ESTADO
    # ----------------
    contexto_ollama = []  # Limpiar contexto al inicio
    
    # Variable para controlar la voz (Audio)
    voz_activa = True
    
    # Variable para controlar si ya se mostró el mensaje inicial
    mensaje_inicial_mostrado = False
    
    # Variable para el Router Pattern (Controla qué Prompt usar)
    modo_guia_activo = False 

    # Variable para el Router Pattern (Controla qué Prompt usar)
    modo_guia_activo = False

    # ----------------
    # COMPONENTES GLOBALES
    # ----------------
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    tabla_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    txt_mensaje = ft.TextField(hint_text="Escribe o habla...", expand=True)
    txt_tabla = ft.TextField(hint_text="Proposición lógica", expand=True)
    
    loading = ft.ProgressBar(width=None, color=ft.Colors.BLUE, visible=False)

    # ----------------
    # CONTROL DE VOZ (BOTÓN)
    # ----------------
    def toggle_voz(e):
        nonlocal voz_activa
        voz_activa = not voz_activa
        btn_voz.icon = ft.Icons.VOLUME_UP if voz_activa else ft.Icons.VOLUME_OFF
        btn_voz.tooltip = "Desactivar voz" if voz_activa else "Activar voz"
        page.update()

    btn_voz = ft.IconButton(
        icon=ft.Icons.VOLUME_UP,
        tooltip="Desactivar voz",
        icon_color=ft.Colors.WHITE,
        on_click=toggle_voz
    )

    # ----------------
    # FUNCIONES CHAT
    # ----------------
    def agregar_mensaje(texto, usuario=False):
        nonlocal ultima_interaccion
        ultima_interaccion = time.time()  # ← registra interacción

        color = ft.Colors.BLUE_100 if usuario else ft.Colors.GREEN_100
        icono = ft.Icons.PERSON if usuario else ft.Icons.SMART_TOY
        alineacion = ft.MainAxisAlignment.END if usuario else ft.MainAxisAlignment.START

        chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(icono, size=16),
                                        ft.Text("Tú" if usuario else "StressGuard_chat", weight="bold"),
                                    ],
                                    tight=True,
                                ),
                                ft.Markdown(texto),
                            ]
                        ),
                        bgcolor=color,
                        padding=15,
                        border_radius=10,
                        width=320,
                    )
                ],
                alignment=alineacion,
            )
        )
        page.update()
        
        if not usuario and voz_activa:
            hablar(texto)

    # -----------------------------------------------
    # INTEGRACIÓN CON OLLAMA usando ollama.chat()
    # -----------------------------------------------
    def contactar_ollama(prompt_usuario):
        def _request():
            nonlocal contexto_ollama
            nonlocal modo_guia_activo
            
            # 1. Preparamos la interfaz
            loading.visible = True
            page.update()

            # LÓGICA DEL ROUTER
            if prompts:
                palabras_clave_malestar = [
                    "estrés", "estres", "mal", "ansiedad", "triste", "depre", 
                    "ayuda", "cansad", "dolor", "no puedo", "agobiad", "nervios",
                    "test", "evalu", "sintoma"
                ]
                if any(k in prompt_usuario.lower() for k in palabras_clave_malestar):
                    modo_guia_activo = True
                
                if modo_guia_activo:
                    print("Router: Usando PROMPT_GUIA")
                    instrucciones_sistema = prompts.PROMPT_GUIA
                else:
                    print("Router: Usando PROMPT_CHARLA")
                    instrucciones_sistema = prompts.PROMPT_CHARLA
                
                # Verificar que el prompt no esté vacío
                if not instrucciones_sistema or len(instrucciones_sistema) < 50:
                    print("⚠️ ADVERTENCIA: Prompt del sistema vacío o muy corto")
                    instrucciones_sistema = prompts.PROMPT_CHARLA
                    
                print(f"📝 Longitud del prompt del sistema: {len(instrucciones_sistema)} caracteres")
            else:
                print("❌ ERROR: prompts.py no está cargado")
                instrucciones_sistema = "Eres un asistente empático de bienestar emocional."

            try:
                # 2. Creamos la burbuja de chat vacía visualmente
                respuesta_acumulada = ""
                
                # Elemento de texto que iremos actualizando
                texto_markdown = ft.Markdown("", extension_set="gitHubWeb")
                
                # Agregamos la burbuja visual al chat INMEDIATAMENTE
                chat_list.controls.append(
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row([ft.Icon(ft.Icons.SMART_TOY, size=16), ft.Text("StressWard", weight="bold")], tight=True),
                                        texto_markdown,
                                    ]
                                ),
                                bgcolor=ft.Colors.GREEN_100,
                                padding=15,
                                border_radius=10,
                                width=320,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    )
                )
                page.update()

                # 3. Construir mensajes para ollama.chat()
                messages = []
                
                # Agregar el prompt del sistema
                messages.append({
                    'role': 'system',
                    'content': instrucciones_sistema
                })
                
                # Agregar historial (si existe en contexto)
                # Por ahora, solo agregamos el mensaje del usuario
                messages.append({
                    'role': 'user',
                    'content': prompt_usuario
                })
                
                # 4. Llamar a ollama.chat() con streaming
                print(f"🚀 Enviando a Ollama: {MODELO_OLLAMA}")
                
                stream = ollama.chat(
                    model=MODELO_OLLAMA,
                    messages=messages,
                    stream=True,
                    options={
                        'temperature': 0.6,
                        'repeat_penalty': 1.1,
                        'top_p': 0.9
                    }
                )
                
                # 5. Procesar streaming
                for chunk in stream:
                    if 'message' in chunk and 'content' in chunk['message']:
                        palabra = chunk['message']['content']
                        respuesta_acumulada += palabra
                        texto_markdown.value = respuesta_acumulada
                        texto_markdown.update()
                
                # Al finalizar, hablamos todo el texto si la voz está activa
                if voz_activa:
                    hablar(respuesta_acumulada)

            except Exception as e:
                print(f"❌ Error al contactar Ollama: {e}")
                texto_markdown.value = f"Error de conexión: {e}"
                texto_markdown.update()
            
            loading.visible = False
            page.update()

        threading.Thread(target=_request, daemon=True).start()

    def procesar_envio(e):
        nonlocal contexto_ollama, modo_guia_activo
        mensaje = txt_mensaje.value.strip()
        if not mensaje:
            return

        agregar_mensaje(mensaje, usuario=True)
        txt_mensaje.value = ""
        page.update()

        clave = mensaje.lower()

        if clave == "salir":
            page.window_close()
            return
        
        # Opción para reiniciar el cerebro del bot
        if clave in ["borrar memoria", "reiniciar", "reset", "limpiar"]:
            nonlocal contexto_ollama, modo_guia_activo
            contexto_ollama = []
            modo_guia_activo = False
            agregar_mensaje("🧹 He reiniciado mi memoria. Empecemos de nuevo. ¿Cómo te sientes?")
            return

        if clave == "tablaverdad":
            page.go("/tabla")
            return

        contactar_ollama(mensaje)

    txt_mensaje.on_submit = procesar_envio

    # ----------------
    # FUNCIONES VOZ
    # ----------------f
    def enviar_por_voz(btn_ref=None):
        if btn_ref:
            btn_ref.icon_color = ft.Colors.RED
            btn_ref.update()

        def callback(texto):
            txt_mensaje.value = texto
            page.update()
            
            if btn_ref:
                btn_ref.icon_color = ft.Colors.BLUE_600
                btn_ref.update()
            
            if texto and texto != "No entendí lo que dijiste":
                procesar_envio(None)

        escuchar_google(callback)

    # ----------------
    # TABLA DE VERDAD
    # ----------------
    def procesar_tabla(e):
        formula = txt_tabla.value.strip()
        if not formula:
            return

        tabla_list.controls.append(ft.Text(f"Evaluar: {formula}", weight="bold"))

        resultado = "Error de módulo"
        if modulos_cargados:
            try:
                resultado = str(tablaVerdad.tablaVerdadera(formula))
            except:
                resultado = "Error en cálculo"
        else:
            resultado = "Módulo tablaVerdad no encontrado"

        tabla_list.controls.append(
            ft.Container(
                content=ft.Text(resultado, font_family="Consolas"),
                bgcolor=ft.Colors.YELLOW_100,
                padding=10,
            )
        )
        txt_tabla.value = ""
        page.update()

    def insertar_simbolo(s):
        txt_tabla.value += s
        page.update()

    # ----------------
    # RUTAS Y NAVEGACIÓN
    # ----------------
    def route_change(route):
        page.views.clear()

        # --- HOME VIEW ---
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Container(
                        expand=True,
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=[ft.Colors.BLUE_800, ft.Colors.INDIGO_400],
                        ),
                        content=ft.Column(
                            [
                                ft.Container(
                                    padding=40,
                                    bgcolor=ft.Colors.WHITE,
                                    border_radius=20,
                                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.BLACK12),
                                    content=ft.Column(
                                        [
                                            ft.Container(
                                                content=ft.Icon(ft.Icons.AUTO_AWESOME, size=60, color=ft.Colors.WHITE),
                                                bgcolor=ft.Colors.BLUE_500,
                                                padding=20,
                                                border_radius=50,
                                                alignment=ft.alignment.center,
                                            ),
                                            ft.Divider(height=20, color="transparent"),
                                            ft.Text(spans=[ft.TextSpan("Hola, soy ", ft.TextStyle(size=24, color=ft.Colors.BLACK87)), ft.TextSpan("StressGuard_chat", ft.TextStyle(size=24, weight="bold", color=ft.Colors.BLUE_600))]),
                                            ft.Text("Tu asistente IA (Potenciado por Ollama)", size=14, color=ft.Colors.GREY_500, italic=True),
                                            ft.Divider(height=30, color="transparent"),
                                            ft.ElevatedButton(
                                                content=ft.Row([ft.Icon(ft.Icons.CHAT_BUBBLE, color=ft.Colors.WHITE), ft.Text("Iniciar Chat", size=16, color=ft.Colors.WHITE), ft.Icon(ft.Icons.ARROW_FORWARD, color=ft.Colors.WHITE)], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                                                style=ft.ButtonStyle(bgcolor={"": ft.Colors.BLUE_600}, color={"": ft.Colors.WHITE}, shape=ft.RoundedRectangleBorder(radius=10), padding=20),
                                                width=250,
                                                on_click=lambda _: page.go("/chat")
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=5
                                    )
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center
                    )
                ],
                padding=0,
            )
        )

        # --- CHAT VIEW ---
        if page.route == "/chat":
            # Mostrar mensaje inicial si se abrió automáticamente por señal de estrés
            nonlocal mensaje_inicial_mostrado
            if MODO_APERTURA == 'automatico' and not mensaje_inicial_mostrado:
                mensaje_inicial_mostrado = True
                # Agregar mensaje del sistema
                agregar_mensaje(
                    "⚠️ **He detectado una señal de estrés en tus sensores biométricos.**\n\n"
                    "¿Cómo te encuentras en este momento? Estoy aquí para ayudarte.",
                    usuario=False
                )
            
            btn_microfono = ft.IconButton(
                icon=ft.Icons.MIC,
                icon_color=ft.Colors.BLUE_600,
                on_click=lambda e: enviar_por_voz(btn_microfono) 
            )

            page.views.append(
                ft.View(
                    "/chat",
                    [
                        ft.AppBar(
                            title=ft.Text("Chat con StressGuard_chat"), 
                            bgcolor=ft.Colors.BLUE_600, 
                            color=ft.Colors.WHITE,
                            actions=[btn_voz, ft.Container(width=10)]
                        ),
                        loading,
                        chat_list,
                        ft.Container(
                            padding=10,
                            content=ft.Row(
                                [
                                    txt_mensaje,
                                    btn_microfono, 
                                    ft.IconButton(icon=ft.Icons.SEND, icon_color=ft.Colors.BLUE_600, on_click=procesar_envio),
                                ]
                            )
                        )
                    ]
                )
            )
            if not contexto_ollama:
                agregar_mensaje(
                    "Hola  Soy StressGuard chat.\n\n"
                    "Estoy aquí para escucharte.\n"
                    "¿Cómo te sientes hoy?"
                )

            

        # --- TABLA VIEW ---
        if page.route == "/tabla":
            teclas = ['A', 'B', 'C', '∧', '∨', '~', '→', '↔', '(', ')']
            botones = [ft.ElevatedButton(text=t, on_click=lambda e, x=t: insertar_simbolo(x)) for t in teclas]

            page.views.append(
                ft.View(
                    "/tabla",
                    [
                        ft.AppBar(title=ft.Text("Tabla de Verdad"), bgcolor=ft.Colors.DEEP_PURPLE_500, color=ft.Colors.WHITE),
                        tabla_list,
                        ft.Container(
                            padding=10,
                            content=ft.Column([
                                ft.Row(botones, wrap=True, alignment=ft.MainAxisAlignment.CENTER),
                                ft.Divider(),
                                ft.Row([txt_tabla, ft.ElevatedButton("Calcular", bgcolor=ft.Colors.ORANGE_300, color=ft.Colors.WHITE, on_click=procesar_tabla)]),
                            ])
                        )
                    ]
                )
            )
 


        page.update()

    def view_pop(view):
        page.views.pop()
        page.go(page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/")

if __name__ == "__main__":
    print("🚀 Iniciando aplicación Flet...")
    ft.app(target=main, view=ft.AppView.FLET_APP)