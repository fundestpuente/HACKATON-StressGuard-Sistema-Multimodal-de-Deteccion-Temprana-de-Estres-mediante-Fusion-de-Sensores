# 🚀 StressGuard - Launcher Principal

## Descripción

**Interfaz gráfica centralizada** para acceder a todos los módulos del sistema StressGuard de manera simple e intuitiva.

## ✨ Características

### 🎯 Funcionalidades Principales

1. **Chatbot Manual**
   - Abre el chatbot en modo manual
   - El chatbot NO conoce el estado de estrés inicialmente
   - Útil para conversación libre

2. **Sistema de Detección Completo**
   - Inicia automáticamente el Receptor de Datos
   - Abre el Simulador de Reloj Samsung
   - Cuando se detecte estrés → Chatbot se abre automáticamente
   - Botón para detener todo el sistema

3. **Monitoreo en Tiempo Real**
   - Indicadores visuales del estado del receptor
   - Indicadores visuales del estado del simulador
   - Actualización automática cada 2 segundos

4. **Gestión de Procesos**
   - Control completo de todos los módulos
   - Cierre seguro de procesos al salir
   - Prevención de duplicación

## 🖥️ Interfaz Gráfica

```
┌────────────────────────────────────────┐
│        🏥 StressGuard                  │
│   Sistema Multimodal de Detección     │
├────────────────────────────────────────┤
│                                        │
│  💬 Chatbot Asistente                 │
│  ┌──────────────────────────────────┐ │
│  │ Conversa con StressWard          │ │
│  │ [Abrir Chatbot]                  │ │
│  └──────────────────────────────────┘ │
│                                        │
│  🫀 Sistema de Detección              │
│  ┌──────────────────────────────────┐ │
│  │ Simulador + Detección automática │ │
│  │ [Iniciar Sistema] [Detener]     │ │
│  └──────────────────────────────────┘ │
│                                        │
│  📊 Estado del Sistema                │
│  ┌──────────────────────────────────┐ │
│  │ ● Receptor: Activo/Detenido      │ │
│  │ ● Simulador: Activo/Detenido     │ │
│  └──────────────────────────────────┘ │
│                                        │
│            [Salir]                     │
└────────────────────────────────────────┘
```

## 🚀 Cómo Usar

### Instalación de Dependencias

```bash
pip install psutil flet
```

### Ejecutar el Launcher

```bash
cd HACKATON-StressGuard-Sistema-Multimodal-de-Deteccion-Temprana-de-Estres-mediante-Fusion-de-Sensores
python launcher.py
```

### Uso de Funciones

#### 1️⃣ Abrir Chatbot Manual

1. Clic en **"Abrir Chatbot"**
2. El chatbot se abre en modo manual
3. Puedes conversar libremente
4. El chatbot NO conoce tu estado de estrés

**Casos de uso:**
- Consultas generales
- Probar el chatbot sin sensores
- Conversación sin contexto de estrés

#### 2️⃣ Iniciar Sistema de Detección

1. Clic en **"Iniciar Sistema"**
2. Se inicia automáticamente:
   - Receptor de datos (consola)
   - Simulador de reloj (interfaz web)
3. Ajusta los sliders del simulador
4. Cuando se detecte estrés → Chatbot se abre automáticamente con mensaje inicial
5. El chatbot SÍ conoce que hay una señal de estrés

**Proceso automático:**
```
Launcher → Receptor (background)
        → Simulador (ventana)
        → [Usuario ajusta sensores]
        → Estrés detectado
        → Chatbot se abre automáticamente
```

#### 3️⃣ Detener Sistema

1. Clic en **"Detener"**
2. Cierra todos los procesos activos:
   - Receptor
   - Simulador
3. El chatbot permanece abierto si existe

#### 4️⃣ Salir

1. Clic en **"Salir"**
2. Detiene todos los procesos
3. Cierra el launcher

## 📊 Indicadores de Estado

### 🟢 Verde: Activo
- El proceso está ejecutándose correctamente

### ⚫ Gris: Detenido
- El proceso no está en ejecución

Los indicadores se actualizan automáticamente cada 2 segundos.

## 🔄 Flujo de Trabajo Típico

### Escenario 1: Solo Chatbot
```
1. Ejecutar launcher.py
2. Clic en "Abrir Chatbot"
3. Conversar libremente
```

### Escenario 2: Detección Completa
```
1. Ejecutar launcher.py
2. Clic en "Iniciar Sistema"
3. Esperar que abra el simulador
4. Ajustar sliders para provocar estrés
5. Chatbot se abre automáticamente
6. Conversar sobre el estado de estrés
```

### Escenario 3: Pruebas Múltiples
```
1. Ejecutar launcher.py
2. Iniciar sistema
3. Probar detección de estrés
4. Detener sistema
5. Reiniciar para nuevas pruebas
```

## 🛠️ Arquitectura Técnica

### Gestión de Procesos

El launcher gestiona tres tipos de procesos:

1. **Receptor** (`receptor_datos.py`)
   - Se ejecuta en consola nueva
   - Espera señales de estrés
   - Se mantiene en segundo plano

2. **Simulador** (`simu_reloj.py`)
   - Se ejecuta en navegador (Flet)
   - Interfaz interactiva
   - Envía datos al receptor

3. **Chatbot** (vía `chatbot_manager.py`)
   - Se abre mediante el gestor
   - Control de instancia única
   - Modos: automático/manual

### Control de Instancias

- ✅ Solo una instancia del launcher puede estar abierta
- ✅ Solo una instancia del chatbot puede estar abierta
- ✅ Solo una instancia del simulador puede estar abierta
- ✅ Solo una instancia del receptor puede estar abierta

### Monitoreo

Thread en segundo plano verifica cada 2 segundos:
- Estado del receptor (PID activo)
- Estado del simulador (PID activo)
- Actualiza indicadores visuales

## ⚠️ Solución de Problemas

### El receptor no inicia
- Verificar que el puerto 65432 esté libre
- Cerrar instancias anteriores del receptor

### El simulador no abre
- Verificar que existe `MachineLearning/simu_reloj.py`
- Verificar dependencias instaladas

### El chatbot no se abre automáticamente
- Verificar que `psutil` está instalado
- Verificar que existe `MachineLearning/chatbot_manager.py`
- Revisar consola del receptor para mensajes de error

### Los indicadores no se actualizan
- Normal: hay un delay de hasta 2 segundos
- Si persiste, reiniciar el launcher

## 📝 Notas Importantes

1. **Orden de inicio**: El launcher siempre inicia primero el receptor, luego el simulador
2. **Cierre manual**: Puedes cerrar el simulador/receptor manualmente, los indicadores se actualizarán
3. **Múltiples señales**: Si ya hay un chatbot abierto, nuevas señales no abren duplicados
4. **Reinicio limpio**: Usar "Detener" antes de "Iniciar Sistema" nuevamente

## 🎯 Beneficios del Launcher

✅ **Simplicidad**: Un solo punto de entrada al sistema  
✅ **Visual**: Indicadores claros del estado  
✅ **Automático**: Gestión inteligente de procesos  
✅ **Seguro**: Cierre controlado de todos los módulos  
✅ **Intuitivo**: No requiere conocimientos técnicos  

---

**Desarrollado para**: StressGuard - Hackaton Samsung  
**Fecha**: Diciembre 2025  
**Tecnología**: Python + Flet + Process Management
