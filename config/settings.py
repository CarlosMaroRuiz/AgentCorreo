
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Default email recipients
DEFAULT_EMAIL_RECIPIENTS = [
    "221220@ids.upchiapas.edu.mx",
    "243250@ib.upchiapas.edu.mx",
    "223267@ids.upchiapas.edu.mx"
]

# Email configuration
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# LLM API configuration
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
DEEPSEEK_TEMPERATURE = float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7"))
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

#telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")