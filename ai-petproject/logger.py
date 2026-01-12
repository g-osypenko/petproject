import datetime
from typing import Optional


LOG_FILE: str = "history.log"


def log_conversation(
    user_query: str,
    ai_response: str,
    source: str = "Telegram",
    tokens: int = 0,
    debug_info: Optional[str] = None
) -> None:

    timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"--- {timestamp} [{source}] ---\n")
            f.write(f"👤 User: {user_query}\n")
            
            if debug_info:
                f.write(f"⚙️ Debug Info: {debug_info}\n")
                
            f.write(f"🤖 AI: {ai_response}\n")
            f.write(f"🪙 Tokens used: {tokens}\n") 
            f.write("-" * 30 + "\n")
    except Exception as e:
        print(f"⚠️ Помилка запису логу: {e}")