from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import interface
from internal import model
from .query import *


class EduProgressRepo(interface.IEduProgressRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def get_progress_by_account_id(self, account_id: int) -> model.EduProgress:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_progress_by_account_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                args = {"account_id": account_id}
                rows = await self.db.select(get_progress_by_account_id, args)

                if rows:
                    rows = model.EduProgress.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return rows[0]
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_current_topic(self, account_id: int) -> model.Topic:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_current_topic",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                progress = await self.get_progress_by_account_id(account_id)
                if not progress or not progress.current_topic_id:
                    span.set_status(Status(StatusCode.OK))
                    return None

                args = {"id": progress.current_topic_id}
                rows = await self.db.select(get_topic_by_id, args)

                if rows:
                    rows = model.Topic.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return rows[0]
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_current_block(self, account_id: int) -> model.Block:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_current_block",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                progress = await self.get_progress_by_account_id(account_id)
                if not progress or not progress.current_block_id:
                    span.set_status(Status(StatusCode.OK))
                    return None

                args = {"id": progress.current_block_id}
                rows = await self.db.select(get_block_by_id, args)

                if rows:
                    rows = model.Block.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return rows[0]
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_current_chapter(self, account_id: int) -> model.Chapter:
        with self.tracer.start_as_current_span(
                "EduProgressRepo.get_current_chapter",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                progress = await self.get_progress_by_account_id(account_id)
                if not progress or not progress.current_chapter_id:
                    span.set_status(Status(StatusCode.OK))
                    return None

                args = {"id": progress.current_chapter_id}
                rows = await self.db.select(get_chapter_by_id, args)

                if rows:
                    rows = model.Chapter.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return rows[0]
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err