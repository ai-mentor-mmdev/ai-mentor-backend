from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import interface
from internal import model


class EduChatService(interface.IEduChatService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            edu_progress_repo: interface.IEduProgressRepo,
            edu_chat_repo: interface.IEduChatRepo,
            llm_client: interface.ILLMClient,
            edu_prompt_service: interface.IEduPromptService
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.edu_chat_repo = edu_chat_repo
        self.llm_client = llm_client
        self.edu_prompt_service = edu_prompt_service

