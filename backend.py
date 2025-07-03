#!/usr/bin/env python3
"""
LLM Learning System - MVP Backend
Система обучения с ИИ экспертами в одном файле
"""

import os
import jwt
import bcrypt
import asyncio
import sqlite3
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

import uvicorn
import openai
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

# ========================= КОНФИГУРАЦИЯ =========================

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
DATABASE_URL = "learning_system.db"

# Настройка OpenAI
openai.api_key = OPENAI_API_KEY


# ========================= МОДЕЛИ ДАННЫХ =========================

class ExpertType(str, Enum):
    TUTOR = "tutor"  # Тьютор - главный эксперт
    CONTENT = "content"  # Эксперт по контенту
    PRACTICE = "practice"  # Эксперт по практике
    ASSESSMENT = "assessment"  # Эксперт по оценке
    MENTOR = "mentor"  # Ментор для поддержки


class UserRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# ========================= PYDANTIC СХЕМЫ =========================

# Auth
class UserRegister(BaseModel):
    login: str
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Student
class StudentProfile(BaseModel):
    id: int
    first_name: str
    last_name: str
    level: str
    total_xp: int


# Content
class TopicOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    difficulty_level: int
    order_index: int


class BlockOut(BaseModel):
    id: int
    title: str
    content: Optional[str]
    difficulty_level: int
    estimated_minutes: int
    order_index: int
    progress: Optional[float] = None


# LLM
class ExpertRequest(BaseModel):
    expert_type: ExpertType
    message: str
    context: Optional[Dict] = None


class ExpertResponse(BaseModel):
    response: str
    expert_type: ExpertType
    tokens_used: int
    suggested_actions: Optional[List[str]] = None


# Progress
class ProgressUpdate(BaseModel):
    block_id: int
    completion_percentage: float
    time_spent_minutes: int


# ========================= БАЗА ДАННЫХ =========================

