from fastapi import status
from fastapi.responses import JSONResponse
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from .model import *


class ChatController(interface.IChatController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            chat_service: interface.IChatService
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.chat_service = chat_service

    async def send_message_to_registrator(self, body: SendMessageToExpert):
        with self.tracer.start_as_current_span(
                "EduChatController.send_message_to_registrator",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": body.account_id,
                    "text": body.text
                }
        ) as span:
            try:
                llm_response = await self.chat_service.send_message_to_registrator(
                    body.account_id,
                    body.text
                )

                response = SendMessageToExpertResponse(llm_response=llm_response)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_interview_expert(self, body: SendMessageToExpert):
        with self.tracer.start_as_current_span(
                "EduChatController.send_message_to_interview_expert",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": body.account_id,
                    "text": body.text
                }
        ) as span:
            try:
                llm_response = await self.chat_service.send_message_to_interview_expert(
                    body.account_id,
                    body.text
                )

                response = SendMessageToExpertResponse(llm_response=llm_response)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_teacher(self, body: SendMessageToExpert):
        with self.tracer.start_as_current_span(
                "EduChatController.send_message_to_teacher",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": body.account_id,
                    "text": body.text
                }
        ) as span:
            try:
                llm_response = await self.chat_service.send_message_to_teacher(
                    body.account_id,
                    body.text
                )

                response = SendMessageToExpertResponse(llm_response=llm_response)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_test_expert(self, body: SendMessageToExpert):
        with self.tracer.start_as_current_span(
                "EduChatController.send_message_to_test_expert",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": body.account_id,
                    "text": body.text
                }
        ) as span:
            try:
                llm_response = await self.chat_service.send_message_to_test_expert(
                    body.account_id,
                    body.text
                )

                response = SendMessageToExpertResponse(llm_response=llm_response)

                span.set_status(Status(StatusCode.OK))
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=response.model_dump(),
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err