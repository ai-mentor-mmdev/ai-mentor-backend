from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import interface
from internal import model
from .query import *


class EduChatRepo(interface.IEduChatRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.db = db

    async def get_chat_by_account_id(self, account_id: int) -> list[model.EduChat]:
        with self.tracer.start_as_current_span(
                "EduChatRepo.get_chat_by_account_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                args = {"account_id": account_id}
                rows = await self.db.select(get_edu_chat_by_account_id, args)

                if rows:
                    rows = model.EduChat.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_chat(self, account_id: int) -> int:
        with self.tracer.start_as_current_span(
                "EduChatRepo.create_chat",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                args = {"account_id": account_id}
                edu_chat_id = await self.db.insert(create_edu_chat, args)

                span.set_status(Status(StatusCode.OK))
                return edu_chat_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_message(self, edu_chat_id: int, text: str) -> int:
        with self.tracer.start_as_current_span(
                "EduChatRepo.create_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "edu_chat_id": edu_chat_id,
                    "text": text
                }
        ) as span:
            try:
                args = {"edu_chat_id": edu_chat_id, "text": text}
                message_id = await self.db.insert(create_edu_message, args)

                span.set_status(Status(StatusCode.OK))
                return message_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_messages_by_chat_id(self, edu_chat_id: int) -> list[model.EduMessage]:
        with self.tracer.start_as_current_span(
                "EduChatRepo.get_messages_by_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "edu_chat_id": edu_chat_id
                }
        ) as span:
            try:
                args = {"edu_chat_id": edu_chat_id}
                rows = await self.db.select(get_edu_messages_by_chat_id, args)

                if rows:
                    rows = model.EduMessage.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                return rows
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err