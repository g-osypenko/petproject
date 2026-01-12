import time
import logging
from google import genai
from google.genai import types
from sqlalchemy import text

from app.config import Config
from app.database.core import SessionLocal
from app.services import prompts

logger = logging.getLogger(__name__)

client = genai.Client(api_key=Config.GEMINI_API_KEY)

# Словник сесій: {user_id: {"session": chat_object, "last_active": timestamp}}
active_sessions = {}
SESSION_TIMEOUT = 86400  

def search_products_tool(user_query: str) -> str:
    print(f"🔧 TOOL CALLED: Searching for '{user_query}'...")
    
    try:
        embedding = client.models.embed_content(
            model="text-embedding-004",
            contents=user_query,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY")
        ).embeddings[0].values
    except Exception as e:
        return f"System Error during embedding: {e}"

    if not embedding: return "Не вдалося обробити запит."

    db = SessionLocal()
    try:
        sql = text("""
            SELECT name, price, specifications, stock_quantity,
                   (embedding <=> :emb) as distance
            FROM products
            WHERE price > 0 
            ORDER BY distance ASC
            LIMIT 10
        """)
        results = db.execute(sql, {"emb": str(embedding)}).fetchall()
        
        if not results:
            return "У базі даних не знайдено товарів за цим запитом."

        products_data = []
        is_availability_request = any(w in user_query.lower() for w in ['є', 'наявн', 'купити'])
        
        for row in results:
            # Фільтр "Тільки в наявності", якщо питають про покупку
            if is_availability_request and row.stock_quantity <= 0:
                continue
                
            spec = row.specifications or {}
            item_desc = (
                f"ID: {row.name}\n"
                f"Price: {row.price} UAH\n"
                f"Stock: {row.stock_quantity} (Status: {'In Stock' if row.stock_quantity > 0 else 'Out of Stock'})\n"
                f"Specs: {spec}\n"
                "---"
            )
            products_data.append(item_desc)
        
        if not products_data:
            return "Товари знайдені, але їх немає в наявності."
            
        return "\n".join(products_data)

    except Exception as e:
        return f"Database Error: {e}"
    finally:
        db.close()

def get_system_instruction() -> str:

    try:
        return prompts.get_main_system_prompt()
    except AttributeError:
        return "CRITICAL ERROR: prompts.get_main_system_prompt not found."

def get_chat_session(user_id: int):
    current_time = time.time()
    
    if user_id in active_sessions:
        active_sessions[user_id]["last_active"] = current_time
        return active_sessions[user_id]["session"]
    
    chat = client.chats.create(
        model=Config.MODEL_ID,
        config=types.GenerateContentConfig(
            tools=[search_products_tool], 
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=False),
            temperature=0.4,
            max_output_tokens=2500,
            system_instruction=get_system_instruction() 
        ),
        history=[]
    )
    
    active_sessions[user_id] = {
        "session": chat,
        "last_active": current_time
    }
    return chat

def reset_session(user_id: int):
    if user_id in active_sessions:
        del active_sessions[user_id]

def cleanup_inactive_sessions():
    current_time = time.time()
    users_to_remove = []
    
    for user_id, data in active_sessions.items():
        if current_time - data["last_active"] > SESSION_TIMEOUT:
            users_to_remove.append(user_id)
    
    if users_to_remove:
        logging.info(f"🧹 Cleaning up: Removing {len(users_to_remove)} inactive sessions.")
        for user_id in users_to_remove:
            del active_sessions[user_id]

def _clean_html(text: str) -> str:
    if not text: return ""
    text = text.replace("<br>", "\n").replace("**", "").replace("###", "")
    text = text.replace("<ul>", "").replace("</ul>", "")
    text = text.replace("<li>", "• ").replace("</li>", "\n")
    return text.strip()

#ГОЛОВНА ТОЧКА ВХОДУ 
def process_message(user_id: int, user_text: str) -> dict:
    try:
        chat = get_chat_session(user_id)
        response = chat.send_message(user_text)
        
        tokens = 0
        if response.usage_metadata:
            tokens = response.usage_metadata.total_token_count

        clean_text = _clean_html(response.text)
        
        return {
            "text": clean_text,
            "tokens": tokens
        }
    except Exception as e:
        logger.error(f"AI Error: {e}")
        reset_session(user_id) 
        
        return {
            "text": "Вибачте, сталася технічна помилка. Спробуйте ще раз! (Якщо помилка повторюється — перевірте консоль сервера)",
            "tokens": 0
        }