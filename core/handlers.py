from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from core.quiz import Quiz
from core.roulette import RussianRouletteGame
from core.database import Database
from core.todo import TodoService


class BotHandlers:
    def __init__(self, bot):
        self.router = Router()
        self.bot = bot

        self.quiz = Quiz()
        self.user_data = {}

        self.roulette_games = {}

        self.db = Database()
        self.todo = TodoService(self.db)

        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start_command, Command("start"))

        # quiz
        self.router.message.register(self.start_quiz, Command("quiz"))
        self.router.callback_query.register(self.handle_answer)

        # roulette
        self.router.message.register(self.start_roulette, Command("roulette"))
        self.router.message.register(self.shoot_roulette, Command("shoot"))
        self.router.message.register(self.stop_roulette, Command("stop"))

        # todo
        self.router.message.register(self.add_todo, Command("add"))
        self.router.message.register(self.list_todo, Command("list"))
        self.router.message.register(self.done_todo, Command("done"))
        self.router.message.register(self.delete_todo, Command("delete"))

    # ---------- TODO ----------
    async def add_todo(self, message: types.Message):
        text = message.text.replace("/add", "").strip()
        if not text:
            await message.answer("Используй: /add текст")
            return

        self.todo.add(message.from_user.id, text)
        await message.answer("✅ Задача добавлена")

    async def list_todo(self, message: types.Message):
        todos = self.todo.get_all(message.from_user.id)
        if not todos:
            await message.answer("📭 Список пуст")
            return

        result = []
        for todo_id, text, is_done in todos:
            status = "✅" if is_done else "⏳"
            result.append(f"{todo_id}. {text} {status}")

        await message.answer("\n".join(result))

    async def done_todo(self, message: types.Message):
        try:
            todo_id = int(message.text.split()[1])
        except:
            await message.answer("Используй: /done id")
            return

        self.todo.mark_done(todo_id, message.from_user.id)
        await message.answer("✅ Выполнено")

    async def delete_todo(self, message: types.Message):
        try:
            todo_id = int(message.text.split()[1])
        except:
            await message.answer("Используй: /delete id")
            return

        self.todo.delete(todo_id, message.from_user.id)
        await message.answer("🗑️ Удалено")
#
    # ---------- START ----------
    async def start_command(self, message: types.Message):
        await message.answer(
            "Привет 👋\n"
            "/quiz — викторина\n"
            "/roulette — русская рулетка\n"
            "/add — добавить задачу\n"
            "/list — список задач"
        )

    # ---------- QUIZ ----------
    async def start_quiz(self, message: types.Message):
        user_id = message.from_user.id
        self.user_data[user_id] = {"score": 0, "q_index": 0}
        await self.send_question(message.chat.id, user_id)

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

        await self.bot.send_message(
            chat_id,
            question_data["question"],
            reply_markup=keyboard
        )

    async def handle_answer(self, callback: types.CallbackQuery):
        user_id = callback.from_user.id
        data = self.user_data.get(user_id)

        if not data:
            await callback.answer("Сначала /quiz")
            return

        question_data = self.quiz.get_question(data["q_index"])

        if callback.data == question_data["correct"]:
            data["score"] += 1

        data["q_index"] += 1
        await callback.answer()
        await self.send_question(callback.message.chat.id, user_id)

    async def finish_quiz(self, chat_id, user_id):
        score = self.user_data[user_id]["score"]
        total = self.quiz.total_questions()

        await self.bot.send_message(
            chat_id,
            f"🏁 Викторина окончена!\nРезультат: {score}/{total}"
        )

        del self.user_data[user_id]

    # ---------- ROULETTE ----------
    async def start_roulette(self, message: types.Message):
        user_id = message.from_user.id
        self.roulette_games[user_id] = RussianRouletteGame()

        await message.answer(
            "Игра началась!\n"
            "1 патрон из 6\n"
            "/shoot — выстрел\n"
            "/stop — остановка"
        )

    async def shoot_roulette(self, message: types.Message):
        user_id = message.from_user.id
        game = self.roulette_games.get(user_id)

        if not game:
            await message.answer("Сначала /roulette")
            return

        result = game.shoot()

        if result == "click":
            await message.answer(f"😅 Пусто! Очки: {game.score}")
        else:
            await message.answer(f"💥 БУМ! Очки: {game.score}")
            del self.roulette_games[user_id]

    async def stop_roulette(self, message: types.Message):
        user_id = message.from_user.id
        game = self.roulette_games.get(user_id)

        if not game:
            await message.answer("Игра не запущена")
            return

        score = game.stop()
        await message.answer(f"⛔ Игра остановлена. Очки: {score}")
        del self.roulette_games[user_id]