class Database:
    def __init__(self, db_path: str = DATABASE_URL):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Таблица аккаунтов
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS accounts
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           login
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           password
                           TEXT
                           NOT
                           NULL,
                           email
                           TEXT
                           UNIQUE
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Таблица студентов
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS students
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           account_id
                           INTEGER
                           NOT
                           NULL,
                           first_name
                           TEXT
                           NOT
                           NULL,
                           last_name
                           TEXT
                           NOT
                           NULL,
                           level
                           TEXT
                           DEFAULT
                           'beginner',
                           total_xp
                           INTEGER
                           DEFAULT
                           0,
                           FOREIGN
                           KEY
                       (
                           account_id
                       ) REFERENCES accounts
                       (
                           id
                       )
                           )
                       ''')

        # Таблица тем
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS topics
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           title
                           TEXT
                           NOT
                           NULL,
                           description
                           TEXT,
                           difficulty_level
                           INTEGER
                           DEFAULT
                           1,
                           order_index
                           INTEGER
                           DEFAULT
                           0,
                           is_active
                           BOOLEAN
                           DEFAULT
                           1
                       )
                       ''')

        # Таблица блоков
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS blocks
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           topic_id
                           INTEGER
                           NOT
                           NULL,
                           title
                           TEXT
                           NOT
                           NULL,
                           content
                           TEXT,
                           difficulty_level
                           INTEGER
                           DEFAULT
                           1,
                           estimated_minutes
                           INTEGER
                           DEFAULT
                           30,
                           order_index
                           INTEGER
                           DEFAULT
                           0,
                           is_active
                           BOOLEAN
                           DEFAULT
                           1,
                           FOREIGN
                           KEY
                       (
                           topic_id
                       ) REFERENCES topics
                       (
                           id
                       )
                           )
                       ''')

        # Таблица прогресса
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS progress
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           student_id
                           INTEGER
                           NOT
                           NULL,
                           block_id
                           INTEGER
                           NOT
                           NULL,
                           completion_percentage
                           REAL
                           DEFAULT
                           0,
                           time_spent_minutes
                           INTEGER
                           DEFAULT
                           0,
                           started_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           completed_at
                           TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           student_id
                       ) REFERENCES students
                       (
                           id
                       ),
                           FOREIGN KEY
                       (
                           block_id
                       ) REFERENCES blocks
                       (
                           id
                       )
                           )
                       ''')

        # Таблица LLM запросов
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS llm_requests
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           student_id
                           INTEGER
                           NOT
                           NULL,
                           expert_type
                           TEXT
                           NOT
                           NULL,
                           prompt
                           TEXT
                           NOT
                           NULL,
                           response
                           TEXT,
                           tokens_used
                           INTEGER
                           DEFAULT
                           0,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           student_id
                       ) REFERENCES students
                       (
                           id
                       )
                           )
                       ''')

        # Таблица сессий чата
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS chat_sessions
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           student_id
                           INTEGER
                           NOT
                           NULL,
                           current_expert
                           TEXT
                           DEFAULT
                           'tutor',
                           context_data
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           updated_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           student_id
                       ) REFERENCES students
                       (
                           id
                       )
                           )
                       ''')

        conn.commit()
        conn.close()

        # Заполняем тестовые данные
        self.seed_data()

    def seed_data(self):
        """Заполнение тестовыми данными"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Проверяем, есть ли уже данные
        cursor.execute("SELECT COUNT(*) FROM topics")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return

        # Добавляем темы
        topics = [
            ("Основы Python", "Изучение базового синтаксиса Python", 1, 1),
            ("ООП в Python", "Объектно-ориентированное программирование", 2, 2),
            ("Веб-разработка с FastAPI", "Создание API с помощью FastAPI", 3, 3),
            ("Базы данных", "Работа с SQL и NoSQL базами", 2, 4),
            ("Машинное обучение", "Основы ML с Python", 4, 5)
        ]

        cursor.executemany('''
                           INSERT INTO topics (title, description, difficulty_level, order_index)
                           VALUES (?, ?, ?, ?)
                           ''', topics)

        # Добавляем блоки для первой темы
        blocks = [
            (1, "Переменные и типы данных",
             "# Переменные в Python\n\nВ Python переменные создаются просто:\n\n```python\nname = 'Иван'\nage = 25\nheight = 175.5\nis_student = True\n```",
             1, 30, 1),
            (1, "Условные операторы",
             "# Условные операторы\n\nИспользуйте if, elif, else:\n\n```python\nif age >= 18:\n    print('Совершеннолетний')\nelse:\n    print('Несовершеннолетний')\n```",
             1, 45, 2),
            (1, "Циклы",
             "# Циклы в Python\n\nFor и while циклы:\n\n```python\nfor i in range(5):\n    print(i)\n\nwhile count < 10:\n    count += 1\n```",
             2, 60, 3),
            (1, "Функции",
             "# Функции\n\nОпределение и вызов функций:\n\n```python\ndef greet(name):\n    return f'Привет, {name}!'\n\nresult = greet('Мир')\n```",
             2, 50, 4)
        ]

        cursor.executemany('''
                           INSERT INTO blocks (topic_id, title, content, difficulty_level, estimated_minutes,
                                               order_index)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''', blocks)

        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path)


# ========================= СИСТЕМА ЭКСПЕРТОВ =========================

class ExpertSystem:
    """Система ИИ экспертов для обучения"""

    @staticmethod
    def get_expert_prompt(expert_type: ExpertType, student_level: str, context: Dict = None) -> str:
        """Получить системный промпт для эксперта"""

        base_context = f"""
КТО ТЫ:
Ты один из экспертов в системе ИИ обучения LLM Learning System - {expert_type.value} эксперт.
В системе есть следующие эксперты:
- Тьютор (tutor) - главный эксперт, координирует обучение
- Эксперт по контенту (content) - объясняет материал
- Эксперт по практике (practice) - дает задания и упражнения  
- Эксперт по оценке (assessment) - проводит тестирование
- Ментор (mentor) - поддерживает мотивацию

Уровень студента: {student_level}
Твой стиль общения дружелюбный и понятный, используй простые объяснения.
Можешь использовать смайлики и примеры.
"""

        if expert_type == ExpertType.TUTOR:
            return f"""{base_context}

РОЛЬ ТЬЮТОРА:
Ты главный координатор обучения. Приветствуешь студентов, помогаешь выбрать направление изучения.

ЧТО ТЫ ДЕЛАЕШЬ:
- Знакомишься со студентом и узнаешь его цели
- Рекомендуешь подходящие темы для изучения
- Координируешь работу других экспертов
- Отвечаешь на общие вопросы об обучении

