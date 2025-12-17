import flet as ft
import pyttsx3
import threading
import speech_recognition as sr
import requests 
import json
import time


# ================================
# IMPORTACIÓN DE PROMPTS Y MÓDULOS
# ================================
try:
    import prompts  # Importamos el archivo con los dos prompts
    print("Prompts cargados correctamente.")
except ImportError:
    prompts = None
    print("Advertencia: No se encontró prompts.py")

try:
    import aprender
    import tablaVerdad
    modulos_cargados = True
except ImportError:
    modulos_cargados = False

# ================================
# CONFIGURACIÓN OLLAMA
# ================================
MODELO_OLLAMA = "llama3.2" 

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
    contexto_ollama = []
    
    # Variable para controlar la voz (Audio)
    voz_activa = True 

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
    # INTEGRACIÓN CON OLLAMA + ROUTER PATTERN
    # -----------------------------------------------
    # -----------------------------------------------
    def iniciativa_bot():
        if time.time() - ultima_interaccion > 12:
            agregar_mensaje(
                "Sigo aquí contigo 🙂\n\n"
                "¿Quieres contarme un poco más sobre cómo te sientes "
                "o prefieres que te ayude con algo específico?"
            )

    # INTEGRACIÓN CON OLLAMA + ROUTER PATTERN (CON STREAMING)
    # -----------------------------------------------
    def contactar_ollama(prompt_usuario):
        def _request():
            nonlocal contexto_ollama
            nonlocal modo_guia_activo
            
            # 1. Preparamos la interfaz
            loading.visible = True
            page.update()

            # LÓGICA DEL ROUTER (Igual que antes)
            instrucciones_sistema = ""
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
                    instrucciones_sistema = getattr(prompts, 'PROMPT_GUIA', "")
                else:
                    print("Router: Usando PROMPT_CHARLA")
                    instrucciones_sistema = getattr(prompts, 'PROMPT_CHARLA', "")

            url = "http://localhost:11434/api/generate"
            
            data = {
                "model": MODELO_OLLAMA,
                "prompt": prompt_usuario,
                "system": instrucciones_sistema,
                "context": contexto_ollama,
                "stream": True  # <--- ACTIVAMOS STREAMING
            }

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
                                        ft.Row([ft.Icon(ft.Icons.SMART_TOY, size=16), ft.Text("StressGuard_chat", weight="bold")], tight=True),
                                        texto_markdown, # Aquí se escribirá el texto
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
                page.update() # Mostramos la burbuja vacía

                # 3. Petición con Streaming
                with requests.post(url, json=data, stream=True) as response:
                    if response.status_code == 200:
                        for line in response.iter_lines():
                            if line:
                                json_part = json.loads(line.decode('utf-8'))
                                palabra = json_part.get("response", "")
                                
                                # Si es el final, guardamos el contexto
                                if json_part.get("done"):
                                    contexto_ollama = json_part.get("context", [])
                                
                                # Actualizamos el texto poco a poco
                                respuesta_acumulada += palabra
                                texto_markdown.value = respuesta_acumulada
                                texto_markdown.update() # Actualizamos SOLO el texto (más rápido)
                        
                        # Al finalizar, hablamos todo el texto si la voz está activa
                        if voz_activa:
                            hablar(respuesta_acumulada)
                    else:
                        texto_markdown.value = f"Error: {response.status_code}"
                        texto_markdown.update()

            except Exception as e:
                agregar_mensaje(f"Error de conexión: {e}")
            
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
        if clave == "borrar memoria":
            nonlocal contexto_ollama, modo_guia_activo
            contexto_ollama = []
            modo_guia_activo = False # Reiniciamos también el modo
            agregar_mensaje("He olvidado nuestra conversación y reiniciado mi estado.")
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
    ft.app(target=main)