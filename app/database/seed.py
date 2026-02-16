import json
import random
from typing import List, Dict, Any
from sqlalchemy import text
from database import SessionLocal
from models import Product, Category

# --- РЕАЛЬНІ ДАНІ (МАСШТАБНЕ ОНОВЛЕННЯ) ---
MODELS_DATA = {
    1: [ # Смартфони та Планшети (Додано планшети та нові бренди)
        # --- ФЛАГМАНИ ---
        ("Apple iPhone 16 Pro Max", "Apple", 58000, ["256GB", "512GB", "1TB"], ["Black Titanium", "Natural", "Desert"]),
        ("Samsung Galaxy S25 Ultra", "Samsung", 52000, ["256GB", "512GB"], ["Titanium Blue", "Titanium Gray"]),
        ("Google Pixel 10 Pro XL", "Google", 45000, ["128GB", "256GB", "512GB"], ["Obsidian", "Hazel"]),
        ("Xiaomi 15 Ultra", "Xiaomi", 38000, ["512GB", "1TB"], ["Black", "White"]),
        ("Honor Magic 6 Pro", "Honor", 40000, ["512GB"], ["Black", "Epi Green"]), # НОВЕ
        ("Nothing Phone (2)", "Nothing", 24000, ["256GB", "512GB"], ["Dark Grey", "White"]), # НОВЕ
        
        # --- СЕРЕДНІЙ КЛАС ---
        ("Apple iPhone 15", "Apple", 33000, ["128GB", "256GB"], ["Black", "Blue", "Pink", "Green"]),
        ("Samsung Galaxy S24 FE", "Samsung", 28000, ["128GB", "256GB"], ["Graphite", "Mint"]),
        ("Google Pixel 8a", "Google", 16000, ["128GB"], ["Obsidian", "Porcelain", "Aloe"]),
        ("OnePlus 12R", "OnePlus", 22000, ["256GB"], ["Iron Gray", "Cool Blue"]), # НОВЕ
        ("Nothing Phone (2a)", "Nothing", 14000, ["128GB", "256GB"], ["Black", "Milk"]), # НОВЕ
        ("Xiaomi Poco F6 Pro", "Xiaomi", 20000, ["512GB", "1TB"], ["Black", "White"]), # НОВЕ
        
        # --- БЮДЖЕТНІ ---
        ("Samsung Galaxy A55", "Samsung", 13999, ["128GB", "256GB"], ["Awesome Iceblue", "Awesome Navy", "Lilac"]),
        ("Samsung Galaxy A35", "Samsung", 11500, ["128GB", "256GB"], ["Iceblue", "Navy"]),
        ("Samsung Galaxy A25", "Samsung", 8500, ["128GB", "256GB"], ["Blue Black", "Yellow"]),
        ("Xiaomi Redmi Note 13 Pro+", "Xiaomi", 15000, ["512GB"], ["Midnight Black", "Purple"]),
        ("Xiaomi Redmi Note 13", "Xiaomi", 7500, ["128GB", "256GB"], ["Midnight Black", "Mint Green"]),
        ("Motorola Moto G84", "Motorola", 9999, ["256GB"], ["Marshmallow Blue", "Viva Magenta"]),
        ("Motorola Edge 40 Neo", "Motorola", 12000, ["256GB"], ["Black Beauty", "Caneel Bay"]), # НОВЕ
        ("Realme 12 Pro", "Realme", 13000, ["256GB"], ["Submarine Blue", "Navigator Beige"]),
        ("Infinix Note 40 Pro", "Infinix", 9500, ["256GB"], ["Vintage Green", "Titan Gold"]), # НОВЕ

        # --- ПЛАНШЕТИ (НОВЕ) ---
        ("Apple iPad Air 13 M2", "Apple", 38000, ["128GB", "256GB"], ["Space Grey", "Blue", "Purple"]),
        ("Apple iPad 10.9 (2022)", "Apple", 16000, ["64GB", "256GB"], ["Blue", "Pink", "Silver"]),
        ("Samsung Galaxy Tab S9 FE", "Samsung", 14000, ["128GB"], ["Gray", "Mint"]),
        ("Lenovo Tab P11 Gen 2", "Lenovo", 11000, ["128GB"], ["Storm Grey"]),
        ("Xiaomi Pad 6", "Xiaomi", 13000, ["256GB"], ["Gravity Gray", "Gold"]),
    ],
    2: [ # Ноутбуки
        # --- MACBOOK ---
        ("Apple MacBook Pro 14 M4", "Apple", 85000, ["16/512GB", "24/1TB"], ["Space Black", "Silver"]),
        ("Apple MacBook Air 15 M3", "Apple", 56000, ["16/512GB"], ["Midnight", "Starlight"]),
        ("Apple MacBook Air 13 M2", "Apple", 41000, ["8/256GB"], ["Midnight", "Space Grey"]),
        
        # --- WINDOWS PREMIUM ---
        ("Dell XPS 16 (2025)", "Dell", 98000, ["32/1TB", "64/2TB"], ["Platinum"]),
        ("Lenovo Yoga Slim 7x", "Lenovo", 48000, ["16/1TB"], ["Cosmic Blue"]),
        ("ASUS Zenbook 14 OLED", "ASUS", 42000, ["16/1TB"], ["Ponder Blue"]),
        ("HP Spectre x360", "HP", 68000, ["16/1TB"], ["Nightfall Black"]), # НОВЕ
        ("Microsoft Surface Laptop 7", "Microsoft", 55000, ["16/512GB"], ["Platinum", "Black"]), # НОВЕ
        
        # --- ГЕЙМЕРСЬКІ ---
        ("ASUS ROG Strix G16", "ASUS", 65000, ["i7/16/1TB/RTX4060", "i9/32/1TB/RTX4070"], ["Eclipse Gray"]),
        ("ASUS TUF Gaming A15", "ASUS", 45000, ["Ryzen7/16/512GB/RTX4050"], ["Mecha Gray"]), # НОВЕ
        ("Lenovo Legion Pro 5", "Lenovo", 72000, ["i7/32/1TB/RTX4070"], ["Onyx Grey"]),
        ("Lenovo LOQ 15", "Lenovo", 38000, ["i5/16/512GB/RTX4050"], ["Storm Grey"]), # НОВЕ
        ("Acer Nitro V 15", "Acer", 32000, ["i5/16/512GB/RTX4050"], ["Obsidian Black"]),
        ("MSI Katana 15", "MSI", 48000, ["i7/16/1TB/RTX4060"], ["Black"]), # НОВЕ
        ("HP Omen 16", "HP", 58000, ["i7/16/1TB/RTX4060"], ["Shadow Black"]), # НОВЕ
        
        # --- БЮДЖЕТНІ ---
        ("Acer Aspire 5", "Acer", 18000, ["16/512GB"], ["Steel Gray"]),
        ("Lenovo IdeaPad Slim 3", "Lenovo", 14500, ["8/256GB"], ["Arctic Grey"]),
        ("HP Pavilion 15", "HP", 22000, ["16/512GB"], ["Natural Silver"]), # НОВЕ
        ("ASUS Vivobook Go 15", "ASUS", 16500, ["16/512GB"], ["Cool Silver"]),
    ],
    3: [ # Комплектуючі (Значне розширення)
        # --- GPU ---
        ("NVIDIA GeForce RTX 5090", "MSI", 95000, ["32GB GDDR7"], ["Suprim X"]),
        ("NVIDIA GeForce RTX 4080 Super", "Gigabyte", 48000, ["16GB"], ["Gaming OC", "Aero"]), # НОВЕ
        ("NVIDIA GeForce RTX 4070 Ti Super", "Palit", 38000, ["16GB"], ["JetStream", "GamingPro"]), # НОВЕ
        ("NVIDIA GeForce RTX 4060 Ti", "MSI", 18000, ["8GB", "16GB"], ["Ventus 2X"]), # НОВЕ
        ("AMD Radeon RX 7900 XTX", "Sapphire", 46000, ["24GB"], ["Nitro+"]), # НОВЕ
        
        # --- CPU ---
        ("AMD Ryzen 7 7800X3D", "AMD", 18500, ["Box"], ["Silver"]), # НОВЕ (Топ для ігор)
        ("AMD Ryzen 5 7500F", "AMD", 7500, ["Tray"], ["Silver"]),
        ("Intel Core i7-14700K", "Intel", 19000, ["Box"], ["Blue"]), # НОВЕ
        ("Intel Core i5-13400F", "Intel", 8200, ["Box"], ["Blue"]),

        # --- Motherboards (НОВЕ) ---
        ("ASUS TUF GAMING B650-PLUS", "ASUS", 8500, ["WIFI"], ["Black"]),
        ("MSI B760 GAMING PLUS WIFI", "MSI", 7200, ["DDR5"], ["Black"]),
        ("Gigabyte X670 AORUS ELITE", "Gigabyte", 12500, ["AX"], ["Black"]),

        # --- RAM ---
        ("Kingston Fury Beast DDR5", "Kingston", 5200, ["32GB (2x16)"], ["Black", "White"]),
        ("G.Skill Trident Z5 Neo", "G.Skill", 6500, ["32GB (2x16)", "64GB (2x32)"], ["RGB Black"]), # НОВЕ
        
        # --- SSD ---
        ("Samsung 990 Pro", "Samsung", 5500, ["1TB", "2TB"], ["Heatsink"]),
        ("Kingston KC3000", "Kingston", 4200, ["1TB", "2TB"], ["Standard"]), # НОВЕ
        ("WD Black SN850X", "Western Digital", 4800, ["1TB", "2TB"], ["Standard"]), # НОВЕ

        # --- Cases & PSU (НОВЕ) ---
        ("Lian Li O11 Dynamic Evo", "Lian Li", 7500, ["ATX Case"], ["Black", "White"]), 
        ("DeepCool CC560", "DeepCool", 2200, ["ATX Case"], ["Black"]), 
        ("be quiet! Pure Power 12 M", "be quiet!", 5500, ["750W", "850W"], ["Black"]),
    ],
    4: [ # Аудіо
        ("Sony WH-1000XM5", "Sony", 13000, ["ANC"], ["Black", "Silver"]),
        ("Sony WH-1000XM6", "Sony", 16000, ["ANC v2"], ["Black", "Navy"]),
        ("Bose QuietComfort Ultra", "Bose", 18000, ["Immersive Audio"], ["Black", "White Smoke"]), # НОВЕ
        ("Sennheiser Momentum 4", "Sennheiser", 14500, ["Wireless"], ["Black", "White"]), # НОВЕ
        
        ("Apple AirPods Pro 2", "Apple", 10000, ["USB-C"], ["White"]),
        ("Apple AirPods Max", "Apple", 24000, ["USB-C"], ["Midnight", "Starlight", "Blue"]), # НОВЕ
        ("Samsung Galaxy Buds 3 Pro", "Samsung", 9000, ["ANC"], ["Silver", "White"]),
        
        ("JBL Tune 520BT", "JBL", 1500, ["57h Battery"], ["Black", "Blue"]), 
        ("Marshall Major V", "Marshall", 6800, ["80h Battery"], ["Black", "Brown"]),
        ("Marshall Stanmore III", "Marshall", 16000, ["Home Speaker"], ["Black", "Cream"]), # НОВЕ
        ("JBL PartyBox 110", "JBL", 14000, ["Portable"], ["Black"]), # НОВЕ
    ],
    5: [ # Геймінг
        ("Sony PlayStation 5 Slim", "Sony", 22000, ["1TB"], ["White"]), # НОВЕ
        ("Sony PlayStation 5 Pro", "Sony", 32000, ["2TB SSD"], ["White"]),
        ("Microsoft Xbox Series X", "Microsoft", 23000, ["1TB"], ["Black"]), # НОВЕ
        ("Microsoft Xbox Series S", "Microsoft", 13500, ["512GB"], ["White"]), # НОВЕ
        ("Nintendo Switch OLED", "Nintendo", 14000, ["Mario Red", "White"], ["Standard"]),
        
        ("Meta Quest 3", "Meta", 26000, ["128GB", "512GB"], ["White"]), # НОВЕ
        ("Valve Steam Deck OLED", "Valve", 26000, ["512GB"], ["Black"]),
        
        ("Logitech G502 X Plus", "Logitech", 6000, ["Wireless"], ["Black", "White"]), # НОВЕ
        ("Razer DeathAdder V3 Pro", "Razer", 6500, ["Wireless"], ["Black", "White"]), # НОВЕ
        ("SteelSeries Arctis Nova 7", "SteelSeries", 7800, ["Wireless"], ["Black"]), # НОВЕ
    ],
    6: [ # Розумний дім та Побут
        ("Roborock S8 Pro Ultra", "Roborock", 45000, ["Dock"], ["White", "Black"]), # НОВЕ
        ("Dreame L10s Ultra", "Dreame", 35000, ["Station"], ["White"]),
        ("Xiaomi Robot Vacuum S10", "Xiaomi", 8000, ["LDS"], ["White"]),
        
        ("Dyson V15 Detect Submarine", "Dyson", 38000, ["Wet&Dry"], ["Yellow"]), # НОВЕ
        ("Dyson Supersonic Nural", "Dyson", 19000, ["Hair Dryer"], ["Vinca Blue"]), # НОВЕ
        
        ("EcoFlow Delta 2", "EcoFlow", 42000, ["1024Wh"], ["Black"]),
        ("Bluetti EB3A", "Bluetti", 12000, ["268Wh"], ["Black"]), # НОВЕ
        
        ("DeLonghi Magnifica S", "DeLonghi", 16000, ["Coffee Machine"], ["Black", "Silver"]), # НОВЕ
        ("Philips Airfryer XXL", "Philips", 9000, ["Smart"], ["Black"]),
        ("Ajax StarterKit Cam Plus", "Ajax", 14000, ["Security"], ["White", "Black"]), # НОВЕ
    ],
    7: [ # Транспорт
        ("Segway Ninebot Max G2", "Ninebot", 33000, ["70km Range"], ["Black"]),
        ("Segway Ninebot E2 Plus", "Ninebot", 16000, ["25km Range"], ["Black"]), # НОВЕ
        ("Xiaomi Electric Scooter 4 Ultra", "Xiaomi", 38000, ["Suspension"], ["Black"]), # НОВЕ
        ("Xiaomi Electric Scooter 4 Lite", "Xiaomi", 14000, ["Gen 2"], ["Black"]),
        ("Proove X-City Pro", "Proove", 18000, ["Max"], ["Black/Blue"]), # НОВЕ
        ("Acer Electrical Scooter Series 5", "Acer", 19000, ["25km/h"], ["Black"]),
        ("Himo Z20 Max", "Himo", 32000, ["E-Bike"], ["Grey", "White"]), # НОВЕ
    ]
}

