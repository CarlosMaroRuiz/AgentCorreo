import re

class Task:
    def __init__(self, description, agent):
        """Initialize a task with description and assigned agent.
        
        Args:
            description (str): Task description
            agent: Agent to perform the task
        """
        self.description = description
        self.agent = agent
        self.output = None

    def execute(self, context=None):
        """Execute the task and store the result.
        
        Args:
            context (str, optional): Additional context
            
        Returns:
            str: Task execution result
        """
        self.output = self.agent.execute_task(self.description, context)
        return self.output

    def decide_next_task(self, available_tasks, context):
        """Decide which task should be executed next based on current context."""
        task_options = "\n".join([
            f"{i + 1}. {task.description[:100]}..."
            for i, task in enumerate(available_tasks)
        ])

        decision_prompt = f"""
        Based on your current results:
        {context}
        
        The following tasks are available:
        {task_options}
        
        Which task should be executed next? Respond with just the task number.
        """

        response = self.agent.llm.generate(decision_prompt)
        try:
            # Extract the task number from the response
            task_num = int(re.search(r'\d+', response).group()) - 1
            return task_num if 0 <= task_num < len(available_tasks) else 0
        except:
            # Default to the first task if parsing fails
            return 0
