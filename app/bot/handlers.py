# app/bot/handlers.py
import asyncio
import logging
from typing import List

from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from app.services import ai_engine, logger
from app.bot.keyboards import main_menu

router = Router()

def split_text(text: str, max_len: int = 4000) -> List[str]:
    """Розбиває довгий текст на шматки."""
    if len(text) <= max_len: return [text]
    parts = []
    while text:
        if len(text) <= max_len:
            parts.append(text)
            break
        split_at = text.rfind('\n', 0, max_len)
        if split_at == -1: split_at = text.rfind(' ', 0, max_len)
        if split_at == -1: split_at = max_len
        parts.append(text[:split_at])
        text = text[split_at:].lstrip()
    return parts

@router.message(CommandStart())
async def start_handler(message: types.Message) -> None:
    ai_engine.reset_session(message.from_user.id)
    
    await message.answer(
        "👋 <b>Привіт! Я AI-помічник магазину.</b>\n\n"
        "Я можу проконсультувати вас щодо техніки, або оберіть дію в меню нижче:",
        reply_markup=main_menu() 
    )


@router.message(F.text == "📦 Мої замовлення")
async def my_orders(message: types.Message):
    await message.answer("🔍 Ця функція в розробці. Тут буде список ваших покупок.")

@router.message(F.text == "↩️ Повернення товару")
async def returns_info(message: types.Message):
    await message.answer(
        "<b>Політика повернення:</b>\n"
        "Ви можете повернути товар протягом 14 днів, якщо він не був у використанні.\n\n"
        "Для оформлення напишіть на email: support@shop.com"
    )

@router.message(F.text == "📄 Договори (Оферта)")
async def contracts_info(message: types.Message):
    await message.answer("📜 Публічна оферта доступна за посиланням: https://example.com/oferta")

@router.message(F.text == "🆘 Проблема з замовленням")
async def order_issues(message: types.Message):
    # 1. Скидаємо контекст (щоб AI не думав, що ми все ще обираємо мишку)
    ai_engine.reset_session(message.from_user.id)
    
    # 2. Задаємо питання, яке спонукає описати проблему
    await message.answer(
        "Ох, мені дуже шкода, що виникли складнощі! 😔\n\n"
        "Я — штучний інтелект, але я прочитав усі інструкції до наших товарів. "
        "Часто проблему можна вирішити за хвилину.\n\n"
        "<b>Опишіть, будь ласка, що саме сталося?</b> (Наприклад: <i>'навушники не заряджаються'</i> або <i>'мишка не світиться'</i>)",
        parse_mode=ParseMode.HTML
    )

@router.message(F.text == "🤖 Консультація AI")
async def ai_help(message: types.Message):
    await message.answer("Я вас слухаю! Просто напишіть, який товар ви шукаєте, або задайте питання.")

@router.message()
async def chat_handler(message: types.Message) -> None:
    user_id = message.from_user.id
    user_input = message.text or ""


    if not user_input: return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    try:
        result = await asyncio.to_thread(ai_engine.process_message, user_id, user_input)
        answer_text = result["text"]
        tokens_used = result["tokens"]

        response_parts = split_text(answer_text)
        for part in response_parts:
            try:
                await message.answer(part, parse_mode=ParseMode.HTML)
            except:
                await message.answer(part, parse_mode=None)

        await asyncio.to_thread(
            logger.log_conversation,
            user_query=user_input,
            ai_response=answer_text,
            tokens=tokens_used,
            debug_info="Menu Mode"
        )

    except Exception as e:
        logging.error(f"Bot Error: {e}")
        await message.answer("Щось пішло не так... Спробуйте пізніше.")