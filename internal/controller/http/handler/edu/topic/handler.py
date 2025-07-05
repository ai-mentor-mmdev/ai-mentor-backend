from fastapi import status
from fastapi.responses import JSONResponse, StreamingResponse
from opentelemetry.trace import StatusCode, SpanKind
from reportbug.debbugs import header

from internal import interface
from .model import *


class EduTopicController(interface.IEduTopicController):
    def __init__(
            self,
            tel: interface.ITelemetry,
            edu_topic_service: interface.IEduTopicService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.edu_topic_service = edu_topic_service

    async def download_topic_content(self, body: DownloadTopicContentBody):
        with self.tracer.start_as_current_span(
                "EduChatController.download_topic_content",
                kind=SpanKind.INTERNAL,
                attributes={
                    "edu_content_type": body.edu_content_type,
                    "topic_id": body.topic_id
                }
        ) as span:
            try:
                file, content_type = await self.edu_topic_service.download_topic_content(
                    body.edu_content_type,
                    body.topic_id
                )
                headers = {
                    "Content-Type": content_type,
                }
                return StreamingResponse(
                    content=file,
                    headers=headers
                )
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
                }
        ) as span:
            try:
                file, content_type = await self.edu_topic_service.download_block_content(
                    body.block_id
                )
                headers = {
                    "Content-Type": content_type,
                }
                return StreamingResponse(
                    content=file,
                    headers=headers
                )
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
