import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from scheduler import start_scheduler
from config import TOKEN_TG
from handlers.start import router as start_router
from handlers.weather_edit import router as weather_edit_router
from handlers.weather_find import router as weather_find_router
from handlers.notify_add import router as notify_add_router
from handlers.notify_edit import router as notify_edit_router
from handlers.help import router as help_router
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN_TG, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

async def main():
    dp.include_router(start_router)
    dp.include_router(weather_edit_router)
    dp.include_router(weather_find_router)
    dp.include_router(notify_add_router)
    dp.include_router(notify_edit_router)
    dp.include_router(help_router)
    logger.info("Бот запущен...")
    try:
        start_scheduler(bot)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Сессия бота завершена.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Отключение бота...")