ПЕРЕКЛЮЧЕНИЕ НА ДРУГИХ ЭКСПЕРТОВ:
- На content эксперта: если нужно объяснить теорию
- На practice эксперта: если нужны практические задания
- На assessment эксперта: если нужно провести тест
- На mentor эксперта: если нужна мотивационная поддержка

КОМАНДЫ ДЛЯ ПЕРЕКЛЮЧЕНИЯ:
- "switch_to_content" - переключиться на эксперта по контенту
- "switch_to_practice" - переключиться на эксперта по практике  
- "switch_to_assessment" - переключиться на эксперта по оценке
- "switch_to_mentor" - переключиться на ментора

ПРИВЕТСТВЕННОЕ СООБЩЕНИЕ:
Представь себя и систему обучения, узнай цели студента.
"""

        elif expert_type == ExpertType.CONTENT:
            return f"""{base_context}

РОЛЬ ЭКСПЕРТА ПО КОНТЕНТУ:
Ты объясняешь теоретический материал понятно и подробно.

ЧТО ТЫ ДЕЛАЕШЬ:
- Объясняешь концепции и теорию
- Приводишь примеры кода и практические иллюстрации
- Отвечаешь на вопросы по материалу
- Разбираешь сложные темы по частям

ЧТО ЗАПРЕЩЕНО:
- Давать готовые решения задач (это делает practice эксперт)
- Проводить тестирование (это делает assessment эксперт)
- Мотивационные речи (это делает mentor)

ПЕРЕКЛЮЧЕНИЕ:
- На practice: если студент хочет практику
- На assessment: если нужно проверить знания
- На tutor: для общих вопросов
"""

        elif expert_type == ExpertType.PRACTICE:
            return f"""{base_context}

РОЛЬ ЭКСПЕРТА ПО ПРАКТИКЕ:
Ты даешь практические задания и помогаешь их решать.

ЧТО ТЫ ДЕЛАЕШЬ:
- Создаешь упражнения и задачи
- Проверяешь код студента
- Даешь подсказки, но не готовые решения
- Предлагаешь пошаговые алгоритмы

ПРИНЦИПЫ:
- Не давай готовые ответы, направляй к решению
- Разбивай сложные задачи на простые шаги
- Поощряй попытки решения

ПЕРЕКЛЮЧЕНИЕ:
- На content: если нужно объяснить теорию
- На assessment: если нужно оценить результат
- На mentor: если студент расстроен
"""

        elif expert_type == ExpertType.ASSESSMENT:
            return f"""{base_context}

РОЛЬ ЭКСПЕРТА ПО ОЦЕНКЕ:
Ты проводишь тестирование и оцениваешь знания.

ЧТО ТЫ ДЕЛАЕШЬ:
- Создаешь тесты и вопросы
- Оцениваешь ответы студента
- Даешь обратную связь по результатам
- Определяешь пробелы в знаниях

ПРИНЦИПЫ:
- Будь объективным, но поддерживающим
- Указывай на ошибки конструктивно
- Предлагай что изучить дополнительно

ПЕРЕКЛЮЧЕНИЕ:
- На content: если нужно объяснить ошибки
- На practice: если нужно больше практики
- На mentor: если студент расстроен результатами
"""

        elif expert_type == ExpertType.MENTOR:
            return f"""{base_context}

РОЛЬ МЕНТОРА:
Ты поддерживаешь мотивацию и помогаешь преодолевать трудности.

ЧТО ТЫ ДЕЛАЕШЬ:
- Мотивируешь и поддерживаешь
- Помогаешь справиться с фрустрацией
- Даешь советы по обучению
- Празднуешь успехи студента

ПРИНЦИПЫ:
- Всегда позитивен и поддерживающ
- Напоминаешь о прогрессе и достижениях
- Даешь практические советы по learning

