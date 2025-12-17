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
import re
import difflib
import unicodedata

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

# Variable global para controlar el warning de voz
_voz_español_advertido = False

def hablar(texto):
    """
    Convierte texto a voz usando pyttsx3
    Intenta usar voz en español si está disponible
    """
    def _hablar():
        global _voz_español_advertido
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Velocidad de habla
            
            # Obtener todas las voces disponibles
            voices = engine.getProperty("voices")
            voz_español_encontrada = False
            
            # Intentar encontrar una voz en español
            for v in voices:
                # Buscar en diferentes lugares
                nombre_lower = v.name.lower()
                id_lower = v.id.lower()
                lang_str = str(v.languages).lower() if v.languages else ""
                
                # Palabras clave para detectar español
                palabras_español = ['spanish', 'español', 'espanol', 'es-', 'es_', 
                                   'sabina', 'helena', 'laura', 'pablo', 'raul']
                
                if any(palabra in nombre_lower or palabra in id_lower or palabra in lang_str 
                       for palabra in palabras_español):
                    engine.setProperty("voice", v.id)
                    voz_español_encontrada = True
                    print(f"🔊 Usando voz: {v.name}")
                    break
            
            # Si no se encontró voz en español, advertir una sola vez
            if not voz_español_encontrada and not _voz_español_advertido:
                print("⚠️ ADVERTENCIA: No se encontró voz en español instalada.")
                print("   Se usará la voz por defecto del sistema (inglés).")
                print("   Para instalar voces en español:")
                print("   - Windows: Configuración > Hora e idioma > Voz > Agregar voces")
                print("   - O desactiva la voz con el botón 🔊 en el chat")
                _voz_español_advertido = True
            
            # Reproducir el texto
            engine.say(texto)
            engine.runAndWait()
            
        except Exception as e:
            print(f"❌ Error TTS: {e}")

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
    # Por defecto: desactivada; el usuario la activa manualmente.
    voz_activa = False
    
    # Variable para controlar si ya se mostró el mensaje inicial
    mensaje_inicial_mostrado = False
    
    # Variable para el Router Pattern (Controla qué Prompt usar)
    modo_guia_activo = False

    # ----------------
    # FLUJO DETERMINÍSTICO DE TESTS
    # ----------------
    ultima_sugerencia_test = None  # "menu" | None
    test_state = {
        "activo": False,
        "tipo": None,
        "indice": 0,
        "respuestas": [],
    }

    NOMBRE_TEST_PSS14 = "PSS-14 (estrés percibido, 14 ítems)"
    NOMBRE_TEST_FISIO = "Test de análisis fisiológico (5 ítems)"

    PSS14_PREGUNTAS = [
        "1) En el último mes, ¿con qué frecuencia te has sentido afectado/a por algo que ocurrió inesperadamente?",
        "2) En el último mes, ¿con qué frecuencia te has sentido incapaz de controlar las cosas importantes en tu vida?",
        "3) En el último mes, ¿con qué frecuencia te has sentido nervioso/a o estresado/a?",
        "4) En el último mes, ¿con qué frecuencia has manejado con éxito los pequeños problemas irritantes de la vida?",
        "5) En el último mes, ¿con qué frecuencia has sentido que has afrontado efectivamente los cambios importantes que han estado ocurriendo en tu vida?",
        "6) En el último mes, ¿con qué frecuencia has estado seguro/a sobre tu capacidad para manejar tus problemas personales?",
        "7) En el último mes, ¿con qué frecuencia has sentido que las cosas van bien?",
        "8) En el último mes, ¿con qué frecuencia has sentido que no podías afrontar todas las cosas que tenías que hacer?",
        "9) En el último mes, ¿con qué frecuencia has podido controlar las dificultades de tu vida?",
        "10) En el último mes, ¿con qué frecuencia has sentido que tenías todo bajo control?",
        "11) En el último mes, ¿con qué frecuencia has estado enfadado/a porque las cosas que te han ocurrido estaban fuera de tu control?",
        "12) En el último mes, ¿con qué frecuencia has pensado sobre las cosas que te faltan por hacer?",
        "13) En el último mes, ¿con qué frecuencia has podido controlar la forma de pasar el tiempo?",
        "14) En el último mes, ¿con qué frecuencia has sentido que las dificultades se acumulan tanto que no puedes superarlas?",
    ]
    # Ítems positivos (invertidos) en PSS-14 (1-indexados)
    # Según el PDF: ítems 4,5,6,7,9,10 y 13 se puntúan invertidos
    PSS14_INVERTIDOS = {4, 5, 6, 7, 9, 10, 13}

    FISIO_PREGUNTAS = [
        "1) En los últimos 7 días, ¿qué tanto se ha visto afectado tu sueño (dificultad para dormir o dormir mal)?",
        "2) En los últimos 7 días, ¿qué tanta tensión muscular has sentido (cuello, mandíbula, espalda)?",
        "3) En los últimos 7 días, ¿con qué intensidad has notado palpitaciones o respiración agitada por nervios?",
        "4) En los últimos 7 días, ¿qué tan frecuentes han sido los dolores de cabeza relacionados con estrés?",
        "5) En los últimos 7 días, ¿qué tanto has tenido molestias digestivas asociadas a nervios/estrés?",
    ]

    def _norm(s: str) -> str:
        return (s or "").strip().lower()

    def _detectar_seleccion_test(mensaje: str):
        t = _norm(mensaje)
        if any(k in t for k in ["pss", "14", "estrés percibido", "estres percibido", "percido", "percibido"]):
            return "pss14"
        if any(k in t for k in ["análisis fisiológico", "analisis fisiologico", "fisiológico", "fisiologico", "síntomas", "sintomas", "5", "señales corporales", "senales corporales", "test fisico", "test físico", "físico", "fisico"]):
            return "fisio"
        return None

    def _detectar_sugerencia_tests_en_respuesta(respuesta: str) -> bool:
        r = _norm(respuesta)
        return any(k in r for k in [
            "pss", "pss-14", "estrés percibido", "estres percibido", "14 ítems", "14 items",
            "análisis fisiológico", "analisis fisiologico", "síntomas", "sintomas", "test físico", "test fisico", "5 ítems", "5 items",
            "te sugiero", "te recomiendo", "test",
        ])

    def _mensaje_opciones(tipo: str) -> str:
        return "Selecciona una opción (botón) o escribe una frase; la interpretaré."

    def _sin_acentos(s: str) -> str:
        s = s or ""
        return "".join(
            c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
        )

    def _similitud(a: str, b: str) -> float:
        a2 = _sin_acentos(_norm(a))
        b2 = _sin_acentos(_norm(b))
        if not a2 or not b2:
            return 0.0
        return difflib.SequenceMatcher(None, a2, b2).ratio()

    def _labels_por_tipo(tipo: str):
        if tipo == "pss14":
            return {
                0: "Nunca",
                1: "Casi nunca",
                2: "De vez en cuando",
                3: "A menudo",
                4: "Muy a menudo",
            }
        return {
            0: "Nada",
            1: "Leve",
            2: "Moderado",
            3: "Alto",
        }

    def _frases_por_opcion(tipo: str):
        if tipo == "pss14":
            return {
                0: ["nunca", "jamas", "jamás", "para nada", "en absoluto"],
                1: ["casi nunca", "rara vez", "raras veces", "muy pocas veces", "pocas veces"],
                2: ["de vez en cuando", "de vez en vez", "ocasionalmente", "a veces", "algunas veces"],
                3: ["a menudo", "frecuentemente", "con frecuencia", "seguido", "muchas veces"],
                4: ["muy a menudo", "muy frecuentemente", "casi siempre", "siempre", "todo el tiempo"],
            }
        return {
            0: ["nada", "para nada", "ninguno", "ninguna", "cero", "sin"],
            1: ["leve", "ligero", "ligera", "poco", "bajo"],
            2: ["moderado", "medio", "media", "regular"],
            3: ["alto", "muy alto", "fuerte", "intenso", "intensa", "severo", "severa"],
        }

    def _probabilidades_opciones(tipo: str, texto: str):
        t = _sin_acentos(_norm(texto))
        labels = _labels_por_tipo(tipo)
        frases = _frases_por_opcion(tipo)

        scores = []
        for valor, label in labels.items():
            best = 0.0
            for f in frases.get(valor, []):
                f2 = _sin_acentos(_norm(f))
                s = _similitud(t, f2)
                if f2 and f2 in t:
                    s = max(s, 0.9)
                best = max(best, s)
            scores.append((valor, label, 0.05 + best))

        total = sum(s for _, _, s in scores) or 1.0
        probs = [(v, l, s / total) for v, l, s in scores]
        probs.sort(key=lambda x: x[2], reverse=True)
        return probs

    def _extraer_valor_desde_texto(tipo: str, texto: str):
        t = _norm(texto)

        # 1) Intentar extraer un número válido dentro del texto
        #    - PSS-14 usa 0–4 (si el usuario responde 1–5, se convierte a 0–4)
        #    - Fisiológico usa 0–3
        nums = re.findall(r"\d+", t)
        for ns in nums:
            try:
                n = int(ns)
            except ValueError:
                continue

            if tipo == "pss14":
                if 0 <= n <= 4:
                    return n
                if 1 <= n <= 5:
                    return n - 1
            else:
                if 0 <= n <= 3:
                    return n

        # 2) Mapear texto libre a valores (sinónimos)
        if tipo == "pss14":
            equivalencias = [
                (4, ["muy a menudo", "muy seguido", "muy frecuentemente", "casi siempre", "siempre"]),
                (3, ["a menudo", "seguido", "frecuentemente", "con frecuencia", "muchas veces"]),
                (2, ["de vez en cuando", "de vez en vez", "ocasionalmente", "a veces", "algunas veces"]),
                (1, ["casi nunca", "rara vez", "raras veces", "muy pocas veces", "pocas veces"]),
                (0, ["nunca", "jamás", "jamas"]),
            ]
        else:
            equivalencias = [
                (3, ["alto", "muy alto", "fuerte", "intenso", "intensa"]),
                (2, ["moderado", "media", "medio", "regular"]),
                (1, ["leve", "bajo", "ligero", "ligera", "poco"]),
                (0, ["nada", "ninguno", "ninguna", "para nada"]),
            ]

        for v, frases in equivalencias:
            for f in frases:
                if f in t:
                    return v
        return None

    def _registrar_respuesta_test(valor: int):
        if not test_state["activo"]:
            return
        tipo = test_state["tipo"]

        if tipo == "pss14" and (valor < 0 or valor > 4):
            agregar_mensaje("Valor fuera de rango. " + _mensaje_opciones(tipo))
            return
        if tipo == "fisio" and (valor < 0 or valor > 3):
            agregar_mensaje("Valor fuera de rango. " + _mensaje_opciones(tipo))
            return

        test_state["respuestas"].append(valor)
        test_state["indice"] += 1

        preguntas = PSS14_PREGUNTAS if tipo == "pss14" else FISIO_PREGUNTAS
        if test_state["indice"] >= len(preguntas):
            _finalizar_test()
        else:
            _enviar_pregunta_actual()

    def _seleccionar_opcion_test(valor: int, label: str):
        # Mostrar el enunciado elegido (no el número)
        agregar_mensaje(label, usuario=True)
        _registrar_respuesta_test(valor)

    def _botones_opciones_test(tipo: str) -> ft.Control:
        if tipo == "pss14":
            opciones = [
                (0, "Nunca"),
                (1, "Casi nunca"),
                (2, "De vez en cuando"),
                (3, "A menudo"),
                (4, "Muy a menudo"),
            ]
        else:
            opciones = [
                (0, "Nada"),
                (1, "Leve"),
                (2, "Moderado"),
                (3, "Alto"),
            ]

        botones = [
            ft.ElevatedButton(text=label, on_click=lambda e, vv=v, ll=label: _seleccionar_opcion_test(vv, ll))
            for v, label in opciones
        ]
        return ft.Row(botones, alignment=ft.MainAxisAlignment.CENTER, wrap=True)

    def _enviar_pregunta_actual():
        if not test_state["activo"] or not test_state["tipo"]:
            return
        tipo = test_state["tipo"]
        idx = test_state["indice"]

        preguntas = PSS14_PREGUNTAS if tipo == "pss14" else FISIO_PREGUNTAS
        if idx < 0 or idx >= len(preguntas):
            return
        nombre = NOMBRE_TEST_PSS14 if tipo == "pss14" else NOMBRE_TEST_FISIO
        pregunta = preguntas[idx]
        # Evitar que Markdown interprete "1)" como lista y rompa el formato
        m = re.match(r"^\s*\d+\s*[\)\.-:]\s*(.*)$", pregunta)
        if m:
            pregunta = m.group(1).strip()

        total = len(preguntas)
        texto_pregunta = (
            f"**Pregunta {idx + 1}/{total}:** {pregunta}\n\n"
            + "Selecciona una opción (o escribe el número)."
        )
        agregar_mensaje(
            texto_pregunta,
            usuario=False,
            acciones=_botones_opciones_test(tipo),
        )

    def _iniciar_test(tipo: str):
        nonlocal ultima_sugerencia_test
        test_state["activo"] = True
        test_state["tipo"] = tipo
        test_state["indice"] = 0
        test_state["respuestas"] = []
        ultima_sugerencia_test = None
        _enviar_pregunta_actual()

    def _interpretar_resultado_pss14(puntaje: int) -> str:
        # Rangos orientativos según el PDF adjunto
        # Moderado: 20 a 25; por encima se considera elevado.
        if puntaje < 20:
            nivel = "BAJO"
        elif puntaje <= 25:
            nivel = "MODERADO"
        else:
            nivel = "ELEVADO"
        return f"Puntaje total: **{puntaje} / 56** → nivel orientativo: **{nivel}** (moderado: 20–25)."

    def _interpretar_resultado_fisico(puntaje: int) -> str:
        if puntaje <= 4:
            nivel = "BAJO"
        elif puntaje <= 9:
            nivel = "MODERADO"
        else:
            nivel = "ALTO"
        return f"Puntaje total: **{puntaje} / 15** → nivel orientativo: **{nivel}**."

    def _finalizar_test():
        tipo = test_state["tipo"]
        if tipo == "pss14":
            # Invertir ítems positivos
            puntajes = []
            for i, val in enumerate(test_state["respuestas"], start=1):
                if i in PSS14_INVERTIDOS:
                    puntajes.append(4 - val)
                else:
                    puntajes.append(val)
            total = sum(puntajes)
            resumen = _interpretar_resultado_pss14(total)
        else:
            total = sum(test_state["respuestas"])
            resumen = _interpretar_resultado_fisico(total)

        agregar_mensaje(
            f"✅ **Test completado**\n\n{resumen}\n\n"
            "Esto es una orientación general, no un diagnóstico. Si quieres, cuéntame qué parte te preocupa más y te propongo 1-2 pasos prácticos."
        )

        test_state["activo"] = False
        test_state["tipo"] = None
        test_state["indice"] = 0
        test_state["respuestas"] = []

    # ----------------
    # COMPONENTES GLOBALES
    # ----------------
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    tabla_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)

    txt_mensaje = ft.TextField(hint_text="Escribe o habla...", expand=True)
    txt_tabla = ft.TextField(hint_text="Proposición lógica", expand=True)
    
    loading = ft.ProgressBar(width=None, color=ft.Colors.BLUE, visible=False)

    def _wrap_selectable(control: ft.Control) -> ft.Control:
        selection_area = getattr(ft, "SelectionArea", None)
        if selection_area:
            return selection_area(content=control)
        return control

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
        icon=ft.Icons.VOLUME_UP if voz_activa else ft.Icons.VOLUME_OFF,
        tooltip="Desactivar voz" if voz_activa else "Activar voz",
        icon_color=ft.Colors.WHITE,
        on_click=toggle_voz
    )

    # ----------------
    # FUNCIONES CHAT
    # ----------------
    def agregar_mensaje(texto, usuario=False, acciones: ft.Control | None = None):
        nonlocal ultima_interaccion
        ultima_interaccion = time.time()  # ← registra interacción

        color = ft.Colors.BLUE_100 if usuario else ft.Colors.GREEN_100
        icono = ft.Icons.PERSON if usuario else ft.Icons.SMART_TOY
        alineacion = ft.MainAxisAlignment.END if usuario else ft.MainAxisAlignment.START

        contenido = [
            ft.Row(
                [
                    ft.Icon(icono, size=16),
                    ft.Text("Tú" if usuario else "StressGuard_chat", weight="bold"),
                ],
                tight=True,
            ),
            _wrap_selectable(ft.Markdown(texto, extension_set="gitHubWeb")),
        ]
        if (not usuario) and acciones is not None:
            contenido.append(acciones)

        chat_list.controls.append(
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            contenido
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
            nonlocal ultima_sugerencia_test
            
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
                acciones_tests = ft.Row(
                    [
                        ft.ElevatedButton(
                            text="PSS-14",
                            on_click=lambda e: _iniciar_test("pss14"),
                        ),
                        ft.ElevatedButton(
                            text="Test de análisis fisiológico",
                            on_click=lambda e: _iniciar_test("fisio"),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    visible=False,
                )
                
                # Agregamos la burbuja visual al chat INMEDIATAMENTE
                chat_list.controls.append(
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Row([ft.Icon(ft.Icons.SMART_TOY, size=16), ft.Text("StressWard", weight="bold")], tight=True),
                                        _wrap_selectable(texto_markdown),
                                        acciones_tests,
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

                # Si el bot recomendó tests, reemplazar por texto conciso + botones (UX requerida)
                if _detectar_sugerencia_tests_en_respuesta(respuesta_acumulada):
                    ultima_sugerencia_test = "menu"
                    texto_markdown.value = (
                        "Lamento que estés pasando por un momento difícil. "
                        "Puedo ayudarte brindándote unos tests que te permitirán medir tu nivel de estrés.\n\n"
                        "Elige una opción:"
                    )
                    texto_markdown.update()
                    acciones_tests.visible = True
                    acciones_tests.update()
                
                # Al finalizar, hablamos el texto final mostrado
                if voz_activa:
                    hablar(texto_markdown.value or respuesta_acumulada)

            except Exception as e:
                print(f"❌ Error al contactar Ollama: {e}")
                texto_markdown.value = f"Error de conexión: {e}"
                texto_markdown.update()
            
            loading.visible = False
            page.update()

        threading.Thread(target=_request, daemon=True).start()

    def procesar_envio(e):
        nonlocal contexto_ollama, modo_guia_activo, ultima_sugerencia_test
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

        # Información de tests (tiempo, intención, propósito)
        if any(k in clave for k in ["qué es", "que es", "en qué consiste", "en que consiste", "para qué", "para que", "tiempo", "cuánto dura", "cuanto dura"]) and any(
            t in clave for t in ["pss", "pss-14", "estrés percibido", "estres percibido", "análisis fisiológico", "analisis fisiologico", "fisiológico", "fisiologico", "test físico", "test fisico", "síntomas", "sintomas"]
        ):
            if any(t in clave for t in ["pss", "pss-14", "estrés percibido", "estres percibido"]):
                agregar_mensaje(
                    f"**{NOMBRE_TEST_PSS14}**\n\n"
                    "- Tiempo estimado: 3–6 minutos (14 respuestas).\n"
                    "- Intención: medir tu percepción de control y sobrecarga en el último mes.\n"
                    "- Propósito: darte un nivel orientativo de estrés (bajo/moderado/alto) según el puntaje total.\n\n"
                    "Si quieres iniciarlo, escribe **PSS-14** o presiona el botón cuando aparezca."
                )
            else:
                agregar_mensaje(
                    f"**{NOMBRE_TEST_FISIO}**\n\n"
                    "- Tiempo estimado: 1–2 minutos (5 respuestas).\n"
                    "- Intención: identificar señales corporales frecuentes asociadas al estrés.\n"
                    "- Propósito: darte un indicador orientativo de carga fisiológica relacionada con estrés.\n\n"
                    "Si quieres iniciarlo, escribe **análisis fisiológico** o presiona el botón cuando aparezca."
                )
            return

        # Cancelar test
        if clave in ["cancelar", "cancelar test", "salir test", "detener"] and test_state["activo"]:
            test_state["activo"] = False
            test_state["tipo"] = None
            test_state["indice"] = 0
            test_state["respuestas"] = []
            agregar_mensaje("🛑 Test cancelado. Si quieres, dime qué te preocupa y te sugiero el test adecuado.")
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

        # Si hay un test activo, interpretar respuesta y avanzar (botón o texto)
        if test_state["activo"]:
            tipo = test_state["tipo"]
            valor = _extraer_valor_desde_texto(tipo, mensaje)
            if valor is None:
                probs = _probabilidades_opciones(tipo, mensaje)
                (v1, l1, p1) = probs[0]
                (v2, l2, p2) = probs[1] if len(probs) > 1 else (None, None, 0.0)

                # Solo pedir que elija de nuevo cuando haya ambigüedad alta entre dos opciones
                # (probabilidades cercanas y ambas relativamente altas)
                es_ambigua = (p2 >= 0.30) and ((p1 - p2) <= 0.12)

                if es_ambigua and v2 is not None:
                    acciones_2 = ft.Row(
                        [
                            ft.ElevatedButton(text=l1, on_click=lambda e, vv=v1, ll=l1: _seleccionar_opcion_test(vv, ll)),
                            ft.ElevatedButton(text=l2, on_click=lambda e, vv=v2, ll=l2: _seleccionar_opcion_test(vv, ll)),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        wrap=True,
                    )
                    agregar_mensaje(
                        "Tu frase se parece a dos opciones. ¿Cuál describe mejor tu caso?\n\n"
                        f"- {l1}\n"
                        f"- {l2}",
                        usuario=False,
                        acciones=acciones_2,
                    )
                    return

                # Si no es ambigua, asociar automáticamente a la opción con mayor probabilidad
                agregar_mensaje(f"Interpreté tu respuesta como: **{l1}**.")
                _registrar_respuesta_test(v1)
                return

            # Si el usuario escribió una frase (no un número), mostrar cómo se interpretó
            if not re.fullmatch(r"\s*\d+\s*", mensaje or ""):
                probs = _probabilidades_opciones(tipo, mensaje)
                labels = _labels_por_tipo(tipo)
                prob_sel = next((p for v, _, p in probs if v == valor), None)
                label_sel = labels.get(valor, str(valor))
                if prob_sel is not None:
                    agregar_mensaje(f"Interpreté tu respuesta como: **{label_sel}**.")

            _registrar_respuesta_test(valor)
            return

        # Selección explícita de test
        seleccionado = _detectar_seleccion_test(mensaje)
        if seleccionado:
            _iniciar_test(seleccionado)
            return

        # Aceptación simple si el bot sugirió un test previamente
        if ultima_sugerencia_test == "menu" and clave in ["si", "sí", "ok", "vale", "de acuerdo", "vamos", "empecemos", "listo"]:
            agregar_mensaje("Perfecto. Elige una opción: escribe **PSS-14** o **análisis fisiológico** (o usa los botones).")
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
                    "Hola, soy StressGuard_chat.\n\n"
                    "Estoy aquí para ayudarte a identificar posibles causas de tu malestar emocional.\n"
                    "Cuéntame: ¿qué es lo que más te preocupa o te está afectando ahora mismo?"
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
    page.go("/chat")

if __name__ == "__main__":
    print("🚀 Iniciando aplicación Flet...")
    ft.app(target=main, view=ft.AppView.FLET_APP)