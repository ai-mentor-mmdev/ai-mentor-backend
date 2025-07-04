import logging
from typing import List
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface, model
from .query import *


class EduChatRepo(interface.IEduChatRepo):
    def __init__(
            self,
            db: interface.IDB,
            tel: interface.ITelemetry
    ):
        self.db = db
        self.tracer = tel.tracer()
        self.logger = tel.logger()

    async def create_chat(self, student_id: int) -> int:
        with self.tracer.start_as_current_span(
                "EduChatRepo.create_chat",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                chat_id = await self.db.insert(CREATE_CHAT_QUERY, {"student_id": student_id})

                span.set_status(Status(StatusCode.OK))
                self.logger.info(f"Создан чат {chat_id} для студента {student_id}")
                return chat_id

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка создания чата для студента {student_id}: {err}")
                raise err

    async def get_or_create_chat(self, student_id: int) -> model.EduChat:
        with self.tracer.start_as_current_span(
                "EduChatRepo.get_or_create_chat",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                # Пытаемся найти существующий чат
                rows = await self.db.select(GET_CHAT_BY_STUDENT_ID_QUERY, {"student_id": student_id})

                if rows:
                    chats = model.EduChat.serialize(rows)
                    span.set_status(Status(StatusCode.OK))
                    self.logger.info(f"Найден существующий чат для студента {student_id}")
                    return chats[0]

                # Создаем новый чат, если не найден
                chat_id = await self.create_chat(student_id)

                # Получаем созданный чат
                rows = await self.db.select(GET_CHAT_BY_STUDENT_ID_QUERY, {"student_id": student_id})
                chats = model.EduChat.serialize(rows)

                span.set_status(Status(StatusCode.OK))
                self.logger.info(f"Создан новый чат для студента {student_id}")
                return chats[0]

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка получения/создания чата для студента {student_id}: {err}")
                raise err

    async def save_message(self, chat_id: int, text: str, role: str) -> int:
        with self.tracer.start_as_current_span(
                "EduChatRepo.save_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                    "role": role,
                    "text_length": len(text)
                }
        ) as span:
            try:
                message_id = await self.db.insert(CREATE_MESSAGE_QUERY, {
                    "chat_id": chat_id,
                    "text": text,
                    "role": role
                })

                # Обновляем timestamp чата
                await self.db.update(UPDATE_CHAT_TIMESTAMP_QUERY, {"chat_id": chat_id})

                span.set_status(Status(StatusCode.OK))
                self.logger.info(f"Сохранено сообщение {message_id} в чат {chat_id} от {role}")
                return message_id

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка сохранения сообщения в чат {chat_id}: {err}")
                raise err

    async def get_chat_history(self, student_id: int, limit: int = 50) -> List[model.EduMessage]:
        with self.tracer.start_as_current_span(
                "EduChatRepo.get_chat_history",
                kind=SpanKind.INTERNAL,
                attributes={
                    "student_id": student_id,
                    "limit": limit
                }
        ) as span:
            try:
                rows = await self.db.select(GET_CHAT_HISTORY_QUERY, {
                    "student_id": student_id,
                    "limit": limit
                })

                messages = model.EduMessage.serialize(rows) if rows else []

                span.set_status(Status(StatusCode.OK))
                span.set_attribute("messages_count", len(messages))
                self.logger.info(f"Получена история чата для студента {student_id}: {len(messages)} сообщений")
                return messages

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка получения истории чата студента {student_id}: {err}")
                raise err

    async def get_recent_messages(self, chat_id: int, count: int = 10) -> List[model.EduMessage]:
        with self.tracer.start_as_current_span(
                "EduChatRepo.get_recent_messages",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                    "count": count
                }
        ) as span:
            try:
                rows = await self.db.select(GET_RECENT_MESSAGES_QUERY, {
                    "chat_id": chat_id,
                    "count": count
                })

                messages = model.EduMessage.serialize(rows) if rows else []
                # Переворачиваем список, чтобы получить сообщения в хронологическом порядке
                messages.reverse()

                span.set_status(Status(StatusCode.OK))
                span.set_attribute("messages_count", len(messages))
                return messages

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка получения последних сообщений чата {chat_id}: {err}")
                raise err

    async def clear_chat_history(self, student_id: int) -> None:
        with self.tracer.start_as_current_span(
                "EduChatRepo.clear_chat_history",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                await self.db.delete(CLEAR_CHAT_HISTORY_QUERY, {"student_id": student_id})

                span.set_status(Status(StatusCode.OK))
                self.logger.info(f"Очищена история чата для студента {student_id}")

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка очистки истории чата студента {student_id}: {err}")
                raise err

    async def get_messages_count(self, chat_id: int) -> int:
        """Получает количество сообщений в чате"""
        with self.tracer.start_as_current_span(
                "EduChatRepo.get_messages_count",
                kind=SpanKind.INTERNAL,
                attributes={"chat_id": chat_id}
        ) as span:
            try:
                rows = await self.db.select(GET_MESSAGES_COUNT_QUERY, {"chat_id": chat_id})

                count = rows[0].count if rows else 0
                span.set_status(Status(StatusCode.OK))
                return count

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка получения количества сообщений чата {chat_id}: {err}")
                raise err