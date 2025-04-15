from agents.base import Agent

class CommunicatorAgent(Agent):
    """Specialized agent for communication tasks."""
    def __init__(self, llm):
        super().__init__(
            name="Comunicador",
            role="Experto en comunicación",
            goal="Crear correos profesionales directos sin metadatos ni explicaciones del proceso",
            backstory="Especialista en comunicación clara y directa que se enfoca en transmitir información de forma profesional",
            llm=llm
        )