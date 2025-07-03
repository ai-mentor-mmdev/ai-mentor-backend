from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import interface
from internal import model


class EduChatService(interface.IEduChatService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            edu_chat_repo: interface.IEduChatRepo,
            llm_client: interface.ILLMClient,
            edu_prompt_service: interface.IEduPromptService
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.edu_chat_repo = edu_chat_repo
        self.llm_client = llm_client
        self.edu_prompt_service = edu_prompt_service

    async def send_message_to_interview_expert(self, account_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "EduChatService.send_message_to_interview_expert",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "text": text
                }
        ) as span:
            try:
                edu_chat_id = await self.get_or_create_chat(account_id)

                await self.edu_chat_repo.create_message(edu_chat_id, text, "user")
                messages = await self.edu_chat_repo.get_messages_by_chat_id(edu_chat_id)
                system_prompt = await self.edu_prompt_service.get_interview_expert_prompt(account_id)

                llm_response = await self.llm_client.generate(
                    self._convert_messages_to_llm_format(messages),
                    system_prompt,
                    0.7
                )

                # Сохраняем ответ ассистента
                await self.create_message(edu_chat_id, f"ASSISTANT: {llm_response}")

                span.set_status(Status(StatusCode.OK))
                return llm_response
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_teacher(self, account_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "EduChatService.send_message_to_teacher",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "text": text
                }
        ) as span:
            try:
                edu_chat_id = await self.get_or_create_chat(account_id)

                # Сохраняем сообщение пользователя
                await self.create_message(edu_chat_id, f"USER: {text}")

                # Получаем историю сообщений
                messages = await self.edu_chat_repo.get_messages_by_chat_id(edu_chat_id)

                # Получаем системный промпт
                system_prompt = await self.edu_prompt_service.get_teacher_prompt(account_id)

                # Отправляем в LLM
                llm_response = await self.llm_client.generate(
                    self._convert_messages_to_llm_format(messages),
                    system_prompt,
                    0.5
                )

                # Сохраняем ответ ассистента
                await self.create_message(edu_chat_id, f"ASSISTANT: {llm_response}")

                span.set_status(Status(StatusCode.OK))
                return llm_response
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_test_expert(self, account_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "EduChatService.send_message_to_test_expert",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id,
                    "text": text
                }
        ) as span:
            try:
                edu_chat_id = await self.get_or_create_chat(account_id)

                # Сохраняем сообщение пользователя
                await self.create_message(edu_chat_id, f"USER: {text}")

                # Получаем историю сообщений
                messages = await self.edu_chat_repo.get_messages_by_chat_id(edu_chat_id)

                # Получаем системный промпт
                system_prompt = await self.edu_prompt_service.get_test_expert_prompt(account_id)

                # Отправляем в LLM
                llm_response = await self.llm_client.generate(
                    self._convert_messages_to_llm_format(messages),
                    system_prompt,
                    0.3
                )

                # Сохраняем ответ ассистента
                await self.create_message(edu_chat_id, f"ASSISTANT: {llm_response}")

                span.set_status(Status(StatusCode.OK))
                return llm_response
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_or_create_chat(self, account_id: int) -> int:
        with self.tracer.start_as_current_span(
                "EduChatService.get_or_create_chat",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                chats = await self.edu_chat_repo.get_chat_by_account_id(account_id)

                if not chats:
                    self.logger.info("Создаем новый образовательный чат", {"account_id": account_id})
                    edu_chat_id = await self.edu_chat_repo.create_chat(account_id)
                    span.set_attribute("edu_chat_id", edu_chat_id)
                else:
                    edu_chat_id = chats[0].id
                    span.set_attribute("edu_chat_id", edu_chat_id)

                span.set_status(Status(StatusCode.OK))
                return edu_chat_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_message(self, edu_chat_id: int, text: str) -> int:
        with self.tracer.start_as_current_span(
                "EduChatService.create_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "edu_chat_id": edu_chat_id,
                    "text": text
                }
        ) as span:
            try:
                message_id = await self.edu_chat_repo.create_message(edu_chat_id, text)
                span.set_attribute("message_id", message_id)

                span.set_status(Status(StatusCode.OK))
                return message_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

