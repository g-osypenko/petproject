import os
import sys
import importlib.util

sys.path.append(os.getcwd())

from app.database.core import SessionLocal, engine, Base
from app.database.models import MigrationLog, Product, Category

MIGRATION_DIR = "migrations"

def init_migration_table():
    Base.metadata.create_all(bind=engine)

def run_migrations():
    if not os.path.exists(MIGRATION_DIR):
        os.makedirs(MIGRATION_DIR)
        print(f"📁 Створено папку {MIGRATION_DIR}")
        return

    db = SessionLocal()
    init_migration_table()
    

    files = sorted([f for f in os.listdir(MIGRATION_DIR) if f.endswith(".py") and f != "__init__.py"])
    
    print(f"📦 Знайдено файлів міграцій: {len(files)}")

    for filename in files:
        exists = db.query(MigrationLog).filter_by(filename=filename).first()
        if exists:
            continue 

        print(f"🚀 Виконується: {filename}...")
        
        try:
            file_path = os.path.join(MIGRATION_DIR, filename)
            spec = importlib.util.spec_from_file_location("migration_module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "up"):
                module.up(db)
                
                db.add(MigrationLog(filename=filename))
                db.commit()
                print(f"✅ Успішно!")
            else:
                print(f"⚠️ У файлі {filename} немає функції 'up(db)'")

        except Exception as e:
            print(f"❌ Помилка в {filename}: {e}")
            db.rollback()
            break 
    
    db.close()
    print("🏁 Роботу завершено.")

if __name__ == "__main__":
    run_migrations()