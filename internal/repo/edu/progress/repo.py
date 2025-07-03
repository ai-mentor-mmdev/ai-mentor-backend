from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import interface, model
from .query import *


class EduProgressRepo(interface.IEduProgressRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.db = db

    async def get_progress_by_account_id(self, account_id: int) -> list[model.EduProgress]:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_progress_by_account_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_progress_by_account_id_query,
                    {"account_id": account_id}
                )

                progress_list = model.EduProgress.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return progress_list
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_progress_by_chat_id(self, edu_chat_id: int) -> list[model.EduProgress]:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_progress_by_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "edu_chat_id": edu_chat_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_progress_by_chat_id_query,
                    {"edu_chat_id": edu_chat_id}
                )

                progress_list = model.EduProgress.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return progress_list
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_current_topic_id(self, account_id: int) -> int:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_current_topic_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_current_topic_id_query,
                    {"account_id": account_id}
                )

                if rows:
                    topic_id = rows[0].current_topic_id
                    span.set_status(Status(StatusCode.OK))
                    return topic_id
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_current_block_id(self, account_id: int) -> int:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_current_block_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_current_block_id_query,
                    {"account_id": account_id}
                )

                if rows:
                    block_id = rows[0].current_block_id
                    span.set_status(Status(StatusCode.OK))
                    return block_id
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_current_chapter_id(self, account_id: int) -> int:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_current_chapter_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_current_chapter_id_query,
                    {"account_id": account_id}
                )

                if rows:
                    chapter_id = rows[0].current_chapter_id
                    span.set_status(Status(StatusCode.OK))
                    return chapter_id
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_approved_topic_ids(self, progress_id: int) -> list[int]:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_approved_topic_ids",
                kind=SpanKind.INTERNAL,
                attributes={
                    "progress_id": progress_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_approved_topic_ids_query,
                    {"progress_id": progress_id}
                )

                if rows and rows[0].approved_topic_ids:
                    topic_ids = rows[0].approved_topic_ids
                    span.set_status(Status(StatusCode.OK))
                    return topic_ids
                else:
                    span.set_status(Status(StatusCode.OK))
                    return []
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_approved_block_ids(self, progress_id: int) -> list[int]:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_approved_block_ids",
                kind=SpanKind.INTERNAL,
                attributes={
                    "progress_id": progress_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_approved_block_ids_query,
                    {"progress_id": progress_id}
                )

                if rows and rows[0].approved_block_ids:
                    block_ids = rows[0].approved_block_ids
                    span.set_status(Status(StatusCode.OK))
                    return block_ids
                else:
                    span.set_status(Status(StatusCode.OK))
                    return []
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_approved_chapter_ids(self, progress_id: int) -> list[int]:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_approved_chapter_ids",
                kind=SpanKind.INTERNAL,
                attributes={
                    "progress_id": progress_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_approved_chapter_ids_query,
                    {"progress_id": progress_id}
                )

                if rows and rows[0].approved_chapter_ids:
                    chapter_ids = rows[0].approved_chapter_ids
                    span.set_status(Status(StatusCode.OK))
                    return chapter_ids
                else:
                    span.set_status(Status(StatusCode.OK))
                    return []
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_current_topic_id(self, progress_id: int, topic_id: int):
        with self.tracer.start_as_current_span(
                "EduProgressRepo.update_current_topic_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "progress_id": progress_id,
                    "topic_id": topic_id
                }
        ) as span:
            try:
                await self.db.update(
                    update_current_topic_id_query,
                    {"progress_id": progress_id, "topic_id": topic_id}
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_current_block_id(self, progress_id: int, block_id: int):
        with self.tracer.start_as_current_span(
                "EduProgressRepo.update_current_block_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "progress_id": progress_id,
                    "block_id": block_id
                }
        ) as span:
            try:
                await self.db.update(
                    update_current_block_id_query,
                    {"progress_id": progress_id, "block_id": block_id}
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def update_current_chapter_id(self, progress_id: int, chapter_id: int):
        with self.tracer.start_as_current_span(
                "EduProgressRepo.update_current_chapter_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "progress_id": progress_id,
                    "chapter_id": chapter_id
                }
        ) as span:
            try:
                await self.db.update(
                    update_current_chapter_id_query,
                    {"progress_id": progress_id, "chapter_id": chapter_id}
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def mark_topic_completed(self, progress_id: int, topic_id: int):
        with self.tracer.start_as_current_span(
                "EduProgressRepo.mark_topic_completed",
                kind=SpanKind.INTERNAL,
                attributes={
                    "progress_id": progress_id,
                    "topic_id": topic_id
                }
        ) as span:
            try:
                await self.db.update(
                    mark_topic_completed_query,
                    {"progress_id": progress_id, "topic_id": topic_id}
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def mark_block_completed(self, progress_id: int, block_id: int):
        with self.tracer.start_as_current_span(
                "EduProgressRepo.mark_block_completed",
                kind=SpanKind.INTERNAL,
                attributes={
                    "progress_id": progress_id,
                    "block_id": block_id
                }
        ) as span:
            try:
                await self.db.update(
                    mark_block_completed_query,
                    {"progress_id": progress_id, "block_id": block_id}
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def mark_chapter_completed(self, progress_id: int, chapter_id: int):
        with self.tracer.start_as_current_span(
                "EduProgressRepo.mark_chapter_completed",
                kind=SpanKind.INTERNAL,
                attributes={
                    "progress_id": progress_id,
                    "chapter_id": chapter_id
                }
        ) as span:
            try:
                await self.db.update(
                    mark_chapter_completed_query,
                    {"progress_id": progress_id, "chapter_id": chapter_id}
                )

                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    # Additional helper methods for the prompt service
    async def get_current_topic(self, account_id: int) -> model.Topic:
        """Получает объект текущей темы для студента"""
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_current_topic",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_current_topic_query,
                    {"account_id": account_id}
                )

                if rows:
                    topics = model.Topic.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return topics[0] if topics else None
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_current_block(self, account_id: int) -> model.Block:
        """Получает объект текущего блока для студента"""
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_current_block",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_current_block_query,
                    {"account_id": account_id}
                )

                if rows:
                    blocks = model.Block.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return blocks[0] if blocks else None
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_current_chapter(self, account_id: int) -> model.Chapter:
        """Получает объект текущей главы для студента"""
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_current_chapter",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_current_chapter_query,
                    {"account_id": account_id}
                )

                if rows:
                    chapters = model.Chapter.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return chapters[0] if chapters else None
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_available_topics(self, account_id: int) -> list[model.Topic]:
        """Получает все доступные темы"""
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_available_topics",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_available_topics_query,
                    {}
                )

                topics = model.Topic.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return topics
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_available_blocks(self, account_id: int) -> list[model.Block]:
        """Получает доступные блоки для текущей темы студента"""
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_available_blocks",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_available_blocks_query,
                    {"account_id": account_id}
                )

                blocks = model.Block.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return blocks
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_available_chapters(self, account_id: int) -> list[model.Chapter]:
        """Получает доступные главы для текущего блока студента"""
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_available_chapters",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_available_chapters_query,
                    {"account_id": account_id}
                )

                chapters = model.Chapter.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return chapters
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_completed_topics(self, account_id: int) -> list[model.Topic]:
        """Получает завершенные темы для студента"""
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_completed_topics",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_completed_topics_query,
                    {"account_id": account_id}
                )

                topics = model.Topic.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return topics
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_completed_blocks(self, account_id: int) -> list[model.Block]:
        """Получает завершенные блоки для студента"""
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_completed_blocks",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_completed_blocks_query,
                    {"account_id": account_id}
                )

                blocks = model.Block.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return blocks
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_completed_chapters(self, account_id: int) -> list[model.Chapter]:
        """Получает завершенные главы для студента"""
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_completed_chapters",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_completed_chapters_query,
                    {"account_id": account_id}
                )

                chapters = model.Chapter.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return chapters
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err