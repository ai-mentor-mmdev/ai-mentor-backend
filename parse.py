#!/usr/bin/env python3
"""
Скрипт для парсинга базы знаний и заполнения БД
Использует LLM для извлечения структуры глав из блоков
"""

import os
import re
import json
import sqlite3
import asyncio
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

import openai
from openai import AsyncOpenAI

# ========================= КОНФИГУРАЦИЯ =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
DATABASE_URL = "learning_system.db"
KNOWLEDGE_BASE_PATH = "./knowledge_base"  # Путь к базе знаний

# Инициализация OpenAI клиента
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# ========================= МОДЕЛИ ДАННЫХ =========================

@dataclass
class Chapter:
    """Глава внутри блока"""
    title: str
    content: str
    order_index: int
    estimated_minutes: int


@dataclass
class Block:
    """Блок обучения"""
    filename: str
    title: str
    content: str
    chapters: List[Chapter]
    difficulty_level: int
    estimated_minutes: int
    order_index: int


@dataclass
class Topic:
    """Тема обучения"""
    name: str
    title: str
    description: str
    intro_content: str
    edu_plan_content: str
    blocks: List[Block]
    difficulty_level: int
    order_index: int


# ========================= LLM СЕРВИС =========================

class LLMParser:
    """Сервис для парсинга контента с помощью LLM"""

    @staticmethod
    async def extract_chapters_from_block(block_content: str, block_title: str) -> List[Dict]:
        """Извлекает главы из блока используя LLM"""

        system_prompt = """
Ты эксперт по анализу образовательного контента. Твоя задача - проанализировать блок обучения и извлечь из него структуру глав.

ПРАВИЛА:
1. Найди все главы/разделы в тексте (обычно помечены заголовками #, ##, ###)
2. Для каждой главы определи:
   - Заголовок главы
   - Основное содержание главы
   - Примерное время изучения в минутах (исходя из объема текста)
3. Верни результат ТОЛЬКО в формате JSON
4. Если в блоке нет четких разделов, создай логические главы на основе содержания

ФОРМАТ ОТВЕТА (только JSON, без дополнительного текста):
{
    "chapters": [
        {
            "title": "Название главы",
            "content": "Содержание главы",
            "estimated_minutes": 15
        }
    ]
}

ВАЖНО: Отвечай ТОЛЬКО JSON, никакого дополнительного текста!
"""

        user_prompt = f"""
Блок: {block_title}

Содержание:
{block_content}

Проанализируй этот блок и извлеки структуру глав в формате JSON.
"""

        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()

            # Удаляем возможные markdown блоки
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)

            # Парсим JSON
            result = json.loads(content)
            return result.get("chapters", [])

        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON для блока {block_title}: {e}")
            print(f"Ответ LLM: {content}")
            return []
        except Exception as e:
            print(f"❌ Ошибка LLM для блока {block_title}: {e}")
            return []

    @staticmethod
    async def extract_topic_info(topic_name: str, intro_content: str, edu_plan_content: str) -> Dict:
        """Извлекает информацию о теме"""

        system_prompt = """
Ты эксперт по анализу образовательного контента. Проанализируй тему обучения и извлеки ключевую информацию.

ЗАДАЧИ:
1. Определи красивое название темы
2. Создай краткое описание (1-2 предложения)
3. Определи уровень сложности (1-5, где 1 - новичок, 5 - эксперт)

ФОРМАТ ОТВЕТА (только JSON):
{
    "title": "Красивое название темы",
    "description": "Краткое описание темы",
    "difficulty_level": 3
}
"""

        user_prompt = f"""
Тема: {topic_name}

Введение:
{intro_content[:1000]}...

План обучения:
{edu_plan_content[:1000]}...

Проанализируй и верни информацию в формате JSON.
"""

        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )

            content = response.choices[0].message.content.strip()
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)

            return json.loads(content)

        except Exception as e:
            print(f"❌ Ошибка извлечения информации о теме {topic_name}: {e}")
            return {
                "title": topic_name.replace("_", " ").title(),
                "description": f"Изучение {topic_name}",
                "difficulty_level": 3
            }


# ========================= ФАЙЛОВЫЙ ПАРСЕР =========================

