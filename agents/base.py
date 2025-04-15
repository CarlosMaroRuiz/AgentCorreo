# agents/base.py
class Agent:
    def __init__(self, name, role, goal, backstory, llm):
        """Inicializar un agente con sus atributos y LLM.
        
        Args:
            name (str): Nombre del agente
            role (str): Descripción del rol
            goal (str): Objetivo principal del agente
            backstory (str): Historia de fondo
            llm: Interfaz del modelo de lenguaje
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.objetivo_original = goal  # Guardar el objetivo original
        self.backstory = backstory
        self.llm = llm
        self.memoria = None  # Se asignará después
    
    def execute_task(self, task_description, context=None):
        """Ejecutar una tarea con contexto opcional.
        
        Args:
            task_description (str): La tarea a realizar
            context (str, opcional): Contexto adicional
            
        Returns:
            str: Resultado de la ejecución de la tarea
        """
        # Construir las partes del prompt por separado
        base_prompt = f"""
        # Agente: {self.name} ({self.role})
        
        ## Tu objetivo
        {self.goal}
        
        ## Tu historia
        {self.backstory}
        
        ## Tu tarea actual
        {task_description}
        """
        
        # Añadir contexto si se proporciona
        if context:
            context_part = f"""
        ## Contexto adicional
        {context}
            """
            prompt = base_prompt + context_part
        else:
            prompt = base_prompt
            
        # Añadir instrucción final
        prompt += """
        
        Cumple con tu tarea de manera profesional.
        """
        
        print(f"🔄 {self.name} está trabajando...")
        response = self.llm.generate(prompt)
        print(f"✅ {self.name} ha completado su tarea.")
        
        return response
    
    def refinar_objetivo(self, tema, contexto=None):
        """Refinar dinámicamente el objetivo del agente basado en el tema y contexto.
        
        Args:
            tema (str): Tema de trabajo
            contexto (str, opcional): Contexto adicional
            
        Returns:
            str: Objetivo refinado
        """
        prompt_refinamiento = f"""
        Tu objetivo actual es: {self.goal}
        
        Estás trabajando en el tema: {tema}
        
        Basado en este tema específico y tu rol como {self.role},
        refina tu objetivo para ser más específico y adaptado a esta tarea.
        Responde solo con el objetivo refinado, sin explicaciones adicionales.
        """
        
        if contexto:
            prompt_refinamiento += f"\nContexto adicional:\n{contexto}"
        
        objetivo_refinado = self.llm.generate(prompt_refinamiento)
        self.objetivo_original = self.goal  # Guardar objetivo original
        self.goal = objetivo_refinado
        
        print(f"🔄 {self.name} refinó su objetivo: {objetivo_refinado[:100]}...")
        return objetivo_refinado
    
    def necesita_mas_informacion(self, resultado):
        """Verificar si el agente necesita más información para completar la tarea.
        
        Args:
            resultado (str): Resultado actual
            
        Returns:
            str o None: Solicitud de información adicional o None si tiene suficiente
        """
        prompt_verificacion = f"""
        Analiza este resultado y determina si necesitas información adicional:
        {resultado}
        
        Si necesitas más información, describe exactamente qué necesitas.
        Si tienes información suficiente, responde con "SUFICIENTE".
        """
        respuesta = self.llm.generate(prompt_verificacion)
        if "SUFICIENTE" in respuesta:
            return None
        return respuesta
    
    def solicitar_informacion_adicional(self, peticion, contexto):
        """Solicitar información adicional basada en una petición.
        
        Args:
            peticion (str): La información solicitada
            contexto (str): Contexto actual
            
        Returns:
            str: Información adicional proporcionada
        """
        prompt_info_adicional = f"""
        Basado en tu trabajo previo:
        {contexto}
        
        Se solicita la siguiente información adicional:
        {peticion}
        
        Proporciona solo la información solicitada de manera concisa.
        """
        return self.execute_task(prompt_info_adicional)