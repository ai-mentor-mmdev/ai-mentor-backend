from fastapi import status
from fastapi.responses import JSONResponse
from opentelemetry.trace import StatusCode, SpanKind

from internal import interface
from .model import *


class EduTopicController(interface.IEduTopicController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            chat_service: interface.IChatService
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.chat_service = chat_service

    async def download_topic_content(self, body: DownloadTopicContentBody):
        with self.tracer.start_as_current_span(
                "EduChatController.download_topic_content",
                kind=SpanKind.INTERNAL,
                attributes={
                    "content_type": body.content_type,
                    "topic_id": body.topic_id
                }
        ) as span:
            try:
               pass
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def download_block_content(self, body: DownloadBlockContentBody):
        with self.tracer.start_as_current_span(
                "EduChatController.download_block_content",
                kind=SpanKind.INTERNAL,
                attributes={
                    "block_id": body.block_id,
                    "topic_id": body.topic_id
                }
        ) as span:
            try:
               pass
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err