class KnowledgeBaseParser:
    """Парсер базы знаний"""

    def __init__(self, knowledge_base_path: str):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.llm_parser = LLMParser()

    async def parse_knowledge_base(self) -> List[Topic]:
        """Парсит всю базу знаний"""
        topics = []

        if not self.knowledge_base_path.exists():
            print(f"❌ Путь к базе знаний не найден: {self.knowledge_base_path}")
            return topics

        # Получаем все директории (темы)
        topic_dirs = [d for d in self.knowledge_base_path.iterdir() if d.is_dir()]

        for i, topic_dir in enumerate(sorted(topic_dirs)):
            print(f"📚 Обрабатываю тему: {topic_dir.name}")

            topic = await self.parse_topic(topic_dir, i + 1)
            if topic:
                topics.append(topic)

        return topics

    async def parse_topic(self, topic_dir: Path, order_index: int) -> Optional[Topic]:
        """Парсит одну тему"""
        topic_name = topic_dir.name

        # Читаем основные файлы
        intro_content = self.read_file_safe(topic_dir / "intro.md")
        edu_plan_content = self.read_file_safe(topic_dir / "edu-plan.md")

        # Извлекаем информацию о теме с помощью LLM
        topic_info = await self.llm_parser.extract_topic_info(
            topic_name, intro_content, edu_plan_content
        )

        # Парсим блоки
        blocks = await self.parse_blocks(topic_dir)

        return Topic(
            name=topic_name,
            title=topic_info.get("title", topic_name.replace("_", " ").title()),
            description=topic_info.get("description", f"Изучение {topic_name}"),
            intro_content=intro_content,
            edu_plan_content=edu_plan_content,
            blocks=blocks,
            difficulty_level=topic_info.get("difficulty_level", 3),
            order_index=order_index
        )

    async def parse_blocks(self, topic_dir: Path) -> List[Block]:
        """Парсит блоки в теме"""
        blocks = []

        # Находим все файлы блоков
        block_files = sorted([f for f in topic_dir.iterdir()
                              if f.name.startswith("block-") and f.name.endswith(".md")])

        for i, block_file in enumerate(block_files):
            print(f"  📖 Обрабатываю блок: {block_file.name}")

            block_content = self.read_file_safe(block_file)
            if not block_content:
                continue

            # Определяем заголовок блока
            block_title = self.extract_title_from_content(block_content) or f"Блок {i + 1}"

            # Извлекаем главы с помощью LLM
            chapters_data = await self.llm_parser.extract_chapters_from_block(
                block_content, block_title
            )

            # Создаем объекты глав
            chapters = []
            total_minutes = 0

            for j, chapter_data in enumerate(chapters_data):
                chapter = Chapter(
                    title=chapter_data.get("title", f"Глава {j + 1}"),
                    content=chapter_data.get("content", ""),
                    order_index=j + 1,
                    estimated_minutes=chapter_data.get("estimated_minutes", 15)
                )
                chapters.append(chapter)
                total_minutes += chapter.estimated_minutes

            # Если главы не найдены, создаем одну главу из всего блока
            if not chapters:
                chapters = [Chapter(
                    title=block_title,
                    content=block_content,
                    order_index=1,
                    estimated_minutes=30
                )]
                total_minutes = 30

            # Определяем сложность блока
            difficulty = self.estimate_difficulty(block_content)

            block = Block(
                filename=block_file.name,
                title=block_title,
                content=block_content,
                chapters=chapters,
                difficulty_level=difficulty,
                estimated_minutes=total_minutes,
                order_index=i + 1
            )

            blocks.append(block)

        return blocks

    def read_file_safe(self, file_path: Path) -> str:
        """Безопасно читает файл"""
        try:
            if file_path.exists():
                return file_path.read_text(encoding='utf-8')
            return ""
        except Exception as e:
            print(f"❌ Ошибка чтения файла {file_path}: {e}")
            return ""

    def extract_title_from_content(self, content: str) -> Optional[str]:
        """Извлекает заголовок из содержимого"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        return None

    def estimate_difficulty(self, content: str) -> int:
        """Оценивает сложность блока"""
        # Простая эвристика на основе ключевых слов
        advanced_keywords = ['advanced', 'complex', 'enterprise', 'architecture', 'optimization']
        intermediate_keywords = ['configuration', 'setup', 'deployment', 'integration']

        content_lower = content.lower()

        advanced_count = sum(1 for word in advanced_keywords if word in content_lower)
        intermediate_count = sum(1 for word in intermediate_keywords if word in content_lower)

        if advanced_count > 0:
            return 4
        elif intermediate_count > 0:
            return 3
        else:
            return 2


# ========================= БАЗА ДАННЫХ =========================

class DatabaseManager:
    """Менеджер базы данных"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def clear_existing_data(self):
        """Очищает существующие данные"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        print("🗑️  Очищаю существующие данные...")

        # Удаляем в правильном порядке из-за внешних ключей
        cursor.execute("DELETE FROM chapters")
        cursor.execute("DELETE FROM progress")
        cursor.execute("DELETE FROM llm_requests")
        cursor.execute("DELETE FROM chat_sessions")
        cursor.execute("DELETE FROM blocks")
        cursor.execute("DELETE FROM topics")

        conn.commit()
        conn.close()

    def create_chapters_table(self):
        """Создает таблицу глав (если не существует)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS chapters
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           block_id
                           INTEGER
                           NOT
                           NULL,
                           title
                           TEXT
                           NOT
                           NULL,
                           content
                           TEXT,
                           order_index
                           INTEGER
                           DEFAULT
                           0,
                           estimated_minutes
                           INTEGER
                           DEFAULT
                           15,
                           is_active
                           BOOLEAN
                           DEFAULT
                           1,
                           FOREIGN
                           KEY
                       (
                           block_id
                       ) REFERENCES blocks
                       (
                           id
                       )
                           )
                       ''')

        conn.commit()
        conn.close()

    def save_topics(self, topics: List[Topic]):
        """Сохраняет темы в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        print("💾 Сохраняю данные в базу...")

        for topic in topics:
            # Сохраняем тему
            cursor.execute('''
                           INSERT INTO topics (title, description, difficulty_level, order_index)
                           VALUES (?, ?, ?, ?)
                           ''', (topic.title, topic.description, topic.difficulty_level, topic.order_index))

            topic_id = cursor.lastrowid

            # Сохраняем блоки
            for block in topic.blocks:
                cursor.execute('''
                               INSERT INTO blocks (topic_id, title, content, difficulty_level,
                                                   estimated_minutes, order_index)
                               VALUES (?, ?, ?, ?, ?, ?)
                               ''', (topic_id, block.title, block.content, block.difficulty_level,
                                     block.estimated_minutes, block.order_index))

                block_id = cursor.lastrowid

                # Сохраняем главы
                for chapter in block.chapters:
                    cursor.execute('''
                                   INSERT INTO chapters (block_id, title, content, order_index,
                                                         estimated_minutes)
                                   VALUES (?, ?, ?, ?, ?)
                                   ''', (block_id, chapter.title, chapter.content,
                                         chapter.order_index, chapter.estimated_minutes))

        conn.commit()
        conn.close()

    def print_statistics(self):
        """Выводит статистику по базе данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM topics")
        topics_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM blocks")
        blocks_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM chapters")
        chapters_count = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(estimated_minutes) FROM blocks")
        total_minutes = cursor.fetchone()[0] or 0

        conn.close()

        print(f"\n📊 Статистика:")
        print(f"   📚 Тем: {topics_count}")
        print(f"   📖 Блоков: {blocks_count}")
        print(f"   📄 Глав: {chapters_count}")
        print(f"   ⏱️  Общее время: {total_minutes} минут ({total_minutes / 60:.1f} часов)")


# ========================= ГЛАВНАЯ ФУНКЦИЯ =========================

async def main():
    """Главная функция парсинга"""
    print("🚀 Запуск парсинга базы знаний...")

    # Проверяем наличие API ключа
    if OPENAI_API_KEY == "your-openai-api-key":
        print("❌ Установите переменную окружения OPENAI_API_KEY")
        return

    # Инициализируем компоненты
    parser = KnowledgeBaseParser(KNOWLEDGE_BASE_PATH)
    db_manager = DatabaseManager(DATABASE_URL)

    # Создаем таблицу глав
    db_manager.create_chapters_table()

    # Очищаем существующие данные
    db_manager.clear_existing_data()

    # Парсим базу знаний
    topics = await parser.parse_knowledge_base()

    if not topics:
        print("❌ Темы не найдены")
        return

    # Сохраняем в базу данных
    db_manager.save_topics(topics)

    # Выводим статистику
    db_manager.print_statistics()

    print("\n✅ Парсинг завершен успешно!")


if __name__ == "__main__":
    asyncio.run(main())