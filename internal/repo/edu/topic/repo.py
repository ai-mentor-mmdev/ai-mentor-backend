# internal/repo/edu/topic/repo.py

from typing import Optional, List
from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import interface, model
from .query import *


class TopicRepo(interface.ITopicRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.db = db

    # Операции с темами (Topics)
    async def create_topic(self, name: str, intro: str, edu_plan: str) -> int:
        """Создает новую тему"""
        with self.tracer.start_as_current_span(
                "TopicRepo.create_topic",
                kind=SpanKind.INTERNAL,
                attributes={
                    "name": name,
                    "intro_length": len(intro),
                    "edu_plan_length": len(edu_plan)
                }
        ) as span:
            try:
                topic_id = await self.db.insert(
                    create_topic_query,
                    {
                        "name": name,
                        "intro": intro,
                        "edu_plan": edu_plan
                    }
                )

                span.set_attribute("topic_id", topic_id)
                span.set_status(Status(StatusCode.OK))
                return topic_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_topic_by_id(self, topic_id: int) -> Optional[model.Topic]:
        """Получает тему по ID"""
        with self.tracer.start_as_current_span(
                "TopicRepo.get_topic_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "topic_id": topic_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_topic_by_id_query,
                    {"topic_id": topic_id}
                )

                if rows:
                    topics = model.Topic.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return topics[0]
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_all_topics(self) -> List[model.Topic]:
        """Получает все темы"""
        with self.tracer.start_as_current_span(
                "TopicRepo.get_all_topics",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rows = await self.db.select(get_all_topics_query, {})

                topics = model.Topic.serialize(rows)
                span.set_attribute("topics_count", len(topics))
                span.set_status(Status(StatusCode.OK))
                return topics
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_topic(self, topic_id: int, name: str = None, intro: str = None, edu_plan: str = None) -> None:
        """Обновляет тему"""
        with self.tracer.start_as_current_span(
                "TopicRepo.update_topic",
                kind=SpanKind.INTERNAL,
                attributes={
                    "topic_id": topic_id,
                    "name_updated": name is not None,
                    "intro_updated": intro is not None,
                    "edu_plan_updated": edu_plan is not None
                }
        ) as span:
            try:
                await self.db.update(
                    update_topic_query,
                    {
                        "topic_id": topic_id,
                        "name": name,
                        "intro": intro,
                        "edu_plan": edu_plan
                    }
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_topic(self, topic_id: int) -> None:
        """Удаляет тему"""
        with self.tracer.start_as_current_span(
                "TopicRepo.delete_topic",
                kind=SpanKind.INTERNAL,
                attributes={
                    "topic_id": topic_id
                }
        ) as span:
            try:
                await self.db.delete(
                    delete_topic_query,
                    {"topic_id": topic_id}
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # Операции с блоками (Blocks)
    async def create_block(self, topic_id: int, name: str, content: str) -> int:
        """Создает новый блок"""
        with self.tracer.start_as_current_span(
                "TopicRepo.create_block",
                kind=SpanKind.INTERNAL,
                attributes={
                    "topic_id": topic_id,
                    "name": name,
                    "content_length": len(content)
                }
        ) as span:
            try:
                block_id = await self.db.insert(
                    create_block_query,
                    {
                        "topic_id": topic_id,
                        "name": name,
                        "content": content
                    }
                )

                span.set_attribute("block_id", block_id)
                span.set_status(Status(StatusCode.OK))
                return block_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_block_by_id(self, block_id: int) -> Optional[model.Block]:
        """Получает блок по ID"""
        with self.tracer.start_as_current_span(
                "TopicRepo.get_block_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "block_id": block_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_block_by_id_query,
                    {"block_id": block_id}
                )

                if rows:
                    blocks = model.Block.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return blocks[0]
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_blocks_by_topic_id(self, topic_id: int) -> List[model.Block]:
        """Получает все блоки по ID темы"""
        with self.tracer.start_as_current_span(
                "TopicRepo.get_blocks_by_topic_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "topic_id": topic_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_blocks_by_topic_id_query,
                    {"topic_id": topic_id}
                )

                blocks = model.Block.serialize(rows)
                span.set_attribute("blocks_count", len(blocks))
                span.set_status(Status(StatusCode.OK))
                return blocks
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_block(self, block_id: int, name: str = None, content: str = None) -> None:
        """Обновляет блок"""
        with self.tracer.start_as_current_span(
                "TopicRepo.update_block",
                kind=SpanKind.INTERNAL,
                attributes={
                    "block_id": block_id,
                    "name_updated": name is not None,
                    "content_updated": content is not None
                }
        ) as span:
            try:
                await self.db.update(
                    update_block_query,
                    {
                        "block_id": block_id,
                        "name": name,
                        "content": content
                    }
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_block(self, block_id: int) -> None:
        """Удаляет блок"""
        with self.tracer.start_as_current_span(
                "TopicRepo.delete_block",
                kind=SpanKind.INTERNAL,
                attributes={
                    "block_id": block_id
                }
        ) as span:
            try:
                await self.db.delete(
                    delete_block_query,
                    {"block_id": block_id}
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # Операции с главами (Chapters)
    async def create_chapter(self, topic_id: int, block_id: int, name: str, content: str) -> int:
        """Создает новую главу"""
        with self.tracer.start_as_current_span(
                "TopicRepo.create_chapter",
                kind=SpanKind.INTERNAL,
                attributes={
                    "topic_id": topic_id,
                    "block_id": block_id,
                    "name": name,
                    "content_length": len(content)
                }
        ) as span:
            try:
                chapter_id = await self.db.insert(
                    create_chapter_query,
                    {
                        "topic_id": topic_id,
                        "block_id": block_id,
                        "name": name,
                        "content": content
                    }
                )

                span.set_attribute("chapter_id", chapter_id)
                span.set_status(Status(StatusCode.OK))
                return chapter_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_chapter_by_id(self, chapter_id: int) -> Optional[model.Chapter]:
        """Получает главу по ID"""
        with self.tracer.start_as_current_span(
                "TopicRepo.get_chapter_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chapter_id": chapter_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_chapter_by_id_query,
                    {"chapter_id": chapter_id}
                )

                if rows:
                    chapters = model.Chapter.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return chapters[0]
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_chapters_by_block_id(self, block_id: int) -> List[model.Chapter]:
        """Получает все главы по ID блока"""
        with self.tracer.start_as_current_span(
                "TopicRepo.get_chapters_by_block_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "block_id": block_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_chapters_by_block_id_query,
                    {"block_id": block_id}
                )

                chapters = model.Chapter.serialize(rows)
                span.set_attribute("chapters_count", len(chapters))
                span.set_status(Status(StatusCode.OK))
                return chapters
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_chapters_by_topic_id(self, topic_id: int) -> List[model.Chapter]:
        """Получает все главы по ID темы"""
        with self.tracer.start_as_current_span(
                "TopicRepo.get_chapters_by_topic_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "topic_id": topic_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_chapters_by_topic_id_query,
                    {"topic_id": topic_id}
                )

                chapters = model.Chapter.serialize(rows)
                span.set_attribute("chapters_count", len(chapters))
                span.set_status(Status(StatusCode.OK))
                return chapters
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_chapter(self, chapter_id: int, name: str = None, content: str = None) -> None:
        """Обновляет главу"""
        with self.tracer.start_as_current_span(
                "TopicRepo.update_chapter",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chapter_id": chapter_id,
                    "name_updated": name is not None,
                    "content_updated": content is not None
                }
        ) as span:
            try:
                await self.db.update(
                    update_chapter_query,
                    {
                        "chapter_id": chapter_id,
                        "name": name,
                        "content": content
                    }
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_chapter(self, chapter_id: int) -> None:
        """Удаляет главу"""
        with self.tracer.start_as_current_span(
                "TopicRepo.delete_chapter",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chapter_id": chapter_id
                }
        ) as span:
            try:
                await self.db.delete(
                    delete_chapter_query,
                    {"chapter_id": chapter_id}
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # Дополнительные вспомогательные методы
    async def get_topics_with_statistics(self) -> List[dict]:
        """Получает темы с количеством блоков и глав"""
        with self.tracer.start_as_current_span(
                "TopicRepo.get_topics_with_statistics",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rows = await self.db.select(get_topics_with_stats_query, {})

                topics_stats = []
                for row in rows:
                    topics_stats.append({
                        "topic": model.Topic(
                            id=row.id,
                            name=row.name,
                            intro=row.intro,
                            edu_plan=row.edu_plan,
                            created_at=row.created_at,
                            updated_at=row.updated_at
                        ),
                        "blocks_count": row.blocks_count,
                        "chapters_count": row.chapters_count
                    })

                span.set_attribute("topics_count", len(topics_stats))
                span.set_status(Status(StatusCode.OK))
                return topics_stats
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_topic_structure(self, topic_id: int) -> dict:
        """Получает полную структуру темы с блоками и главами"""
        with self.tracer.start_as_current_span(
                "TopicRepo.get_topic_structure",
                kind=SpanKind.INTERNAL,
                attributes={
                    "topic_id": topic_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_topic_structure_query,
                    {"topic_id": topic_id}
                )

                if not rows:
                    span.set_status(Status(StatusCode.OK))
                    return None

                # Группируем данные по структуре
                topic_data = None
                blocks_data = {}

                for row in rows:
                    # Создаем объект темы только один раз
                    if topic_data is None:
                        topic_data = {
                            "id": row.topic_id,
                            "name": row.topic_name,
                            "intro": row.topic_intro,
                            "edu_plan": row.topic_edu_plan
                        }

                    # Добавляем блоки
                    if row.block_id and row.block_id not in blocks_data:
                        blocks_data[row.block_id] = {
                            "id": row.block_id,
                            "name": row.block_name,
                            "chapters": []
                        }

                    # Добавляем главы
                    if row.chapter_id and row.block_id:
                        blocks_data[row.block_id]["chapters"].append({
                            "id": row.chapter_id,
                            "name": row.chapter_name
                        })

                # Формируем финальную структуру
                structure = {
                    "topic": topic_data,
                    "blocks": list(blocks_data.values())
                }

                span.set_attribute("blocks_count", len(blocks_data))
                span.set_status(Status(StatusCode.OK))
                return structure
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def topic_exists(self, topic_id: int) -> bool:
        """Проверяет существование темы"""
        with self.tracer.start_as_current_span(
                "TopicRepo.topic_exists",
                kind=SpanKind.INTERNAL,
                attributes={
                    "topic_id": topic_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    check_topic_exists_query,
                    {"topic_id": topic_id}
                )

                exists = rows[0].exists if rows else False
                span.set_attribute("exists", exists)
                span.set_status(Status(StatusCode.OK))
                return exists
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def block_exists(self, block_id: int) -> bool:
        """Проверяет существование блока"""
        with self.tracer.start_as_current_span(
                "TopicRepo.block_exists",
                kind=SpanKind.INTERNAL,
                attributes={
                    "block_id": block_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    check_block_exists_query,
                    {"block_id": block_id}
                )

                exists = rows[0].exists if rows else False
                span.set_attribute("exists", exists)
                span.set_status(Status(StatusCode.OK))
                return exists
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def chapter_exists(self, chapter_id: int) -> bool:
        """Проверяет существование главы"""
        with self.tracer.start_as_current_span(
                "TopicRepo.chapter_exists",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chapter_id": chapter_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    check_chapter_exists_query,
                    {"chapter_id": chapter_id}
                )

                exists = rows[0].exists if rows else False
                span.set_attribute("exists", exists)
                span.set_status(Status(StatusCode.OK))
                return exists
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err