def generate_full_inventory() -> List[Dict[str, Any]]:
    """Генерує 600+ товарних позицій (SKU)."""
    products = []
    
    # 1. БАЗОВА ГЕНЕРАЦІЯ
    for cat_id, models in MODELS_DATA.items():
        for base_name, brand, price, configs, colors in models:
            for conf in configs:
                for color in colors:
                    final_price = float(price)
                    
                    # Логіка націнок
                    if "1TB" in conf: final_price *= 1.35
                    elif "2TB" in conf: final_price *= 1.6
                    elif "512GB" in conf and "256GB" in configs: final_price *= 1.2
                    elif "32GB" in conf and "16GB" in configs: final_price *= 1.25
                    elif "i9" in conf: final_price *= 1.4
                    elif "Pro" in base_name and "Max" in base_name: final_price *= 1.1
                    elif "Station" in conf or "Dock" in conf: final_price *= 1.3
                    
                    full_name = f"{base_name} {conf} {color}"
                    
                    # Сток
                    stock = random.randint(0, 50)
                    # Популярного більше
                    if any(x in full_name for x in ["iPhone", "AirPods", "Galaxy A", "Redmi", "PlayStation"]):
                        stock = random.randint(20, 150)
                    
                    products.append({
                        "name": full_name,
                        "price": round(final_price, 2),
                        "category_id": cat_id,
                        "stock_quantity": stock,
                        "rating": round(random.uniform(3.8, 5.0), 1),
                        "specifications": {
                            "brand": brand,
                            "configuration": conf,
                            "color": color,
                            "warranty": "12 months" if final_price < 20000 else "24 months",
                            "release_year": random.choice([2023, 2024, 2025])
                        }
                    })
    
    # 2. МАСШТАБУВАННЯ ДО 600+
    print(f"Початкова кількість унікальних SKU (Base): {len(products)}")
    
    original_products = products[:] 
    
    while len(products) < 650: # Трохи підняв ліміт
        base_item = random.choice(original_products)
        new_item = base_item.copy()
        new_item["specifications"] = base_item["specifications"].copy()
        
        variant_type = random.choice(["EU", "OpenBox", "Refurbished", "Showcase"])
        
        if variant_type == "EU":
            new_item["name"] = new_item["name"] + " (EU Version)"
            new_item["price"] = round(new_item["price"] * 0.9, 2)
            new_item["specifications"]["warranty"] = "3 months (Store)"
            
        elif variant_type == "OpenBox":
            new_item["name"] = new_item["name"] + " [Open Box]"
            new_item["price"] = round(new_item["price"] * 0.85, 2)
            new_item["specifications"]["condition"] = "Like New"
            
        elif variant_type == "Refurbished":
            new_item["name"] = new_item["name"] + " (Refurbished)"
            new_item["price"] = round(new_item["price"] * 0.75, 2)
            new_item["specifications"]["condition"] = "Factory Restored"
            new_item["specifications"]["warranty"] = "6 months"
            
        elif variant_type == "Showcase":
            new_item["name"] = new_item["name"] + " (Вітрина - Знижка)"
            new_item["price"] = round(new_item["price"] * 0.8, 2)
            new_item["stock_quantity"] = random.randint(1, 3)
            
        if not any(p["name"] == new_item["name"] for p in products):
            products.append(new_item)
            
    return products

