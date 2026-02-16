# migrations/001_add_budget_mice.py
from models import Product, Category

# Дані для додавання
NEW_PRODUCTS = [
    # (Назва, Бренд, Ціна, Специфікації)
    ("Logitech G102 Lightsync", "Logitech", 999, 
     {"brand": "Logitech", "color": "Black", "connectivity": "Wired", "dpi": "8000", "rgb": "Yes"}),
     
    ("Logitech G102 Lightsync White", "Logitech", 999, 
     {"brand": "Logitech", "color": "White", "connectivity": "Wired", "dpi": "8000", "rgb": "Yes"}),

    ("A4Tech Bloody V7", "A4Tech", 799, 
     {"brand": "A4Tech", "color": "Black", "connectivity": "Wired", "dpi": "3200"}),
     
    ("Razer DeathAdder Essential", "Razer", 1100, 
     {"brand": "Razer", "color": "Black", "connectivity": "Wired", "dpi": "6400"}),
]

def up(db):
    # 1. Знаходимо категорію "Геймінг" (вона має ID 5 згідно seed.py)
    # Або шукаємо по імені
    category = db.query(Category).filter(Category.name.like("%Геймінг%")).first()
    
    if not category:
        print("Категорія Геймінг не знайдена! Пропускаємо.")
        return

    count = 0
    for name, brand, price, specs in NEW_PRODUCTS:
        # Перевірка на дублікати (щоб не додати двічі, якщо лог зіб'ється)
        exists = db.query(Product).filter_by(name=name).first()
        if exists:
            print(f"  - Товар {name} вже є. Пропускаємо.")
            continue

        new_product = Product(
            name=name,
            price=price,
            category_id=category.id,
            stock_quantity=50, # Ставимо дефолтний сток
            rating=4.5,
            specifications=specs
            # embedding буде NULL, поки ви не запустите скрипт генерації векторів
        )
        db.add(new_product)
        count += 1
    
    db.commit()
    print(f"  + Додано {count} нових товарів.")