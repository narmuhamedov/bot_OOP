class Quiz:
    def __init__(self):
        self.questions = [
            {
                "question": "Столица Франции?",
                "options": ["Берлин", "Париж", "Рим", "Мадрид"],
                "correct": "Париж"
            },
            {
                "question": "2 + 2 = ?",
                "options": ["3", "4", "5", "22"],
                "correct": "4"
            },
            {
                "question": "Самый большой океан?",
                "options": ["Атлантический", "Индийский", "Тихий", "Северный Ледовитый"],
                "correct": "Тихий"
            }
        ]

    def get_question(self, index):
        if index < len(self.questions):
            return self.questions[index]
        return None

    def total_questions(self):
        return len(self.questions)
