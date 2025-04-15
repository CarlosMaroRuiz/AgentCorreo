# Guía de Usuario: Sistema Multiagente

Esta guía explica cómo utilizar el Sistema Multiagente para crear flujos de trabajo inteligentes basados en LLMs con agentes que colaboran entre sí.

## 🌟 Resultados obtenidos

El sistema multiagente ha demostrado buenos resultados en la generación de contenidos profesionales. A continuación se muestran algunos ejemplos:

### Correos HTML personalizados

El sistema genera correos electrónicos con diseño HTML personalizado según el tema tratado, con un formato profesional y atractivo.

![Resultado de correo generado](/img/resultado.jpeg)

### Integración con Telegram

El sistema también funciona como un bot de Telegram, permitiendo a los usuarios generar correos desde cualquier dispositivo de forma conversacional.

![Interacción con el bot de Telegram](/img/telegram1.jpg)

![Resultado del bot de Telegram](/img/telegram2.jpeg)

## 📚 Índice

1. [Instalación](#instalación)
2. [Componentes básicos](#componentes-básicos)
3. [Creando agentes](#creando-agentes)
4. [Definiendo tareas](#definiendo-tareas)
5. [Configurando el flujo de trabajo](#configurando-el-flujo-de-trabajo)
6. [Sistema de memoria](#sistema-de-memoria)
7. [Ejemplos prácticos](#ejemplos-prácticos)
8. [Solución de problemas](#solución-de-problemas)

## 📥 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/CarlosMaroRuiz/AgentCorreo.git
cd AgentCorreo

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu editor favorito
```

Asegúrate de configurar las siguientes variables en el archivo `.env`:
- `DEEPSEEK_API_KEY`: Tu clave de API para DeepSeek
- `EMAIL_SMTP_SERVER`: Servidor SMTP para envío de correos
- `EMAIL_SMTP_PORT`: Puerto del servidor SMTP
- `EMAIL_USERNAME`: Tu correo electrónico
- `EMAIL_PASSWORD`: Tu contraseña o clave de aplicación
- `TELEGRAM_TOKEN`: token de nuesto bot

## 🧩 Componentes básicos

El sistema se compone de cuatro elementos principales:

1. **Agentes**: Entidades especializadas con roles y objetivos específicos
2. **Tareas**: Trabajos específicos asignados a los agentes
3. **Flujo de trabajo**: Secuencia y organización de tareas
4. **Memoria**: Sistema de almacenamiento para aprender de experiencias pasadas

## 🤖 Creando agentes

Los agentes son el corazón del sistema. Cada agente tiene un rol específico y utiliza un LLM para completar tareas.

### Uso básico de agentes

```python
from llm.deepseek import DeepSeekAPI
from agents.base import Agent

# Crear conexión con el LLM
deepseek = DeepSeekAPI(model="deepseek-chat", temperature=0.7)

# Crear un agente básico
mi_agente = Agent(
    name="Investigador",
    role="Especialista en recopilación de datos",
    goal="Encontrar información precisa y relevante",
    backstory="Experimentado investigador con habilidades analíticas",
    llm=deepseek
)
```

### Crear agentes especializados

Para crear un agente especializado, extiende la clase `Agent`:

```python
from agents.base import Agent

class MiAgenteEspecializado(Agent):
    def __init__(self, llm):
        super().__init__(
            name="Nombre del Agente",
            role="Rol del Agente",
            goal="Objetivo principal",
            backstory="Historia de fondo",
            llm=llm
        )
    
    # Opcionalmente, personaliza el comportamiento
    def execute_task(self, task_description, context=None):
        # Preprocesamiento personalizado aquí
        return super().execute_task(task_description, context)
```

### Métodos importantes de Agent

| Método | Descripción | Parámetros |
|--------|-------------|------------|
| `execute_task()` | Ejecuta una tarea usando el LLM | `task_description`, `context=None` |
| `refinar_objetivo()` | Adapta el objetivo al tema actual | `tema`, `contexto=None` |
| `necesita_mas_informacion()` | Verifica si se requiere más datos | `resultado` |
| `solicitar_informacion_adicional()` | Solicita datos adicionales | `peticion`, `contexto` |

## 📋 Definiendo tareas

Las tareas son instrucciones específicas asignadas a un agente.

### Crear una tarea básica

```python
from workflow.task import Task

# Crear una tarea para un agente
tarea = Task(
    description="""
    Investiga el tema "Inteligencia Artificial" y recopila información.
    
    INSTRUCCIONES:
    1. Buscar definiciones y conceptos clave
    2. Incluir aplicaciones actuales
    3. Destacar avances recientes
    """,
    agent=mi_agente
)
```

### Referencia a resultados anteriores

Puedes referenciar resultados de tareas previas usando placeholders:

```python
tarea_siguiente = Task(
    description="""
    Analiza esta información sobre Inteligencia Artificial.
    
    INSTRUCCIONES:
    1. Identifica los 3 conceptos más importantes
    2. Sintetiza la información principal
    
    {task_1}  # Esto será reemplazado por el resultado de la primera tarea
    """,
    agent=otro_agente
)
```

## 🔄 Configurando el flujo de trabajo

El flujo de trabajo coordina la ejecución de tareas entre diferentes agentes.

### Crear un flujo básico

```python
from workflow.workflow import MultiAgentWorkflow

# Crear el flujo con agentes y tareas
flujo = MultiAgentWorkflow(
    agents=[agente1, agente2, agente3],
    tasks=[tarea1, tarea2, tarea3]
)

# Ejecutar el flujo
resultados = flujo.run()

# Acceder a los resultados
primer_resultado = resultados["task_1"]
segundo_resultado = resultados["task_2"]
```

### Flujo con retroalimentación entre agentes

El modo con retroalimentación permite que los agentes soliciten información adicional:

```python
# Ejecutar con retroalimentación
resultados = flujo.ejecutar_con_retroalimentacion()
```

### Ejecutar tareas personalizadas

Para métodos especiales de un agente:

```python
resultado_personalizado = flujo.ejecutar_tarea_personalizada(
    1,  # Índice del agente (0-based)
    param1, param2,  # Parámetros para el método
    method_name='nombre_del_metodo'  # Nombre del método a ejecutar
)
```

## 🧠 Sistema de memoria

La memoria permite a los agentes aprender de experiencias previas.

### Inicializar memoria para un agente

```python
from memory.agente_memoria import AgenteMemoria

# Asignar memoria a un agente
mi_agente.memoria = AgenteMemoria("NombreDelAgente")
```

### Almacenar resultados en memoria

```python
# Guardar una tarea completada en memoria
mi_agente.memoria.agregar_tarea(
    descripcion_tarea="Descripción de la tarea",
    resultado="Resultado obtenido",
    calificacion_exito=9,  # Valoración de 1-10
    tema="Tema específico"
)
```

### Recuperar tareas similares

```python
# Buscar tareas similares previas
tareas_similares = mi_agente.memoria.obtener_tareas_exitosas_similares(
    descripcion_tarea="Nueva tarea a realizar",
    tema="Tema de la tarea",
    limite=3  # Número máximo de resultados
)

# Usar las tareas similares como contexto
if tareas_similares:
    ejemplos = "\n\n".join([f"Ejemplo {i+1}:\n{tarea['resultado'][:300]}..." 
                          for i, tarea in enumerate(tareas_similares)])
    contexto = f"Ejemplos previos similares:\n{ejemplos}"
```

## 🔍 Ejemplos prácticos

### Flujo de trabajo para generar un correo informativo

```python
# Inicializar el LLM
deepseek = DeepSeekAPI(model="deepseek-chat", temperature=0.7)

# Crear agentes
investigador = ResearcherAgent(deepseek)
analista = AnalystAgent(deepseek)
comunicador = CommunicatorAgent(deepseek)

# Asignar memoria
investigador.memoria = AgenteMemoria("Investigador")
analista.memoria = AgenteMemoria("Analista")
comunicador.memoria = AgenteMemoria("Comunicador")

# Definir tema
tema = "Energías renovables"

# Refinar objetivos según el tema
investigador.refinar_objetivo(tema)
analista.refinar_objetivo(tema)
comunicador.refinar_objetivo(tema)

# Crear tareas
tarea_investigacion = Task(
    description=f"""
    Investiga el tema "{tema}" y recopila información relevante.
    
    INSTRUCCIONES:
    1. Busca datos importantes sobre el tema
    2. Incluye definiciones, historia y aplicaciones
    3. Menciona 3-5 puntos interesantes
    """,
    agent=investigador
)

tarea_analisis = Task(
    description=f"""
    Analiza la siguiente información sobre "{tema}".
    
    INSTRUCCIONES:
    1. Identifica los aspectos más importantes
    2. Sintetiza la información de forma concisa
    
    {{task_1}}
    """,
    agent=analista
)

tarea_comunicacion = Task(
    description=f"""
    Crea un correo electrónico sobre "{tema}".
    
    INSTRUCCIONES:
    1. Utiliza formato profesional
    2. Incluye introducción, desarrollo y conclusión
    
    {{task_2}}
    """,
    agent=comunicador
)

# Crear el flujo de trabajo
flujo = MultiAgentWorkflow(
    agents=[investigador, analista, comunicador],
    tasks=[tarea_investigacion, tarea_analisis, tarea_comunicacion]
)

# Ejecutar con retroalimentación
resultados = flujo.ejecutar_con_retroalimentacion()

# Obtener el correo generado
correo = resultados["task_3"]
print(correo)
```

### Crear un agente con comportamiento personalizado

```python
class AnalistaFinanciero(Agent):
    def __init__(self, llm):
        super().__init__(
            name="Analista Financiero",
            role="Especialista en análisis de datos financieros",
            goal="Interpretar tendencias y ofrecer recomendaciones basadas en datos",
            backstory="Analista con 15 años de experiencia en mercados globales",
            llm=llm
        )
    
    def execute_task(self, task_description, context=None):
        # Añadir instrucciones específicas para análisis financiero
        task_with_guidelines = f"""
        {task_description}
        
        DIRECTRICES FINANCIERAS:
        - Considera siempre el contexto macroeconómico
        - Incluye análisis de riesgo
        - Destaca tendencias a corto y largo plazo
        """
        return super().execute_task(task_with_guidelines, context)
    
    def analizar_tendencia(self, datos, periodo):
        """Método especializado para análisis de tendencias."""
        prompt = f"""
        Analiza estos datos financieros para el periodo {periodo}:
        {datos}
        
        Identifica patrones, tendencias y posibles predicciones.
        """
        return self.llm.generate(prompt)
```

## ❓ Solución de problemas

### Problema: El agente no responde como se espera

**Solución**: Mejora las instrucciones en la descripción de la tarea. Sé específico sobre lo que quieres que haga:

```python
tarea = Task(
    description="""
    Investiga el tema "IA" y proporciona información estructurada.
    
    INSTRUCCIONES ESPECÍFICAS:
    1. Define claramente el concepto de IA
    2. Proporciona ejemplos concretos de aplicaciones
    3. Estructura la información en secciones numeradas
    4. NO incluyas opiniones personales
    5. Límite de extensión: 500 palabras
    """,
    agent=mi_agente
)
```

### Problema: Los agentes no comparten información correctamente

**Solución**: Asegúrate de que los placeholders estén correctamente formateados:

```python
# Correcto: Usar {task_1} para referenciar la primera tarea
tarea.description = "Analiza esto: {task_1}"

# Incorrecto: Evita espacios o errores de formato
# tarea.description = "Analiza esto: { task_1 }"
```

### Problema: La memoria no recupera tareas similares

**Solución**: Asegúrate de que el directorio `memory/` existe y tiene permisos de escritura:

```python
import os
os.makedirs("memory", exist_ok=True)
```

---


---

Recuerda que puedes personalizar cualquier aspecto del sistema para adaptarlo a tus necesidades específicas. ¡Experimenta con diferentes agentes, tareas y flujos para obtener los mejores resultados!