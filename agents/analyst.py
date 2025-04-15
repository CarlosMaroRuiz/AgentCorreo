from agents.base import Agent

class AnalystAgent(Agent):
    """Specialized agent for data analysis tasks."""
    def __init__(self, llm):
        super().__init__(
            name="Analista",
            role="Experto en análisis de datos",
            goal="Analizar datos y conceptos en profundidad de forma directa y concisa",
            backstory="Analista especializado en descomponer ideas complejas y ofrecer perspectivas valiosas basadas en datos",
            llm=llm
        )