ПЕРЕКЛЮЧЕНИЕ:
- На tutor: для планирования обучения
- На content: если нужны объяснения
- На practice: если готов к практике
"""

        return base_context

    @staticmethod
    def should_switch_expert(response: str) -> Optional[ExpertType]:
        """Проверить, нужно ли переключиться на другого эксперта"""
        switch_commands = {
            "switch_to_content": ExpertType.CONTENT,
            "switch_to_practice": ExpertType.PRACTICE,
            "switch_to_assessment": ExpertType.ASSESSMENT,
            "switch_to_mentor": ExpertType.MENTOR,
            "switch_to_tutor": ExpertType.TUTOR
        }

        for command, expert_type in switch_commands.items():
            if command in response:
                return expert_type

        return None


# ========================= СЕРВИСЫ =========================

class AuthService:
    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.now() + timedelta(hours=24)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return payload.get("sub")
        except jwt.PyJWTError:
            return None


class LLMService:
    @staticmethod
    async def generate_response(
            messages: List[Dict],
            system_prompt: str,
            temperature: float = 0.7
    ) -> Tuple[str, int]:
        """Генерация ответа от LLM"""
        try:
            full_messages = [{"role": "system", "content": system_prompt}] + messages

            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=full_messages,
                max_tokens=1000,
                temperature=temperature
            )

            content = response.choices[0].message.content
            tokens = response.usage.total_tokens

            return content, tokens

        except Exception as e:
            return f"Извините, произошла ошибка: {str(e)}", 0


# ========================= FASTAPI ПРИЛОЖЕНИЕ =========================

app = FastAPI(title="LLM Learning System", version="1.0.0")
security = HTTPBearer()
db = Database()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================= DEPENDENCY =========================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_id = AuthService.verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT s.*
                   FROM students s
                            JOIN accounts a ON s.account_id = a.id
                   WHERE a.id = ?
                   """, (user_id,))

    student = cursor.fetchone()
    conn.close()

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "id": student[0],
        "account_id": student[1],
        "first_name": student[2],
        "last_name": student[3],
        "level": student[4],
        "total_xp": student[5]
    }


# ========================= AUTH ENDPOINTS =========================

