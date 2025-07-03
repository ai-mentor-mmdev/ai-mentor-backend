import ast
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from internal import interface, model, common

@dataclass
class Chapter:
    name: str
    content: str = ""


@dataclass
class Block:
    name: str
    file_path: Path
    content: str
    chapters: list[Chapter]


@dataclass
class Topic:
    name: str
    intro: str
    edu_plan: str
    blocks: list[Block]

class BlockParsing:
    def __init__(self, llm_client: interface.ILLMClient):
        self.knowledge_dir = "pkg/backend_knowledge"
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        self.parsed_topics: dict[str, Topic] = {}

    async def parse(self) -> dict[str, Topic]:
        self.logger.info("Начинаем полный парсинг образовательного контента")

        path = Path(self.knowledge_dir)

        if not path.exists():
            self.logger.error(f"Директория {self.knowledge_dir} не найдена")
            return {}

        for topic_dir in path.iterdir():
            if not topic_dir.is_dir():
                continue

            topic_name = topic_dir.name
            self.logger.info(f"Парсинг топика: {topic_name}")

            try:
                topic = await  self._parse_topic(topic_dir)
                self.parsed_topics[topic_name] = topic
                self.logger.info(f"Топик {topic_name} успешно распарсен")
            except Exception as e:
                self.logger.error(f"Ошибка при парсинге топика {topic_name}: {e}")
                continue

        self.logger.info(f"Парсинг завершен. Обработано {len(self.parsed_topics)} топиков")
        return self.parsed_topics

    async def _parse_topic(self, topic_dir: Path) -> Topic:
        topic_name = topic_dir.name

        intro = self._read_file_safe(topic_dir / "intro.md")
        edu_plan = self._read_file_safe(topic_dir / "edu_plan.md")

        blocks = []
        for file_path in topic_dir.iterdir():
            if file_path.is_file() and file_path.name.startswith("block-") and file_path.suffix == ".md":
                try:
                    block = self._parse_block(file_path)
                    blocks.append(block)
                except Exception as e:
                    self.logger.error(f"Ошибка при парсинге блока {file_path}: {e}")
                    continue

        return Topic(
            name=topic_name,
            intro=intro,
            edu_plan=edu_plan,
            blocks=blocks
        )

    async def _parse_block(self, file_path: Path) -> Block:
        block_name = file_path.stem
        content = self._read_file_safe(file_path)

        chapters = await self._extract_chapters_from_content(content)

        return Block(
            name=block_name,
            file_path=file_path,
            content=content,
            chapters=chapters
        )

    def _read_file_safe(self, file_path: Path) -> str:
        try:
            if file_path.exists():
                return file_path.read_text(encoding='utf-8')
            else:
                self.logger.warning(f"Файл не найден: {file_path}")
                return ""
        except Exception as e:
            self.logger.error(f"Ошибка при чтении файла {file_path}: {e}")
            return ""

    async def _extract_chapters_from_content(self, content: str) -> List[Chapter]:
        if not content.strip():
            return []

        try:
            chapter_names = await self.get_all_chapters_name(content)
            return [Chapter(name=name) for name in chapter_names]
        except Exception as e:
            self.logger.error(f"Ошибка при извлечении глав: {e}")
            return []

    async def get_all_chapters_name(self, block_content: str) -> List[str]:
            prompt = f"""Это блок обучающего материала, пришли мне просто название всех глав в виде списка. 
Формат ответа:        
[Название, Название]

БЛОК:
{block_content}
"""

            try:
                llm_response = await self.llm_client.generate(
                    [model.EduMessage(id=1, edu_chat_id=0, text=prompt, role=common.Roles.user)],
                    ""
                )
                llm_response = json.loads(llm_response)
                return llm_response
            except Exception as e:
                self.logger.error(f"Ошибка при обращении к LLM: {e}")
                return []

