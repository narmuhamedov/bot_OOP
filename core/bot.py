from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from core.handlers import BotHandlers


class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.dp = Dispatcher(storage=MemoryStorage())
        # Передаем экземпляр бота в обработчики
        self.handlers = BotHandlers(self.bot)

    
    def register_handlers(self):
        self.dp.include_router(self.handlers.router)
    
    async def start(self):
        self.register_handlers()
        await self.dp.start_polling(self.bot)