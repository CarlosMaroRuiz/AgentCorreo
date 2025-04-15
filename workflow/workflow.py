# workflow/workflow.py
class MultiAgentWorkflow:
    def __init__(self, agents=None, tasks=None):
        """Inicializar un flujo de trabajo multiagente."""
        self.agents = agents or []
        self.tasks = tasks or []
        self.results = {}
    
    def add_agent(self, agent):
        """Añadir un agente al flujo de trabajo."""
        self.agents.append(agent)
    
    def add_task(self, task):
        """Añadir una tarea al flujo de trabajo."""
        self.tasks.append(task)
    
    def run(self):
        """Ejecutar todas las tareas en secuencia."""
        context = {}
        
        print("🚀 Iniciando flujo de trabajo multiagente...")
        
        for i, task in enumerate(self.tasks):
            print(f"\nTarea {i+1}/{len(self.tasks)}: {task.description[:50]}...")
            
            # Reemplazar placeholders de tareas anteriores
            task_description = task.description
            task_context = ""
            
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in task_description:
                    task_description = task_description.replace(placeholder, value)
                task_context += f"\n\n{key.upper()}:\n{value}"
            
            # Ejecutar la tarea
            result = task.execute(task_context)
            task_key = f"task_{i+1}"
            context[task_key] = result
            self.results[task_key] = result
        
        print("\n✨ Flujo de trabajo completado.")
        return self.results
    
    def ejecutar_con_retroalimentacion(self):
        """Ejecutar tareas con bucles de retroalimentación entre agentes."""
        context = {}
        
        print("🚀 Iniciando flujo de trabajo multiagente con retroalimentación...")
        
        i = 0
        while i < len(self.tasks):
            task = self.tasks[i]
            print(f"\nTarea {i+1}/{len(self.tasks)}: {task.description[:50]}...")
            
            # Reemplazar placeholders de tareas anteriores
            task_description = task.description
            task_context = ""
            
            for key, value in context.items():
                placeholder = f"{{{key}}}"
                if placeholder in task_description:
                    task_description = task_description.replace(placeholder, value)
                task_context += f"\n\n{key.upper()}:\n{value}"
            
            # Ejecutar la tarea
            result = task.execute(task_context)
            
            # Verificar si el agente necesita más información
            needs_more_info = task.agent.necesita_mas_informacion(result)
            
            if needs_more_info and i > 0:
                # Obtener información adicional del agente anterior
                print(f"⚠️ {task.agent.name} solicita información adicional...")
                previous_agent = self.tasks[i-1].agent
                additional_info = previous_agent.solicitar_informacion_adicional(
                    needs_more_info, 
                    context[f"task_{i}"]
                )
                
                # Actualizar contexto con información adicional
                context[f"info_adicional_{i}"] = additional_info
                print(f"✅ {previous_agent.name} ha proporcionado información adicional.")
                
                # Volver a ejecutar la tarea actual con información adicional
                print(f"🔄 {task.agent.name} reintenta la tarea con nueva información...")
                result = task.execute(task_context + f"\n\nINFORMACIÓN ADICIONAL:\n{additional_info}")
            
            # Si no se necesita información adicional, continuar normalmente
            task_key = f"task_{i+1}"
            context[task_key] = result
            self.results[task_key] = result
            i += 1
        
        print("\n✨ Flujo de trabajo con retroalimentación completado.")
        return self.results
    
    def ejecutar_tarea_personalizada(self, task_index, *args, **kwargs):
        """Ejecuta una tarea personalizada específica con argumentos adicionales."""
        if task_index < 0 or task_index >= len(self.tasks):
            raise ValueError(f"Índice de tarea {task_index} fuera de rango")
            
        task = self.tasks[task_index]
        agent = task.agent
        
        # Verificar si el agente tiene el método necesario
        method_name = kwargs.pop('method_name', 'execute_task')
        if not hasattr(agent, method_name):
            raise AttributeError(f"El agente {agent.name} no tiene el método {method_name}")
        
        # Obtener y ejecutar el método
        method = getattr(agent, method_name)
        return method(*args, **kwargs)