def seed_real_database() -> None:
    db = SessionLocal()
    try:
        print("--- Очищення старої бази ---")
        db.execute(text("TRUNCATE TABLE products RESTART IDENTITY CASCADE;"))
        db.execute(text("TRUNCATE TABLE categories RESTART IDENTITY CASCADE;"))
        db.commit()

        print("--- Створення категорій ---")
        categories = [
            {"name": "Смартфони та Планшети", "description": "Телефони, планшети, аксесуари"},
            {"name": "Ноутбуки", "description": "Для роботи, навчання та ігор"},
            {"name": "Комплектуючі ПК", "description": "Залізо для збірки ПК"},
            {"name": "Аудіо", "description": "Навушники та акустика"},
            {"name": "Геймінг", "description": "Консолі, VR та периферія"},
            {"name": "Розумний дім та Побут", "description": "Техніка для дому, кавомашини"},
            {"name": "Транспорт", "description": "Електротранспорт"},
        ]
        for idx, cat in enumerate(categories, 1):
            db.add(Category(id=idx, **cat))
        db.commit()

        print("--- Генерація асортименту ---")
        all_items = generate_full_inventory()
        
        db.bulk_insert_mappings(Product, all_items)
        db.commit()
        
        print(f"✅ База успішно наповнена! Всього: {len(all_items)} товарів.")
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_real_database()