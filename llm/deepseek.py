import os
from openai import OpenAI
from config.settings import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

class DeepSeekAPI:
    def __init__(self, model="deepseek-chat", temperature=0.7):
        """Initialize DeepSeek API wrapper."""
        if not DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
        
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        
    def generate(self, prompt):
        """Generate a response using the DeepSeek API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling DeepSeek API: {str(e)}")
            return f"Error: {str(e)}"