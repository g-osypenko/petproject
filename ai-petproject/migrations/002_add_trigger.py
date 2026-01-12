# migrations/002_add_trigger.py
from sqlalchemy import text

def up(db):
    print("   -> 🔫 Створення тригера LISTEN/NOTIFY...")
    
    # 1. Створюємо функцію, яка відправляє сповіщення
    # Вона відправляє канал "new_product_event" і ID нового товару
    sql_function = """
    CREATE OR REPLACE FUNCTION notify_new_product() RETURNS trigger AS $$
    BEGIN
        PERFORM pg_notify('new_product_event', NEW.id::text);
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    
    # 2. Прив'язуємо цю функцію до таблиці products (тільки при INSERT)
    sql_trigger = """
    CREATE TRIGGER product_insert_trigger
    AFTER INSERT ON products
    FOR EACH ROW EXECUTE FUNCTION notify_new_product();
    """
    
    try:
        db.execute(text(sql_function))
        db.execute(text(sql_trigger))
        db.commit()
    except Exception as e:
        print(f"⚠️ Помилка створення тригера (можливо вже є): {e}")
        db.rollback()