@app.post("/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    conn = db.get_connection()
    cursor = conn.cursor()

    # Проверяем существование пользователя
    cursor.execute("SELECT id FROM accounts WHERE login = ?", (user_data.login,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Login already exists")

    # Создаем аккаунт
    hashed_password = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()
    cursor.execute("""
                   INSERT INTO accounts (login, email, password)
                   VALUES (?, ?, ?)
                   """, (user_data.login, user_data.email, hashed_password))

    account_id = cursor.lastrowid

    # Создаем профиль студента
    cursor.execute("""
                   INSERT INTO students (account_id, first_name, last_name)
                   VALUES (?, ?, ?)
                   """, (account_id, user_data.first_name, user_data.last_name))

    conn.commit()
    conn.close()

    access_token = AuthService.create_access_token(data={"sub": account_id})
    return {"access_token": access_token}


@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, password FROM accounts WHERE login = ?", (user_data.login,))
    account = cursor.fetchone()
    conn.close()

    if not account or not bcrypt.checkpw(user_data.password.encode(), account[1].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = AuthService.create_access_token(data={"sub": account[0]})
    return {"access_token": access_token}


# ========================= STUDENT ENDPOINTS =========================

@app.get("/students/profile", response_model=StudentProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    return StudentProfile(**current_user)


# ========================= CONTENT ENDPOINTS =========================

@app.get("/topics", response_model=List[TopicOut])
async def get_topics():
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT id, title, description, difficulty_level, order_index
                   FROM topics
                   WHERE is_active = 1
                   ORDER BY order_index
                   """)
    topics = cursor.fetchall()
    conn.close()

    return [TopicOut(
        id=t[0], title=t[1], description=t[2],
        difficulty_level=t[3], order_index=t[4]
    ) for t in topics]


@app.get("/topics/{topic_id}/blocks", response_model=List[BlockOut])
async def get_topic_blocks(topic_id: int, current_user: dict = Depends(get_current_user)):
    conn = db.get_connection()
    cursor = conn.cursor()

    # Получаем блоки
    cursor.execute("""
                   SELECT id, title, content, difficulty_level, estimated_minutes, order_index
                   FROM blocks
                   WHERE topic_id = ?
                     AND is_active = 1
                   ORDER BY order_index
                   """, (topic_id,))
    blocks = cursor.fetchall()

    result = []
    for block in blocks:
        # Получаем прогресс
        cursor.execute("""
                       SELECT completion_percentage
                       FROM progress
                       WHERE student_id = ?
                         AND block_id = ?
                       """, (current_user["id"], block[0]))

        progress_row = cursor.fetchone()
        progress = progress_row[0] if progress_row else 0

        result.append(BlockOut(
            id=block[0], title=block[1], content=block[2],
            difficulty_level=block[3], estimated_minutes=block[4],
            order_index=block[5], progress=progress
        ))

    conn.close()
    return result


@app.get("/blocks/{block_id}", response_model=BlockOut)
async def get_block(block_id: int):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT id, title, content, difficulty_level, estimated_minutes, order_index
                   FROM blocks
                   WHERE id = ?
                   """, (block_id,))

    block = cursor.fetchone()
    conn.close()

    if not block:
        raise HTTPException(status_code=404, detail="Block not found")

    return BlockOut(
        id=block[0], title=block[1], content=block[2],
        difficulty_level=block[3], estimated_minutes=block[4],
        order_index=block[5]
    )


# ========================= EXPERT SYSTEM ENDPOINTS =========================

@app.post("/experts/chat", response_model=ExpertResponse)
async def chat_with_expert(
        request: ExpertRequest,
        current_user: dict = Depends(get_current_user)
):
    conn = db.get_connection()
    cursor = conn.cursor()

    # Получаем или создаем сессию
    cursor.execute("""
                   SELECT id, current_expert, context_data
                   FROM chat_sessions
                   WHERE student_id = ?
                   ORDER BY updated_at DESC LIMIT 1
                   """, (current_user["id"],))

    session = cursor.fetchone()

    if not session:
        # Создаем новую сессию
        cursor.execute("""
                       INSERT INTO chat_sessions (student_id, current_expert, context_data)
                       VALUES (?, ?, '{}')
                       """, (current_user["id"], request.expert_type.value))
        session_id = cursor.lastrowid
        current_expert = request.expert_type.value
        context_data = "{}"
    else:
        session_id = session[0]
        current_expert = session[1]
        context_data = session[2] or "{}"

    # Получаем системный промпт
    system_prompt = ExpertSystem.get_expert_prompt(
        ExpertType(current_expert),
        current_user["level"],
        request.context
    )

    # Получаем историю последних сообщений
    cursor.execute("""
                   SELECT prompt, response
                   FROM llm_requests
                   WHERE student_id = ?
                   ORDER BY created_at DESC LIMIT 10
                   """, (current_user["id"],))

    history = cursor.fetchall()
    messages = []

    # Преобразуем историю в формат для LLM
    for h in reversed(history):
        messages.append({"role": "user", "content": h[0]})
        if h[1]:
            messages.append({"role": "assistant", "content": h[1]})

    # Добавляем текущее сообщение
    messages.append({"role": "user", "content": request.message})

    # Генерируем ответ
    response, tokens = await LLMService.generate_response(
        messages, system_prompt, 0.7
    )

    # Проверяем на переключение эксперта
    new_expert = ExpertSystem.should_switch_expert(response)
    if new_expert:
        current_expert = new_expert.value
        # Очищаем команду из ответа
        for command in ["switch_to_content", "switch_to_practice", "switch_to_assessment", "switch_to_mentor",
                        "switch_to_tutor"]:
            response = response.replace(command, "")
        response = response.strip()

        # Обновляем сессию
        cursor.execute("""
                       UPDATE chat_sessions
                       SET current_expert = ?,
                           updated_at     = CURRENT_TIMESTAMP
                       WHERE id = ?
                       """, (current_expert, session_id))

    # Сохраняем запрос
    cursor.execute("""
                   INSERT INTO llm_requests (student_id, expert_type, prompt, response, tokens_used)
                   VALUES (?, ?, ?, ?, ?)
                   """, (current_user["id"], current_expert, request.message, response, tokens))

    # Добавляем XP
    cursor.execute("""
                   UPDATE students
                   SET total_xp = total_xp + ?
                   WHERE id = ?
                   """, (1, current_user["id"]))

    conn.commit()
    conn.close()

    # Предлагаем действия в зависимости от эксперта
    suggested_actions = []
    expert_enum = ExpertType(current_expert)

    if expert_enum == ExpertType.TUTOR:
        suggested_actions = ["Изучить материал", "Выполнить задание", "Пройти тест"]
    elif expert_enum == ExpertType.CONTENT:
        suggested_actions = ["Задать вопрос", "Перейти к практике", "Вернуться к тьютору"]
    elif expert_enum == ExpertType.PRACTICE:
        suggested_actions = ["Получить подсказку", "Проверить решение", "Изучить теорию"]
    elif expert_enum == ExpertType.ASSESSMENT:
        suggested_actions = ["Пройти тест", "Повторить материал", "Получить обратную связь"]
    elif expert_enum == ExpertType.MENTOR:
        suggested_actions = ["Продолжить обучение", "Поставить цель", "Отпраздновать успех"]

    return ExpertResponse(
        response=response,
        expert_type=ExpertType(current_expert),
        tokens_used=tokens,
        suggested_actions=suggested_actions
    )


# ========================= PROGRESS ENDPOINTS =========================

@app.post("/progress/update")
async def update_progress(
        progress_data: ProgressUpdate,
        current_user: dict = Depends(get_current_user)
):
    conn = db.get_connection()
    cursor = conn.cursor()

    # Проверяем существующий прогресс
    cursor.execute("""
                   SELECT id
                   FROM progress
                   WHERE student_id = ?
                     AND block_id = ?
                   """, (current_user["id"], progress_data.block_id))

    existing = cursor.fetchone()

    if existing:
        # Обновляем
        cursor.execute("""
                       UPDATE progress
                       SET completion_percentage = ?,
                           time_spent_minutes    = time_spent_minutes + ?,
                           completed_at          = CASE
                                                       WHEN ? >= 100 THEN CURRENT_TIMESTAMP
                                                       ELSE completed_at
                               END
                       WHERE id = ?
                       """, (
                           progress_data.completion_percentage,
                           progress_data.time_spent_minutes,
                           progress_data.completion_percentage,
                           existing[0]
                       ))
    else:
        # Создаем новый
        completed_at = None
        if progress_data.completion_percentage >= 100:
            completed_at = datetime.utcnow().isoformat()

        cursor.execute("""
                       INSERT INTO progress (student_id, block_id, completion_percentage, time_spent_minutes,
                                             completed_at)
                       VALUES (?, ?, ?, ?, ?)
                       """, (
                           current_user["id"],
                           progress_data.block_id,
                           progress_data.completion_percentage,
                           progress_data.time_spent_minutes,
                           completed_at
                       ))

    # Награждаем XP за завершение
    if progress_data.completion_percentage >= 100:
        cursor.execute("""
                       UPDATE students
                       SET total_xp = total_xp + ?
                       WHERE id = ?
                       """, (10, current_user["id"]))

    conn.commit()
    conn.close()

    return {"status": "updated"}


@app.get("/students/progress")
async def get_student_progress(current_user: dict = Depends(get_current_user)):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
                   SELECT p.block_id,
                          p.completion_percentage,
                          p.time_spent_minutes,
                          p.started_at,
                          p.completed_at,
                          b.title
                   FROM progress p
                            JOIN blocks b ON p.block_id = b.id
                   WHERE p.student_id = ?
                   ORDER BY p.started_at DESC
                   """, (current_user["id"],))

    progress = cursor.fetchall()
    conn.close()

    return [
        {
            "block_id": p[0],
            "completion_percentage": p[1],
            "time_spent_minutes": p[2],
            "started_at": p[3],
            "completed_at": p[4],
            "block_title": p[5]
        }
        for p in progress
    ]


# ========================= UTILITY ENDPOINTS =========================

@app.get("/")
async def root():
    return {
        "message": "LLM Learning System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ========================= ЗАПУСК =========================

if __name__ == "__main__":
    print("🚀 Запуск LLM Learning System...")
    print("📚 Доступно на: http://localhost:8000")
    print("📖 Документация: http://localhost:8000/docs")
    print("\n💡 Система экспертов:")
    print("   🎓 Tutor - главный координатор")
    print("   📝 Content - объяснения материала")
    print("   ⚡ Practice - практические задания")
    print("   ✅ Assessment - тестирование")
    print("   🌟 Mentor - мотивационная поддержка")

    uvicorn.run(app, host="0.0.0.0", port=8000)