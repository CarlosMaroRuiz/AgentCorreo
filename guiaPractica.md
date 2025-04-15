# Guía Práctica del Sistema Multiagente

Esta guía práctica está diseñada para ayudarte a entender y utilizar efectivamente el Sistema Multiagente para crear aplicaciones inteligentes basadas en LLMs.

## 📋 Contenido

1. [Conceptos básicos](#conceptos-básicos)
2. [Cómo empezar](#cómo-empezar)
3. [Diseño de agentes efectivos](#diseño-de-agentes-efectivos)
4. [Creación de tareas óptimas](#creación-de-tareas-óptimas)
5. [Flujos de trabajo avanzados](#flujos-de-trabajo-avanzados)
6. [Mejores prácticas](#mejores-prácticas)
7. [Patrones de diseño comunes](#patrones-de-diseño-comunes)
8. [Personalización](#personalización)
9. [Solución de problemas](#solución-de-problemas)

## Conceptos básicos

### ¿Qué es un sistema multiagente?

Un sistema multiagente es una arquitectura que utiliza múltiples "agentes" especializados para resolver problemas complejos. Cada agente tiene un rol específico y colabora con otros agentes para completar tareas.

### Componentes clave

1. **Agentes**: Entidades inteligentes con un propósito específico
2. **Tareas**: Instrucciones para los agentes
3. **Flujo de trabajo**: Coordina la ejecución de tareas entre agentes
4. **Memoria**: Almacena experiencias para aprendizaje y referencia

### Beneficios del enfoque multiagente

- **Especialización**: Cada agente se centra en lo que hace mejor
- **Modularidad**: Fácil de mantener y actualizar
- **Escalabilidad**: Añade más agentes según sea necesario
- **Flexibilidad**: Adapta el sistema a diferentes casos de uso

## Cómo empezar

### Instalación rápida

1. Clona el repositorio:
```bash
git clone https://github.com/usuario/sistema-multiagente.git
cd sistema-multiagente
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las credenciales:
```bash
cp .env.example .env
# Edita el archivo .env con tus credenciales
```

### Ejemplo mínimo funcional

Este es el código mínimo para crear un sistema multiagente funcional:

```python
from llm.deepseek import DeepSeekAPI
from agents.base import Agent
from workflow.task import Task
from workflow.workflow import MultiAgentWorkflow

# Inicializar LLM
deepseek = DeepSeekAPI()

# Crear agentes
agente1 = Agent(name="Agente1", role="Rol1", goal="Objetivo1", 
                backstory="Historia1", llm=deepseek)
agente2 = Agent(name="Agente2", role="Rol2", goal="Objetivo2", 
                backstory="Historia2", llm=deepseek)

# Crear tareas
tarea1 = Task(description="Instrucciones para tarea 1", agent=agente1)
tarea2 = Task(description="Usa esto: {task_1}", agent=agente2)

# Crear flujo
flujo = MultiAgentWorkflow(
    agents=[agente1, agente2],
    tasks=[tarea1, tarea2]
)

# Ejecutar
resultados = flujo.run()
print(resultados["task_2"])  # Resultado final
```

## Diseño de agentes efectivos

### Componentes de un buen agente

1. **Nombre distintivo**: Identifica claramente el propósito
2. **Rol específico**: Define el área de especialización
3. **Objetivo claro**: Establece lo que debe lograr
4. **Historia convincente**: Proporciona contexto y personalidad

### Personalidad y tono

El "backstory" influye en cómo responde el agente. Por ejemplo:

```python
# Agente formal y técnico
agente_tecnico = Agent(
    name="Especialista Técnico",
    role="Experto en aspectos técnicos",
    goal="Proporcionar información técnica precisa",
    backstory="Ingeniero con 20 años de experiencia y enfoque metódico",
    llm=deepseek
)

# Agente creativo y accesible
agente_creativo = Agent(
    name="Innovador",
    role="Generador de ideas creativas",
    goal="Producir conceptos originales y accesibles",
    backstory="Pensador divergente con pasión por explicar ideas complejas de forma simple",
    llm=deepseek
)
```

### Especialización de agentes

Es mejor crear agentes especializados que generalistas:

✅ **Bueno**: "Analista de datos financieros"  
❌ **Evitar**: "Agente que hace de todo"

### Sobrescribir métodos

Para comportamientos especializados, extiende la clase `Agent`:

```python
class AgenteEspecial(Agent):
    def execute_task(self, task_description, context=None):
        # Preprocesamiento personalizado
        modified_task = task_description + "\nConsideración especial: ..."
        return super().execute_task(modified_task, context)
```

## Creación de tareas óptimas

### Anatomía de una buena tarea

1. **Contexto claro**: Sobre qué trata la tarea
2. **Instrucciones específicas**: Qué hacer exactamente
3. **Formato deseado**: Cómo debe presentarse el resultado
4. **Limitaciones**: Restricciones o consideraciones importantes

### Estructura recomendada

```python
tarea = Task(
    description="""
    [CONTEXTO: Breve descripción del tema o situación]
    
    INSTRUCCIONES:
    1. [Paso o requisito específico]
    2. [Otro paso o requisito]
    3. [...]
    
    FORMATO DESEADO:
    [Descripción de cómo debe estructurarse la respuesta]
    
    CONSIDERACIONES:
    - [Limitación o punto importante]
    - [Otra consideración]
    """,
    agent=mi_agente
)
```

### Uso efectivo de placeholders

Los placeholders permiten referenciar resultados anteriores:

```python
tarea2 = Task(
    description="Analiza estos resultados: {task_1}",
    agent=analista
)

tarea3 = Task(
    description="""
    Sintetiza esta información:
    
    ANÁLISIS PRINCIPAL:
    {task_2}
    
    INFORMACIÓN ADICIONAL:
    {info_adicional_2}
    """,
    agent=sintetizador
)
```

### Evitar ambigüedad

Sé específico sobre lo que quieres:

✅ **Bueno**: "Lista 5 ventajas y 5 desventajas en formato de viñetas"  
❌ **Evitar**: "Habla sobre ventajas y desventajas"

## Flujos de trabajo avanzados

### Ejecución con retroalimentación

La retroalimentación permite a los agentes solicitar información adicional:

```python
resultados = flujo.ejecutar_con_retroalimentacion()
```

Este proceso ocurre cuando:
1. Un agente ejecuta su tarea
2. El sistema detecta que necesita más información
3. Se solicita información al agente anterior
4. La tarea se reintenta con la nueva información

### Ejecución de métodos personalizados

Para funcionalidades específicas:

```python
resultado = flujo.ejecutar_tarea_personalizada(
    2,  # Índice del agente (0-indexed)
    "Parámetro adicional",
    otro_parametro=123,
    method_name='metodo_especializado'
)
```

### Flujos condicionales

Aunque no es nativo, puedes implementar flujos condicionales:

```python
# Ejecutar primera tarea
resultado1 = tarea1.execute()

# Decidir qué tarea ejecutar después
if "palabra clave" in resultado1.lower():
    tarea_siguiente = tarea_opcion_a
else:
    tarea_siguiente = tarea_opcion_b

# Configurar contexto manualmente
contexto = {"task_1": resultado1}
resultado2 = tarea_siguiente.execute(context=contexto)
```

## Mejores prácticas

### Prompting efectivo

1. **Sé específico**: Define claramente lo que quieres
2. **Estructurado**: Usa numeración, viñetas y secciones
3. **Ejemplos**: Proporciona ejemplos del formato deseado
4. **Tono y estilo**: Indica cómo debe "sonar" la respuesta

### Gestión de memoria

1. Usa calificaciones significativas (1-10) para los resultados
2. Limita las muestras de resultados largos (usa primeros 300-500 caracteres)
3. Limpia la memoria periódicamente si se vuelve demasiado grande

### Manejo de errores

Implementa manejo de errores para robustez:

```python
try:
    resultado = flujo.ejecutar_con_retroalimentacion()
except Exception as e:
    print(f"Error en el flujo: {str(e)}")
    # Implementar plan de respaldo
    resultado = {"task_1": "Contenido por defecto"}
```

### Optimización de costos

1. Usa temperaturas bajas (0.0-0.3) para tareas que requieren precisión
2. Limita la longitud de los prompts cuando sea posible
3. Implementa caché para resultados frecuentes

## Patrones de diseño comunes

### Patrón Investigador-Analista-Sintetizador

Útil para procesar información compleja:

```python
investigador = ResearcherAgent(llm)
analista = AnalystAgent(llm)
sintetizador = Agent(name="Sintetizador", ...)

tareas = [
    Task(description="Investiga sobre X", agent=investigador),
    Task(description="Analiza: {task_1}", agent=analista),
    Task(description="Sintetiza: {task_2}", agent=sintetizador)
]
```

### Patrón Generador-Evaluador-Refinador

Ideal para crear contenido de alta calidad:

```python
generador = Agent(name="Generador", ...)
evaluador = Agent(name="Evaluador", ...)
refinador = Agent(name="Refinador", ...)

tareas = [
    Task(description="Genera contenido sobre X", agent=generador),
    Task(description="Evalúa este contenido: {task_1}", agent=evaluador),
    Task(description="Refina basado en esta evaluación: \n{task_1}\n\nEvaluación: {task_2}", agent=refinador)
]
```

### Patrón Divisor-Especialista-Integrador

Para procesar información extensa:

```python
divisor = Agent(name="Divisor", ...)
especialista = Agent(name="Especialista", ...)
integrador = Agent(name="Integrador", ...)

tareas = [
    Task(description="Divide este contenido en secciones: [contenido]", agent=divisor),
    Task(description="Procesa cada sección: {task_1}", agent=especialista),
    Task(description="Integra los resultados: {task_2}", agent=integrador)
]
```

## Personalización

### Crear conectores para otros LLMs

Puedes adaptar el sistema para usar otros LLMs:

```python
# llm/openai_api.py
class OpenAIAPI:
    def __init__(self, model="gpt-4", temperature=0.7):
        self.model = model
        self.temperature = temperature
        # Configuración específica...
    
    def generate(self, prompt):
        # Implementación específica para OpenAI
        # Debe devolver el texto generado como string
```

### Extender la funcionalidad de memoria

Para memoria más sofisticada:

```python
class MemoriaAvanzada(AgenteMemoria):
    def __init__(self, nombre_agente, archivo_memoria=None):
        super().__init__(nombre_agente, archivo_memoria)
    
    def busqueda_semantica(self, query, threshold=0.7):
        """Busca por similitud semántica en lugar de palabras clave."""
        # Implementación de búsqueda semántica
```

### Integración con sistemas externos

Ejemplo de integración con una base de datos:

```python
class AgenteConDB(Agent):
    def __init__(self, name, role, goal, backstory, llm, db_connection):
        super().__init__(name, role, goal, backstory, llm)
        self.db = db_connection
    
    def execute_task(self, task_description, context=None):
        # Consultar DB para información relevante
        db_info = self.get_relevant_data()
        # Añadir a la tarea
        enhanced_task = f"{task_description}\n\nDatos de referencia:\n{db_info}"
        return super().execute_task(enhanced_task, context)
    
    def get_relevant_data(self):
        # Implementar lógica de consulta a DB
        return "Datos relevantes de la DB"
```

## Solución de problemas

### Problemas comunes y soluciones

1. **Respuestas demasiado genéricas**
   - Solución: Añade más especificidad en las instrucciones
   - Ejemplo: "Proporciona al menos 3 ejemplos concretos con datos numéricos"

2. **Agentes ignorando partes de las instrucciones**
   - Solución: Estructura las instrucciones más claramente con numeración
   - Ejemplo: "1. Haz X. 2. Luego haz Y. 3. Finalmente, haz Z."

3. **Respuestas excesivamente largas**
   - Solución: Añade limitaciones explícitas
   - Ejemplo: "Limita tu respuesta a 300 palabras máximo"

4. **Placeholders no funcionando**
   - Solución: Verifica el formato exacto `{task_X}` sin espacios adicionales
   - Asegúrate de que la tarea referenciada existe y es anterior

5. **Memoria no guardando correctamente**
   - Solución: Verifica permisos de escritura y que la ruta exista
   - Añade manejo de excepciones al guardar

### Diagnóstico y depuración

Para diagnóstico detallado:

```python
# Activar modo de depuración
import logging
logging.basicConfig(level=logging.DEBUG)

# Inspeccionar prompts generados
task_description = task.description
context_formatted = "Contexto formateado"
full_prompt = f"""
# Agente: {agent.name} ({agent.role})
## Objetivo
{agent.goal}
## Historia
{agent.backstory}
## Tarea
{task_description}
## Contexto adicional
{context_formatted}
"""
print("PROMPT COMPLETO:")
print(full_prompt)

# Probar individualmente
result = agent.llm.generate(full_prompt)
print("RESULTADO:")
print(result)
```

---

Esta guía práctica te ayudará a aprovechar al máximo el Sistema Multiagente. Combina estos conceptos con los ejemplos de código y la referencia de clases para crear aplicaciones potentes y flexibles.

Recuerda que la experimentación es clave: prueba diferentes configuraciones, prompts y estructuras de agentes para encontrar lo que mejor funciona para tu caso de uso específico.