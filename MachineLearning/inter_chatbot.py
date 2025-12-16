import flet as ft
import pyttsx3
import threading

# --- IMPORTACIÓN SEGURA DE MÓDULOS EXTERNOS ---
try:
    import aprender
    import tablaVerdad
    modulos_cargados = True
except ImportError:
    print("ADVERTENCIA: No se encontraron 'aprender.py' o 'tablaVerdad.py'. Se usarán respuestas simuladas.")
    modulos_cargados = False

# --- CONFIGURACIÓN DE VOZ (EN HILO SEPARADO) ---
def hablar(texto):
    def _thread_hablar():
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")
            for voice in voices:
                if "spanish" in voice.name.lower() or "es" in voice.languages:
                    engine.setProperty("voice", voice.id)
                    break
            engine.say(texto)
            engine.runAndWait()
        except Exception as e:
            print(f"Error de voz: {e}")

    threading.Thread(target=_thread_hablar, daemon=True).start()

def main(page: ft.Page):
    page.title = "Amaya - Asistente Virtual"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 500
    page.window_height = 700
    page.window_resizable = True

    # --- VARIABLES DE ESTADO ---
    estado = {"aprendiendo": False, "pregunta_previa": ""}

    # --- COMPONENTES REUTILIZABLES ---
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    tabla_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    txt_mensaje = ft.TextField(hint_text="Escribe aquí...", expand=True, autofocus=True)
    txt_tabla = ft.TextField(hint_text="Escribe la proposición...", expand=True)

    # --- FUNCIONES LÓGICAS ---
    def agregar_mensaje_chat(texto, es_usuario=False):
        # CORRECCIÓN: ft.Colors (Mayúscula)
        color_bg = ft.Colors.BLUE_100 if es_usuario else ft.Colors.GREEN_100
        alineacion = ft.MainAxisAlignment.END if es_usuario else ft.MainAxisAlignment.START
        
        # CORRECCIÓN: ft.Icons (Mayúscula)
        icono = ft.Icons.PERSON if es_usuario else ft.Icons.SMART_TOY 

        chat_list.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(icono, size=16), ft.Text("Tú" if es_usuario else "Amaya", weight="bold")], tight=True),
                        ft.Text(texto)
                    ]),
                    bgcolor=color_bg, border_radius=10, padding=10, width=300,
                )
            ], alignment=alineacion)
        )
        page.update()
        if not es_usuario: hablar(texto)

    def procesar_envio(e):
        mensaje = txt_mensaje.value
        if not mensaje.strip(): return
        agregar_mensaje_chat(mensaje, es_usuario=True)
        txt_mensaje.value = ""
        txt_mensaje.focus()
        page.update()

        mensaje_clave = mensaje.lower().strip()
        
        if mensaje_clave == "salir":
            page.window_close()
        elif mensaje_clave == "tablaverdad":
            page.go("/tabla")
        else:
            resp = "No tengo mis módulos de cerebro conectados."
            if modulos_cargados:
                try: resp = aprender.chat_bot(mensaje)
                except: pass
            
            if resp == "falso":
                 resp = "No sé la respuesta (Modo aprendizaje desactivado en ejemplo)"
            
            agregar_mensaje_chat(resp)

    def procesar_tabla(e):
        formula = txt_tabla.value
        if not formula: return
        tabla_list.controls.append(ft.Text(f"Evaluar: {formula}", weight="bold"))
        res = "V F V F"
        if modulos_cargados:
             try: res = str(tablaVerdad.tablaVerdadera(formula))
             except: pass
        
        # CORRECCIÓN: ft.Colors (Mayúscula)
        tabla_list.controls.append(ft.Container(content=ft.Text(res, font_family="Consolas"), bgcolor=ft.Colors.YELLOW_100, padding=10))
        txt_tabla.value = ""
        page.update()

    def insertar_simbolo(simbolo):
        txt_tabla.value += simbolo
        txt_tabla.focus()
        page.update()

    # --- RUTAS Y VISTAS ---
    def route_change(route):
        page.views.clear()
        
        # VISTA 1: HOME
        page.views.append(
            ft.View(
                "/",
                [
                    ft.Column(
                        [
                            # CORRECCIÓN: ft.Icons y ft.Colors (Mayúscula)
                            ft.Icon(ft.Icons.FACE_RETOUCHING_NATURAL, size=100, color=ft.Colors.BLUE),
                            ft.Text("Habla con Amaya", size=30, weight="bold", color=ft.Colors.BLUE),
                            ft.ElevatedButton("Comenzar", on_click=lambda _: page.go("/chat"), height=50, width=200),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True
                    )
                ],
                bgcolor=ft.Colors.LIGHT_BLUE_50
            )
        )

        # VISTA 2: CHAT
        if page.route == "/chat":
            page.views.append(
                ft.View(
                    "/chat",
                    [
                        ft.AppBar(title=ft.Text("Chat con Amaya"), bgcolor=ft.Colors.BLUE_200),
                        chat_list,
                        # CORRECCIÓN: ft.Icons (Mayúscula)
                        ft.Row([txt_mensaje, ft.IconButton(icon=ft.Icons.SEND, on_click=procesar_envio)])
                    ],
                    bgcolor=ft.Colors.WHITE
                )
            )

        # VISTA 3: TABLA
        if page.route == "/tabla":
            teclas = ['A', 'B', 'C', 'D', '∧', '∨', '~', '→', '↔', '(', ')']
            botones_teclado = [ft.ElevatedButton(text=t, on_click=lambda e, x=t: insertar_simbolo(x), width=50) for t in teclas]
            page.views.append(
                ft.View(
                    "/tabla",
                    [
                        ft.AppBar(title=ft.Text("Tabla de Verdad"), bgcolor=ft.Colors.AMBER_200),
                        tabla_list,
                        ft.Container(content=ft.Row(controls=botones_teclado, wrap=True, alignment=ft.MainAxisAlignment.CENTER), padding=10, bgcolor=ft.Colors.GREY_100),
                        ft.Row([txt_tabla, ft.ElevatedButton("Calcular", on_click=procesar_tabla)])
                    ]
                )
            )
        
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    page.go("/")

ft.app(target=main)