import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import Config
from app.bot.handlers import router as main_router

async def main() -> None:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.info("🚀 Starting AI Shop Bot (Enterprise Version)...")

    #Ініціалізація бота
    bot = Bot(
        token=Config.BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    dp = Dispatcher()
    dp.include_router(main_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped manually")