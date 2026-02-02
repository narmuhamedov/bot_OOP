from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from core.quiz import Quiz
from core.roulette import RussianRouletteGame

class BotHandlers:
    def __init__(self, bot):
        self.router = Router()
        self.bot = bot  # Сохраняем экземпляр бота
        self.quiz = Quiz()
        self.user_data = {}  # хранение состояния пользователей

        self.roulette_games = {}

        self.register_handlers()


    def register_handlers(self):
        self.router.message.register(self.start_command, Command("start"))
        self.router.message.register(self.start_quiz, Command("quiz"))

        self.router.message.register(self.start_roulette, Command("roulette"))

        self.router.message.register(self.shoot_roulette, Command("shoot"))
        self.router.message.register(self.stop_roulette, Command("stop"))
        
        self.router.callback_query.register(self.handle_answer)

    # --- Команда старт ---
    async def start_command(self, message: types.Message):
        await message.answer(
            "Привет 👋\n"
            "Напиши /quiz чтобы начать викторину 🎯"
        )

    # --- Запуск викторины ---
    async def start_quiz(self, message: types.Message):
        user_id = message.from_user.id
        self.user_data[user_id] = {"score": 0, "q_index": 0}
        await self.send_question(message.chat.id, user_id)

    # --- Отправка вопроса ---
    async def send_question(self, chat_id, user_id):
        data = self.user_data[user_id]
        question_data = self.quiz.get_question(data["q_index"])

        if not question_data:
            await self.finish_quiz(chat_id, user_id)
            return

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=opt, callback_data=opt)]
                for opt in question_data["options"]
            ]
        )

        # Используем сохраненный экземпляр бота
        await self.bot.send_message(chat_id, question_data["question"], reply_markup=keyboard)

    # --- Обработка ответа ---
    async def handle_answer(self, callback: types.CallbackQuery):
        user_id = callback.from_user.id
        data = self.user_data.get(user_id)

        if not data:
            await callback.answer("Сначала начни викторину через /quiz")
            return

        question_data = self.quiz.get_question(data["q_index"])
        selected_answer = callback.data

        if selected_answer == question_data["correct"]:
            data["score"] += 1

        data["q_index"] += 1

        await callback.answer("Ответ принят!")
        await self.send_question(callback.message.chat.id, user_id)

    # --- Завершение викторины ---
    async def finish_quiz(self, chat_id, user_id):
        score = self.user_data[user_id]["score"]
        total = self.quiz.total_questions()

        await self.bot.send_message(chat_id, f"🏁 Викторина окончена!\nТвой результат: {score} из {total}")

        del self.user_data[user_id]
    

    #Для игры рулетка
    async def start_roulette(self, message: types.Message):
        user_id = message.from_user.id
        game = RussianRouletteGame()
        self.roulette_games[user_id] = game

        await message.answer(
            "Игра началась!\n"
            "В барабане 1 патрон из 6 ....\n"
            "Нажми на /shoot чтобы стрельнуть или /stop чтобы закончить игру!"
        )
    
    #метод выстрела
    async def shoot_roulette(self, message:types.Message):
        user_id = message.from_user.id
        game = self.roulette_games.get(user_id)

        if not game:
            await message.answer("сначала выполни команду  /roulette")
            return

        result = game.shoot()

        if result == 'click':
            await message.answer(f'Пусто тебе повезло! Ваши очки - {game.score}')
        
        elif result == 'boom':
            await message.answer(f'Тебе не повезло! Игра окончена! Ваши очки - {game.score}')
            del self.roulette_games[user_id]

    
    #Метод для принудительной остановки игры
    async def stop_roulette(self, message: types.Message):
        user_id = message.from_user.id
        game = self.roulette_games.get(user_id)


        if not game:
            await message.answer('Игра не запущена!')
            return
        
        score = game.stop()
        await message.answer(f'Ты остановил игру принудительно! ваши очки - {score}')
        del self.roulette_games[user_id]
