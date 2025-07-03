from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import common
from internal import model


class EduChatService(interface.IEduChatService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            edu_chat_repo: interface.IEduChatRepo,
            edu_progress_repo: interface.IEduProgressRepo,
            llm_client: interface.ILLMClient,
            edu_prompt_service: interface.IEduPromptService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.edu_chat_repo = edu_chat_repo
        self.edu_progress_repo = edu_progress_repo
        self.llm_client = llm_client
        self.edu_prompt_service = edu_prompt_service

    async def send_message_to_interview_expert(self, student_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "EduChatService.send_message_to_interview_expert",
                kind=SpanKind.INTERNAL,
                attributes={
                    "student_id": student_id,
                    "text": text,
                }
        ) as span:
            try:
                chat = await self._get_or_create_chat(student_id)
                await self.edu_chat_repo.add_message(chat.id, text, common.Roles.user)
                messages = await self.edu_chat_repo.get_messages_by_chat_id(chat.id)
                system_prompt = await self.edu_prompt_service.get_interview_expert_prompt(student_id)

                llm_response = await self.llm_client.generate(
                    messages,
                    system_prompt,
                    0.7,
                    "gpt-4o-mini"
                )

                # Проверяем, есть ли команды в ответе
                if self._check_command_in_response(llm_response):
                    self.logger.info("LLM ответила командой для эксперта по интервью")
                    span.set_status(Status(StatusCode.OK))
                    return llm_response
                else:
                    # Сохраняем ответ ассистента
                    await self.edu_chat_repo.add_message(chat.id, llm_response, common.Roles.assistant)

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
                    "text": text,
                }
        ) as span:
            try:
                # Получаем или создаем чат для студента
                chat = await self._get_or_create_chat(account_id)

                # Добавляем сообщение пользователя
                await self.edu_chat_repo.add_message(chat.id, text, common.Roles.user)

                # Получаем историю сообщений
                messages = await self.edu_chat_repo.get_messages_by_chat_id(chat.id)

                # Получаем системный промпт для преподавателя
                system_prompt = await self.edu_prompt_service.get_teacher_prompt(account_id)

                # Генерируем ответ от LLM
                llm_response = await self.llm_client.generate(
                    messages,
                    system_prompt,
                    0.5,
                    "gpt-4o-mini"
                )

                # Проверяем, есть ли команды в ответе
                if self._check_command_in_response(llm_response):
                    self.logger.info("LLM ответила командой для преподавателя")
                    span.set_status(Status(StatusCode.OK))
                    return llm_response
                else:
                    # Сохраняем ответ ассистента
                    await self.edu_chat_repo.add_message(chat.id, llm_response, common.Roles.assistant)

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
                    "text": text,
                }
        ) as span:
            try:
                # Получаем или создаем чат для студента
                chat = await self._get_or_create_chat(account_id)

                # Добавляем сообщение пользователя
                await self.edu_chat_repo.add_message(chat.id, text, common.Roles.user)

                # Получаем историю сообщений
                messages = await self.edu_chat_repo.get_messages_by_chat_id(chat.id)

                # Получаем системный промпт для эксперта по тестированию
                system_prompt = await self.edu_prompt_service.get_test_expert_prompt(account_id)

                # Генерируем ответ от LLM
                llm_response = await self.llm_client.generate(
                    messages,
                    system_prompt,
                    0.3,
                    "gpt-4o-mini"
                )

                # Проверяем, есть ли команды в ответе
                if self._check_command_in_response(llm_response):
                    self.logger.info("LLM ответила командой для эксперта по тестированию")
                    span.set_status(Status(StatusCode.OK))
                    return llm_response
                else:
                    # Сохраняем ответ ассистента
                    await self.edu_chat_repo.add_message(chat.id, llm_response, common.Roles.assistant)

                    span.set_status(Status(StatusCode.OK))
                    return llm_response

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def _get_or_create_chat(self, student_id: int) -> model.EduChat:
        """Получает существующий чат или создает новый для студента"""
        with self.tracer.start_as_current_span(
                "EduChatService._get_or_create_chat",
                kind=SpanKind.INTERNAL,
                attributes={
                    "student_id": student_id
                }
        ) as span:
            try:
                # Пытаемся получить существующий чат
                chat = await self.edu_chat_repo.get_chat_by_student_id(student_id)

                if chat is None:
                    # Создаем новый чат если его нет
                    chat_id = await self.edu_chat_repo.create_chat(student_id)
                    chat = await self.edu_chat_repo.get_chat_by_id(chat_id)

                    span.set_attribute("chat_created", True)
                    span.set_attribute("chat_id", chat_id)
                else:
                    span.set_attribute("chat_created", False)
                    span.set_attribute("chat_id", chat.id)

                span.set_status(Status(StatusCode.OK))
                return chat

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    def _check_command_in_response(self, llm_response: str) -> bool:
        """Проверяет, содержит ли ответ LLM команды навигации или переключения экспертов"""
        with self.tracer.start_as_current_span(
                "EduChatService._check_command_in_response",
                kind=SpanKind.INTERNAL,
                attributes={
                    "llm_response": llm_response
                }
        ) as span:
            try:
                # Проверяем команды переключения между экспертами
                expert_switch_commands = [
                    common.EduStateSwitchCommand.to_teacher,
                    common.EduStateSwitchCommand.to_test_expert,
                    common.EduStateSwitchCommand.to_interview_expert,
                ]

                # Проверяем команды навигации
                navigation_commands = [
                    common.EduNavigationCommand.to_topic,
                    common.EduNavigationCommand.to_block,
                    common.EduNavigationCommand.to_chapter,
                    common.EduNavigationCommand.show_topics,
                    common.EduNavigationCommand.show_blocks,
                    common.EduNavigationCommand.show_chapters,
                    common.EduNavigationCommand.show_progress,
                ]

                # Проверяем команды прогресса
                progress_commands = [
                    common.EduProgressAction.complete_topic,
                    common.EduProgressAction.complete_block,
                    common.EduProgressAction.complete_chapter,
                    common.EduProgressAction.start_topic,
                    common.EduProgressAction.start_block,
                    common.EduProgressAction.start_chapter,
                ]

                all_commands = expert_switch_commands + navigation_commands + progress_commands

                # Проверяем наличие любой из команд в ответе
                has_command = any(command in llm_response for command in all_commands)

                span.set_attribute("has_command", has_command)
                span.set_status(Status(StatusCode.OK))

                return has_command

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err


    async def delete_all_messages(self, chat_id: int) -> None:
        """Удаляет все сообщения в чате (если такая функция нужна)"""
        with self.tracer.start_as_current_span(
                "EduChatService.delete_all_messages",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id
                }
        ) as span:
            try:
                # Здесь нужно будет добавить метод в репозиторий
                # await self.edu_chat_repo.delete_all_messages(chat_id)

                span.set_status(Status(StatusCode.OK))

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err