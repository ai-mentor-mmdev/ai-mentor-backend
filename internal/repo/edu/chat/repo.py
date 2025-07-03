from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import interface, model
from .query import *


class EduChatRepo(interface.IEduChatRepo):
    def __init__(
            self,
            tel: interface.ITelemetry,
            db: interface.IDB
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.db = db

    async def create_chat(self, account_id: int) -> int:
        """Создает новый чат для студента"""
        with self.tracer.start_as_current_span(
                "EduChatRepo.create_chat",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                chat_id = await self.db.insert(
                    create_chat_query,
                    {"account_id": account_id}
                )

                span.set_status(Status(StatusCode.OK))
                return chat_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_chat_by_account_id(self, account_id: int) -> model.EduChat:
        """Получает чат по ID студента"""
        with self.tracer.start_as_current_span(
                "EduChatRepo.get_chat_by_account_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_chat_by_account_id_query,
                    {"account_id": account_id}
                )

                if rows:
                    chats = model.EduChat.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return chats[0]
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_chat_by_id(self, chat_id: int) -> model.EduChat:
        """Получает чат по его ID"""
        with self.tracer.start_as_current_span(
                "EduChatRepo.get_chat_by_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_chat_by_id_query,
                    {"chat_id": chat_id}
                )

                if rows:
                    chats = model.EduChat.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    return chats[0]
                else:
                    span.set_status(Status(StatusCode.OK))
                    return None
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def add_message(self, edu_chat_id: int, text: str, role: str) -> int:
        """Добавляет сообщение в чат"""
        with self.tracer.start_as_current_span(
                "EduChatRepo.add_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "edu_chat_id": edu_chat_id,
                    "role": role,
                    "text_length": len(text)
                }
        ) as span:
            try:
                message_id = await self.db.insert(
                    add_message_query,
                    {
                        "edu_chat_id": edu_chat_id,
                        "text": text,
                        "role": role
                    }
                )

                span.set_status(Status(StatusCode.OK))
                return message_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_messages_by_chat_id(self, edu_chat_id: int, limit: int = 50) -> list[model.EduMessage]:
        """Получает сообщения чата с ограничением"""
        with self.tracer.start_as_current_span(
                "EduChatRepo.get_messages_by_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "edu_chat_id": edu_chat_id,
                    "limit": limit
                }
        ) as span:
            try:
                rows = await self.db.select(
                    get_messages_by_chat_id_query,
                    {"edu_chat_id": edu_chat_id, "limit": limit}
                )

                messages = model.EduMessage.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return messages
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err