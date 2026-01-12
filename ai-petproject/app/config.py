import os
import sys
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Google AI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_ID = "gemini-2.5-flash"

    # Settings
    LOG_FILE = "history.log"

    @staticmethod
    def validate():
        missing = []
        if not Config.BOT_TOKEN: missing.append("TELEGRAM_BOT_TOKEN")
        if not Config.DATABASE_URL: missing.append("DATABASE_URL")
        if not Config.GEMINI_API_KEY: missing.append("GEMINI_API_KEY")
        
        if missing:
            print(f"❌ CRITICAL ERROR: Не знайдено змінні в .env: {', '.join(missing)}")
            sys.exit(1)


Config.validate()