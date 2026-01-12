import time
import logging
import select  
from typing import List

from google import genai
from google.genai import types
from sqlalchemy import text 

from app.config import Config
from app.database.core import SessionLocal, engine 
from app.database.models import Product

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DatabaseVectorManager:
    def __init__(self, model: str = "text-embedding-004"):
        self.model = model
        if not Config.GEMINI_API_KEY:
            raise ValueError("❌ GEMINI_API_KEY не знайдено")
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)

    def _get_embedding(self, text: str) -> List[float]:
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=text,
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    title="Product Description"
                )
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"API Error: {e}")
            return []

    def textify_product(self, product: Product) -> str:
        specs = product.specifications if product.specifications else {}
        return (
            f"Product: {product.name}. "
            f"Category ID: {product.category_id}. "
            f"Description: {product.description or ''} "
            f"Specs: {specs}"
        ).strip()

    def process_specific_product(self, product_id: int):
        session = SessionLocal()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product and product.embedding is None:
                logger.info(f"⚡ Instant Update: Обробка ID {product_id}...")
                text_rep = self.textify_product(product)
                vector = self._get_embedding(text_rep)
                if vector:
                    product.embedding = vector
                    session.commit()
                    logger.info(f"✅ ID {product_id} векторизовано миттєво!")
            else:
                pass
        except Exception as e:
            logger.error(f"Error processing ID {product_id}: {e}")
        finally:
            session.close()

    def fill_missing_embeddings(self):
        session = SessionLocal()
        try:
            products = session.query(Product).filter(Product.embedding.is_(None)).limit(50).all()
            if products:
                logger.info(f"🔍 Scan found {len(products)} pending items...")
                for p in products:
                    self.process_specific_product(p.id)
        finally:
            session.close()

    def run_daemon(self, interval: int = 30):
        logger.info(" Vector Manager: Connecting to Real-Time Events...")
        
        connection = engine.raw_connection()
        connection.set_isolation_level(0) 
        cursor = connection.cursor()
        
        cursor.execute("LISTEN new_product_event;")
        logger.info("📡 Listening for 'new_product_event'...")

        while True:
            # 3. Чекаємо на повідомлення АБО таймаут (select)
            # select чекає, поки connection стане "готовим до читання"
            if select.select([connection], [], [], interval) == ([], [], []):
                # Таймаут спрацював (подій не було N секунд) -> Запускаємо звичайну перевірку
                # Це страховка на випадок, якщо повідомлення загубилось
                self.fill_missing_embeddings()
            else:
                # Є подія!
                connection.poll()
                while connection.notifies:
                    notify = connection.notifies.pop(0)
                    product_id = int(notify.payload)
                    logger.info(f"🔔 Received Notification for Product ID: {product_id}")
                    
                    # Обробляємо саме цей товар
                    self.process_specific_product(product_id)

if __name__ == "__main__":
    manager = DatabaseVectorManager()
    manager.run_daemon()