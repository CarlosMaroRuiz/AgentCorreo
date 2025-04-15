# Referencia Rápida: Clases y Métodos del Sistema Multiagente

Esta guía de referencia contiene información detallada sobre las clases y métodos disponibles en el Sistema Multiagente.

## Índice de Clases

1. [Agent](#clase-agent)
2. [Task](#clase-task)
3. [MultiAgentWorkflow](#clase-multiagentworkflow)
4. [AgenteMemoria](#clase-agentememoria)
5. [DeepSeekAPI](#clase-deepseekapi)

---

## Clase `Agent`

Clase base para todos los agentes del sistema, ubicada en `agents/base.py`.

### Constructor

```python
def __init__(self, name, role, goal, backstory, llm)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `name` | `str` | Nombre identificativo del agente |
| `role` | `str` | Rol o función del agente |
| `goal` | `str` | Objetivo principal que persigue |
| `backstory` | `str` | Historia o contexto de fondo |
| `llm` | `LLM` | Instancia del modelo de lenguaje |

### Métodos principales

#### `execute_task`

```python
def execute_task(self, task_description, context=None)
```

Ejecuta una tarea utilizando el LLM asociado al agente.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `task_description` | `str` | Descripción detallada de la tarea |
| `context` | `str` | Contexto adicional (opcional) |
| **Retorna** | `str` | Resultado generado por el LLM |

#### `refinar_objetivo`

```python
def refinar_objetivo(self, tema, contexto=None)
```

Adapta el objetivo del agente para un tema específico.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `tema` | `str` | Tema sobre el que trabajará |
| `contexto` | `str` | Información contextual (opcional) |
| **Retorna** | `str` | Objetivo refinado |

#### `necesita_mas_informacion`

```python
def necesita_mas_informacion(self, resultado)
```

Determina si el agente necesita información adicional para completar su tarea.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `resultado` | `str` | Resultado parcial actual |
| **Retorna** | `str` o `None` | Solicitud de información o `None` si es suficiente |

#### `solicitar_informacion_adicional`

```python
def solicitar_informacion_adicional(self, peticion, contexto)
```

Genera una solicitud formal de información adicional.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `peticion` | `str` | Descripción de lo que se necesita |
| `contexto` | `str` | Contexto actual disponible |
| **Retorna** | `str` | Respuesta con la información solicitada |

### Creación de agentes especializados

```python
# Ejemplo de agente especializado que extiende la clase base
class ResearcherAgent(Agent):
    def __init__(self, llm):
        super().__init__(
            name="Investigador",
            role="Experto en investigación",
            goal="Encontrar información precisa y relevante",
            backstory="Investigador experto en recopilar información valiosa",
            llm=llm
        )
        
    # Opcional: sobrescribir métodos para comportamiento especializado
```

---

## Clase `Task`

Define tareas asignadas a agentes, ubicada en `workflow/task.py`.

### Constructor

```python
def __init__(self, description, agent)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `description` | `str` | Descripción detallada de la tarea |
| `agent` | `Agent` | Agente asignado a la tarea |

### Métodos principales

#### `execute`

```python
def execute(self, context=None)
```

Ejecuta la tarea utilizando el agente asignado.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `context` | `str` | Contexto adicional (opcional) |
| **Retorna** | `str` | Resultado de la ejecución |

### Uso de placeholders

Las tareas pueden referenciar resultados de tareas anteriores:

```python
tarea = Task(
    description="Analiza estos resultados: {task_1}",
    agent=mi_agente
)
```

| Placeholder | Descripción |
|-------------|-------------|
| `{task_1}` | Resultado de la primera tarea |
| `{task_2}` | Resultado de la segunda tarea |
| `{info_adicional_X}` | Información adicional solicitada |

---

## Clase `MultiAgentWorkflow`

Gestiona flujos de trabajo con múltiples agentes, ubicada en `workflow/workflow.py`.

### Constructor

```python
def __init__(self, agents=None, tasks=None)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `agents` | `list` | Lista de agentes (opcional) |
| `tasks` | `list` | Lista de tareas (opcional) |

### Métodos principales

#### `add_agent`

```python
def add_agent(self, agent)
```

Añade un agente al flujo de trabajo.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `agent` | `Agent` | Agente a añadir |

#### `add_task`

```python
def add_task(self, task)
```

Añade una tarea al flujo de trabajo.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `task` | `Task` | Tarea a añadir |

#### `run`

```python
def run(self)
```

Ejecuta todas las tareas secuencialmente.

| **Retorna** | `dict` | Diccionario con los resultados de todas las tareas |

#### `ejecutar_con_retroalimentacion`

```python
def ejecutar_con_retroalimentacion(self)
```

Ejecuta las tareas permitiendo que los agentes soliciten información adicional.

| **Retorna** | `dict` | Diccionario con los resultados de todas las tareas |

#### `ejecutar_tarea_personalizada`

```python
def ejecutar_tarea_personalizada(self, task_index, *args, **kwargs)
```

Ejecuta un método personalizado de un agente específico.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `task_index` | `int` | Índice de la tarea/agente (0-based) |
| `*args` | `any` | Argumentos posicionales para el método |
| `**kwargs` | `any` | Argumentos con nombre para el método |
| `method_name` | `str` | Nombre del método a ejecutar (en kwargs) |
| **Retorna** | `any` | Resultado del método ejecutado |

---

## Clase `AgenteMemoria`

Sistema de memoria para agentes, ubicado en `memory/agente_memoria.py`.

### Constructor

```python
def __init__(self, nombre_agente, archivo_memoria=None)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `nombre_agente` | `str` | Nombre identificativo del agente |
| `archivo_memoria` | `str` | Ruta al archivo de memoria (opcional) |

### Métodos principales

#### `cargar_memoria`

```python
def cargar_memoria(self)
```

Carga la memoria desde un archivo o inicializa una nueva.

| **Retorna** | `dict` | Estructura de datos de la memoria |

#### `guardar_memoria`

```python
def guardar_memoria(self)
```

Guarda la memoria actual en un archivo JSON.

#### `agregar_tarea`

```python
def agregar_tarea(self, descripcion_tarea, resultado, calificacion_exito, tema=None)
```

Almacena el resultado de una tarea ejecutada.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `descripcion_tarea` | `str` | Descripción de la tarea realizada |
| `resultado` | `str` | Resultado obtenido |
| `calificacion_exito` | `int` | Valoración de 1-10 |
| `tema` | `str` | Tema relacionado (opcional) |

#### `obtener_tareas_exitosas_similares`

```python
def obtener_tareas_exitosas_similares(self, descripcion_tarea, tema=None, limite=3)
```

Recupera tareas similares anteriores.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `descripcion_tarea` | `str` | Descripción para buscar similitudes |
| `tema` | `str` | Tema para filtrar (opcional) |
| `limite` | `int` | Número máximo de resultados |
| **Retorna** | `list` | Lista de tareas similares |

### Estructura de datos de memoria

```python
{
    "tareas_previas": [
        {
            "timestamp": "2025-04-14T15:30:22.123456",
            "descripcion": "Investigar sobre IA",
            "muestra_resultado": "La inteligencia artificial es...",
            "calificacion_exito": 9,
            "tema": "Inteligencia Artificial"
        },
        # ...más tareas
    ],
    "resultados_exitosos": [
        # Tareas con calificación >= 8
    ],
    "temas": {
        "Inteligencia Artificial": {
            "contador": 5,
            "exito_promedio": 8.6
        },
        # ...más temas
    }
}
```

---

## Clase `DeepSeekAPI`

Wrapper para la API de DeepSeek, ubicado en `llm/deepseek.py`.

### Constructor

```python
def __init__(self, model="deepseek-chat", temperature=0.7)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `model` | `str` | Nombre del modelo a utilizar |
| `temperature` | `float` | Temperatura para generación (0.0-1.0) |

### Métodos principales

#### `generate`

```python
def generate(self, prompt)
```

Genera texto a partir de un prompt.

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `prompt` | `str` | Instrucción o prompt para el modelo |
| **Retorna** | `str` | Texto generado |

---

## Configuración del Sistema

Archivo `config/settings.py`:

```python
# Ejemplo de configuración
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_TEMPERATURE = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))

# Configuración de email
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Destinatarios predeterminados
DEFAULT_EMAIL_RECIPIENTS = [
    "email1@example.com",
    "email2@example.com"
]
```

---

## Utilidades

### Funciones de email (`utils/email_utils.py`)

```python
def send_email(to, subject, body, is_html=False, smtp_server=None, 
               smtp_port=None, username=None, password=None)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `to` | `str` | Destinatario |
| `subject` | `str` | Asunto del correo |
| `body` | `str` | Contenido del correo |
| `is_html` | `bool` | Indica si el contenido es HTML |
| **Retorna** | `str` | Mensaje de resultado |

### Funciones de procesamiento de texto (`utils/text_processing.py`)

```python
def clean_email_content(email_body)
```

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `email_body` | `str` | Texto del correo a limpiar |
| **Retorna** | `str` | Correo limpio formateado |

---

Esta referencia rápida incluye los detalles técnicos más importantes para trabajar con el Sistema Multiagente. Para más información, consulta los comentarios en el código fuente o la documentación completa del proyecto.