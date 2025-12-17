# 🤖 Sistema de Apertura Inteligente del Chatbot

## 📝 Descripción

Sistema que abre automáticamente el chatbot **StressWard** cuando se detecta estrés en los sensores biométricos, con control de instancia única para evitar duplicación.

## ✨ Características Implementadas

### 1. **Control de Instancia Única**
- ✅ Solo una instancia del chatbot puede estar abierta a la vez
- ✅ Previene duplicación de ventanas cuando llegan múltiples señales de estrés
- ✅ Si se cierra y llega nueva señal, se vuelve a abrir automáticamente

### 2. **Dos Modos de Apertura**

#### 🔴 Modo Automático (Señal de Estrés)
- Se activa cuando el reloj Samsung detecta estrés
- El chatbot inicia la conversación con un mensaje:
  > ⚠️ **He detectado una señal de estrés en tus sensores biométricos.**
  > ¿Cómo te encuentras en este momento? Estoy aquí para ayudarte.

#### 🟢 Modo Manual (Usuario)
- Se activa cuando el usuario abre el chatbot manualmente
- Comportamiento estándar: espera a que el usuario inicie la conversación

## 📁 Archivos Modificados/Creados

### Nuevos Archivos
1. **`MachineLearning/chatbot_manager.py`**
   - Gestor principal del chatbot
   - Control de instancia única mediante archivo de bloqueo
   - Funciones para abrir chatbot en modo automático o manual

2. **`MachineLearning/requirements.txt`**
   - Dependencias necesarias (incluye `psutil`)

### Archivos Modificados
1. **`Chatbot/inter_chatbot.py`**
   - Detección del modo de apertura (`--modo=automatico` o `--modo=manual`)
   - Mensaje inicial automático cuando se abre por señal de estrés
   - Limpieza del archivo de bloqueo al cerrar

2. **`MachineLearning/receptor_datos.py`**
   - Integración con el gestor de chatbot
   - Apertura automática al recibir señal de estrés

## 🚀 Flujo de Funcionamiento

```
┌─────────────────────┐
│ simu_reloj.py       │  1. Detecta estrés
│ (Reloj Samsung)     │     en sensores
└──────────┬──────────┘
           │ Envía datos
           ▼
┌─────────────────────┐
│ receptor_datos.py   │  2. Recibe alerta
│                     │     de estrés
└──────────┬──────────┘
           │ Llama a
           ▼
┌─────────────────────┐
│ chatbot_manager.py  │  3. Verifica si ya
│                     │     hay instancia
└──────────┬──────────┘
           │
           ├─ SÍ existe ──→ No hace nada
           │
           └─ NO existe ─→ Abre chatbot
                           con --modo=automatico
                                   │
                                   ▼
                          ┌─────────────────────┐
                          │ inter_chatbot.py    │
                          │ Modo: AUTOMÁTICO    │
                          │ Mensaje inicial: SÍ │
                          └─────────────────────┘
```

## 🛠️ Instalación

1. Instalar dependencias:
```bash
pip install -r MachineLearning/requirements.txt
```

2. Asegurarse de que Ollama esté ejecutándose con el modelo `llama3.2`

## 📋 Instrucciones de Uso

### Prueba del Sistema Completo

1. **Iniciar el receptor de datos:**
```bash
cd MachineLearning
python receptor_datos.py
```

2. **Iniciar el simulador del reloj:**
```bash
cd MachineLearning
python simu_reloj.py
```

3. **Provocar estrés:**
   - Ajustar los sliders en el simulador para generar una predicción de estrés
   - El chatbot se abrirá automáticamente

4. **Probar prevención de duplicación:**
   - Con el chatbot abierto, generar más señales de estrés
   - Verificar que no se abran ventanas adicionales

5. **Probar reapertura:**
   - Cerrar el chatbot
   - Generar nueva señal de estrés
   - Verificar que se vuelva a abrir

### Prueba del Gestor (Standalone)

```bash
cd MachineLearning
python chatbot_manager.py
```

Esto ejecutará pruebas automáticas del gestor.

## 🔧 Funciones Principales

### En `chatbot_manager.py`:

- **`esta_chatbot_ejecutandose()`**: Verifica si hay una instancia activa
- **`abrir_chatbot(modo='manual')`**: Abre el chatbot en el modo especificado
- **`abrir_chatbot_por_estres()`**: Atajo para modo automático
- **`abrir_chatbot_manual()`**: Atajo para modo manual
- **`limpiar_lock()`**: Limpia el archivo de bloqueo

### En `inter_chatbot.py`:

- Detecta `--modo=automatico` o `--modo=manual` al inicio
- Muestra mensaje inicial solo en modo automático
- Limpia archivo de bloqueo al cerrar (`atexit`)

## 📌 Notas Técnicas

- **Archivo de bloqueo**: `.chatbot_instance.lock` (contiene el PID del proceso)
- **Ubicación**: `MachineLearning/.chatbot_instance.lock`
- **Proceso independiente**: El chatbot se ejecuta como proceso separado
- **Limpieza automática**: El archivo de bloqueo se elimina al cerrar el chatbot

## ⚠️ Posibles Problemas y Soluciones

### El chatbot no se abre
- Verificar que existe `Chatbot/inter_chatbot.py`
- Verificar que `psutil` está instalado
- Revisar la consola de `receptor_datos.py` para mensajes de error

### Se abren múltiples instancias
- Eliminar manualmente `.chatbot_instance.lock` si existe
- Reiniciar los procesos

### El chatbot no muestra mensaje inicial
- Verificar que se está pasando `--modo=automatico` correctamente
- Revisar la consola del chatbot para el mensaje de modo

## 📊 Estado de Implementación

- ✅ Tarea 1: Crear módulo gestor de chatbot
- ✅ Tarea 2: Implementar control de instancia única
- ✅ Tarea 3: Modificar inter_chatbot.py para modo automático/manual
- ✅ Tarea 4: Integrar gestor en receptor_datos.py
- ✅ Tarea 5: Agregar mensaje inicial según modo
- ⏳ Tarea 6: Pruebas del sistema completo (pendiente de ejecutar)

---

**Desarrollado para**: StressGuard - Sistema Multimodal de Detección Temprana de Estrés
**Fecha**: Diciembre 2025
