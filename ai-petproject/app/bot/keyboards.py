from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🤖 Консультація AI"),
                KeyboardButton(text="📦 Мої замовлення")
            ],
            [
                KeyboardButton(text="↩️ Повернення товару"),
                KeyboardButton(text="🆘 Проблема з замовленням")
            ],
            [
                KeyboardButton(text="📄 Договори (Оферта)")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Оберіть пункт меню...",
        is_persistent=True  
    )