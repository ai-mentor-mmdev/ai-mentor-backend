from opentelemetry.trace import SpanKind, Status, StatusCode

from .query import *
from internal import model
from internal import interface


class TopicRepo(interface.ITopicRepo):
    def __init__(self, tel: interface.ITelemetry, db: interface.IDB):
        self.db = db
        self.tracer = tel.tracer()

    # Topic methods
    async def get_topic_by_id(self, topic_id: int) -> list[model.Topic]:
        with self.tracer.start_as_current_span(
                "TopicRepo.get_topic_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"topic_id": topic_id}
        ) as span:
            try:
                args = {'topic_id': topic_id}
                rows = await self.db.select(get_topic_by_id, args)
                result = model.Topic.serialize(rows) if rows else []

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_all_topic(self) -> list[model.Topic]:
        with self.tracer.start_as_current_span(
                "TopicRepo.get_all_topic",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rows = await self.db.select(get_all_topics, {})
                result = model.Topic.serialize(rows) if rows else []

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    # Block methods
    async def get_block_by_id(self, block_id: int) -> list[model.Block]:
        with self.tracer.start_as_current_span(
                "TopicRepo.get_block_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"block_id": block_id}
        ) as span:
            try:
                args = {'block_id': block_id}
                rows = await self.db.select(get_block_by_id, args)
                result = model.Block.serialize(rows) if rows else []

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_all_block(self) -> list[model.Block]:
        with self.tracer.start_as_current_span(
                "TopicRepo.get_all_block",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rows = await self.db.select(get_all_blocks, {})
                result = model.Block.serialize(rows) if rows else []

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    # Chapter methods
    async def get_chapter_by_id(self, chapter_id: int) -> list[model.Chapter]:
        with self.tracer.start_as_current_span(
                "TopicRepo.get_chapter_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"chapter_id": chapter_id}
        ) as span:
            try:
                args = {'chapter_id': chapter_id}
                rows = await self.db.select(get_chapter_by_id, args)
                result = model.Chapter.serialize(rows) if rows else []

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def get_all_chapter(self) -> list[model.Chapter]:
        with self.tracer.start_as_current_span(
                "TopicRepo.get_all_chapter",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rows = await self.db.select(get_all_chapters, {})
                result = model.Chapter.serialize(rows) if rows else []

                span.set_status(StatusCode.OK)
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    # Student progress methods
    async def update_current_topic(self, student_id: int, topic_id: int, topic_name: str):
        with self.tracer.start_as_current_span(
                "TopicRepo.update_current_topic",
                kind=SpanKind.INTERNAL,
                attributes={
                    "student_id": student_id,
                    "topic_id": topic_id
                }
        ) as span:
            try:
                args = {
                    'student_id': student_id,
                    'topic_id': str(topic_id),
                    'topic_name': topic_name,
                }
                await self.db.update(update_current_topic, args)
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_current_block(self, student_id: int, block_id: int, block_name: str):
        with self.tracer.start_as_current_span(
                "TopicRepo.update_current_block",
                kind=SpanKind.INTERNAL,
                attributes={
                    "student_id": student_id,
                    "block_id": block_id
                }
        ) as span:
            try:
                args = {
                    'student_id': student_id,
                    'block_id': str(block_id),
                    'block_name': block_name,
                }
                await self.db.update(update_current_block, args)
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def update_current_chapter(self, student_id: int, chapter_id: int, chapter_name: str):
        with self.tracer.start_as_current_span(
                "TopicRepo.update_current_chapter",
                kind=SpanKind.INTERNAL,
                attributes={
                    "student_id": student_id,
                    "chapter_id": chapter_id
                }
        ) as span:
            try:
                args = {
                    'student_id': student_id,
                    'chapter_id': str(chapter_id),
                    'chapter_name': chapter_name,
                }
                await self.db.update(update_current_chapter, args)
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err