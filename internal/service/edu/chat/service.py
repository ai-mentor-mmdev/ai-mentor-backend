# internal/service/edu/chat/service.py
from opentelemetry.trace import Status, StatusCode, SpanKind
from typing import Dict, List, Optional, Any
import json
import re

from internal import interface, model, common
from internal import model


class EduChatService(interface.IEduChatService):
    """Главный сервис для работы с образовательными чатами"""

    def __init__(
            self,
            tel: interface.ITelemetry,
            student_repo: interface.IStudentRepo,
            chat_repo: interface.IEduChatRepo,
            topic_repo: interface.ITopicRepo,
            llm_client: interface.ILLMClient,
            prompt_service: interface.IEduChatPromptGenerator,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.student_repo = student_repo
        self.chat_repo = chat_repo
        self.topic_repo = topic_repo
        self.llm_client = llm_client
        self.prompt_service = prompt_service

        # Паттерн для поиска команд
        self.command_pattern = re.compile(r'#(\w+)(?::([^#\s]+))?')

        # Инициализируем обработчиков экспертов
        self.expert_handlers = {
            common.ExpertType.INTERVIEW_EXPERT: InterviewExpertHandler(self),
            common.ExpertType.TEACHER: TeacherHandler(self),
            common.ExpertType.TEST_EXPERT: TestExpertHandler(self),
            common.ExpertType.CAREER_CONSULTANT: CareerConsultantHandler(self),
            common.ExpertType.PROGRESS_ANALYST: ProgressAnalystHandler(self),
        }

    async def send_message_to_registrator(self, student_id: int, text: str) -> str:
        """Отправка сообщения преподавателю"""
        with self.tracer.start_as_current_span(
                "EduChatService.send_message_to_registrator",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                response = await self._process_message(
                    student_id=student_id,
                    text=text,
                    expert_type=common.ExpertType.REGISTRATOR
                )

                span.set_status(Status(StatusCode.OK))
                return response.message

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err


    async def send_message_to_interview_expert(self, student_id: int, text: str) -> str:
        """Отправка сообщения эксперту по интервью"""
        with self.tracer.start_as_current_span(
                "EduChatService.send_message_to_interview_expert",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                response = await self._process_message(
                    student_id=student_id,
                    text=text,
                    expert_type=common.ExpertType.INTERVIEW_EXPERT
                )

                span.set_status(Status(StatusCode.OK))
                return response.message

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_teacher(self, student_id: int, text: str) -> str:
        """Отправка сообщения преподавателю"""
        with self.tracer.start_as_current_span(
                "EduChatService.send_message_to_teacher",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                response = await self._process_message(
                    student_id=student_id,
                    text=text,
                    expert_type=common.ExpertType.TEACHER
                )

                span.set_status(Status(StatusCode.OK))
                return response.message

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_to_test_expert(self, student_id: int, text: str) -> str:
        """Отправка сообщения эксперту по тестированию"""
        with self.tracer.start_as_current_span(
                "EduChatService.send_message_to_test_expert",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                response = await self._process_message(
                    student_id=student_id,
                    text=text,
                    expert_type=common.ExpertType.TEST_EXPERT
                )

                span.set_status(Status(StatusCode.OK))
                return response.message

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def _process_message(
            self,
            student_id: int,
            text: str,
            expert_type: common.ExpertType
    ) -> common.ExpertResponse:
        """Общий метод обработки сообщений"""
        # 1. Получаем студента и чат
        student = await self._get_or_create_student(student_id)
        chat = await self._get_or_create_chat(student.id)

        # 2. Сохраняем сообщение пользователя
        await self.chat_repo.save_message(chat.id, text, common.Roles.user)

        # 3. Получаем историю сообщений
        messages = await self.chat_repo.get_messages(student.id, limit=50)

        # 4. Получаем промпт для эксперта
        system_prompt = await self._get_expert_prompt(expert_type, student.id)

        # 5. Получаем ответ от LLM
        llm_response = await self.llm_client.generate(
            history=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )

        # 6. Сохраняем ответ ассистента
        await self.chat_repo.save_message(chat.id, llm_response, common.Roles.assistant)

        # 7. Формируем ответ
        return common.ExpertResponse(
            expert=expert_type,
            message=llm_response,
            metadata={
                "student_id": student.id,
                "chat_id": chat.id,
                "interview_stage": student.interview_stage
            }
        )

    async def _analyze_chat(
            self,
            student_id: int,
            text: str,
            expert_type: common.ExpertType
    ) -> common.ExpertResponse:
        """Общий метод обработки сообщений"""
        # 1. Получаем студента
        student = await self._get_or_create_student(student_id)

        # 2. Получаем историю сообщений
        messages = await self.chat_repo.get_messages(student.id, limit=50)

        # 3. Получаем промпт для анализа
        system_prompt = await self._get_expert_prompt(expert_type, student.id)

        # 4. Получаем список команд от ллм
        llm_commands = await self.llm_client.generate(
            history=messages,
            system_prompt=system_prompt,
            temperature=0.7
        )

        commands = self._extract_commands(llm_commands)

        # 7. Формируем ответ
        return common.ExpertResponse(
            expert=expert_type,
            commands_executed=commands
        )


    async def _get_or_create_student(self, student_id: int) -> model.Student:
        """Получает или создает студента"""
        students = await self.student_repo.get_by_id(student_id)
        if students:
            return students[0]

        # Создаем нового студента
        new_student = model.Student(
            id=0,
            account_id=student_id,
            interview_stage="WELCOME"
        )
        student_id = await self.student_repo.create_student(new_student)
        new_student.id = student_id
        return new_student

    async def _get_or_create_chat(self, student_id: int) -> model.EduChat:
        """Получает или создает студента"""
        chats = await self.chat_repo.get_by_id(student_id)
        if chats:
            return chats[0]

        # Создаем нового студента
        new_chat = model.EduChat(
            id=0,
            student_id=student_id
        )
        chat_id = await self.chat_repo.create_chat(new_chat)
        new_chat.id = chat_id
        return new_chat

    async def _get_expert_prompt(self, expert_type: ExpertType, student_id: int) -> str:
        """Получает промпт для эксперта"""
        prompt_methods = {
            ExpertType.INTERVIEW_EXPERT: self.prompt_service.get_interview_expert_prompt,
            ExpertType.TEACHER: self.prompt_service.get_teacher_prompt,
            ExpertType.TEST_EXPERT: self.prompt_service.get_test_expert_prompt,
        }

        method = prompt_methods.get(expert_type)
        if not method:
            raise ValueError(f"Неизвестный тип эксперта: {expert_type}")

        return await method(student_id)

    def _extract_commands(self, text: str) -> List[common.Command]:
        """Извлекает команды из текста"""
        commands = []

        for match in self.command_pattern.finditer(text):
            command_name = match.group(1)
            params = match.group(2).split(':') if match.group(2) else []

            # Определяем тип команды
            command_type = self._determine_command_type(command_name)

            command = common.Command(
                name=command_name,
                type=command_type,
                params=params,
                raw=match.group(0)
            )
            commands.append(command)

        return commands

    def _determine_command_type(self, command_name: str) -> CommandType:
        """Определяет тип команды по её имени"""
        if command_name.startswith("switch_to_"):
            return CommandType.SWITCH_EXPERT
        elif command_name.startswith("nav_to_") or "topic" in command_name or "block" in command_name:
            return CommandType.NAVIGATION
        elif command_name.startswith("update_") or "profile" in command_name:
            return CommandType.PROFILE_UPDATE
        elif "interview" in command_name or "stage" in command_name:
            return CommandType.INTERVIEW_CONTROL
        elif "test" in command_name or "assessment" in command_name:
            return CommandType.TEST_CONTROL
        elif "career" in command_name or "resume" in command_name:
            return CommandType.CAREER_CONTROL
        elif "analytics" in command_name or "progress" in command_name:
            return CommandType.ANALYTICS_CONTROL
        else:
            return CommandType.SYSTEM

    async def _execute_commands(
            self,
            student: model.Student,
            chat_id: int,
            commands: List[Command],
            expert_type: ExpertType
    ) -> List[CommandResult]:
        """Выполняет список команд"""
        results = []

        for command in commands:
            try:
                # Получаем обработчик для текущего эксперта
                handler = self.expert_handlers.get(expert_type)
                if not handler:
                    raise ValueError(f"Нет обработчика для эксперта {expert_type}")

                # Выполняем команду
                result = await handler.execute_command(command, student, chat_id)
                results.append(result)

                self.logger.info(
                    f"Команда {command.name} выполнена успешно",
                    {"student_id": student.id, "expert": expert_type.value}
                )

            except Exception as e:
                self.logger.error(
                    f"Ошибка выполнения команды {command.name}: {e}",
                    {"student_id": student.id, "expert": expert_type.value}
                )

                results.append(CommandResult(
                    command_name=command.name,
                    success=False,
                    type=command.type.value,
                    error=str(e)
                ))

        return results


class BaseExpertHandler:
    """Базовый класс для обработчиков экспертов"""

    def __init__(self, service: EduChatService):
        self.service = service
        self.student_repo = service.student_repo
        self.chat_repo = service.chat_repo
        self.topic_repo = service.topic_repo
        self.llm_client = service.llm_client
        self.logger = service.logger

    async def execute_command(
            self,
            command: Command,
            student: model.Student,
            chat_id: int
    ) -> CommandResult:
        """Выполняет команду"""
        # Базовые команды, доступные всем экспертам
        if command.type == CommandType.SWITCH_EXPERT:
            return await self._handle_switch_expert(command, student)

        # Делегируем специфичные команды наследникам
        return await self._handle_specific_command(command, student, chat_id)

    async def _handle_switch_expert(self, command: Command, student: model.Student) -> CommandResult:
        """Обрабатывает переключение эксперта"""
        new_expert = command.name.replace("switch_to_", "")

        return CommandResult(
            command_name=command.name,
            success=True,
            type="expert_switch",
            data={"new_expert": new_expert, "message": f"Переключаемся на {new_expert}"}
        )

    async def _handle_specific_command(
            self,
            command: Command,
            student: model.Student,
            chat_id: int
    ) -> CommandResult:
        """Обрабатывает специфичные команды эксперта"""
        raise NotImplementedError("Наследники должны реализовать этот метод")


class InterviewExpertHandler(BaseExpertHandler):
    """Обработчик команд эксперта по интервью"""

    async def _handle_specific_command(
            self,
            command: Command,
            student: model.Student,
            chat_id: int
    ) -> CommandResult:
        """Обрабатывает команды эксперта по интервью"""

        # Управление этапами интервью
        if command.name == "set_interview_stage":
            return await self._set_interview_stage(command, student)

        # Анализ диалога
        elif command.name == "analyze_dialogue":
            return await self._analyze_dialogue(command, student, chat_id)

        # Обновление профиля
        elif command.type == CommandType.PROFILE_UPDATE:
            return await self._update_profile(command, student)

        # Генерация плана обучения
        elif command.name == "generate_learning_plan":
            return await self._generate_learning_plan(command, student)

        # Завершение интервью
        elif command.name == "complete_interview":
            return await self._complete_interview(command, student)

        else:
            return CommandResult(
                command_name=command.name,
                success=False,
                type=command.type.value,
                error=f"Неизвестная команда для InterviewExpert: {command.name}"
            )

    async def _set_interview_stage(self, command: Command, student: model.Student) -> CommandResult:
        """Устанавливает этап интервью"""
        if not command.params:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="interview_control",
                error="Не указан этап интервью"
            )

        stage = command.params[0]
        await self.student_repo.set_interview_stage(student.id, stage)
        student.interview_stage = stage

        return CommandResult(
            command_name=command.name,
            success=True,
            type="interview_control",
            data={"stage": stage}
        )

    async def _analyze_dialogue(self, command: Command, student: model.Student, chat_id: int) -> CommandResult:
        """Анализирует диалог и извлекает данные профиля"""
        # Получаем историю диалога
        messages = await self.chat_repo.get_chat_history(student.id, limit=30)

        # Получаем промпт для анализа
        analysis_prompt = await self.service.prompt_service.get_dialogue_analysis_prompt(messages)

        # Анализируем с помощью LLM
        analysis_result = await self.llm_client.generate(
            history=[],
            system_prompt=analysis_prompt,
            temperature=0.3
        )

        try:
            # Парсим JSON ответ
            analysis_data = json.loads(analysis_result)

            # Обновляем профиль студента
            if "updates" in analysis_data:
                student.update_from_dict(analysis_data["updates"])
                await self.student_repo.update(student)

            return CommandResult(
                command_name=command.name,
                success=True,
                type="interview_control",
                data={
                    "updates_applied": analysis_data.get("updates", {}),
                    "confidence_score": analysis_data.get("confidence_score", 0),
                    "ready_for_teaching": analysis_data.get("ready_for_teaching", False)
                }
            )

        except json.JSONDecodeError as e:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="interview_control",
                error=f"Ошибка парсинга результата анализа: {e}"
            )

    async def _update_profile(self, command: Command, student: model.Student) -> CommandResult:
        """Обновляет поле профиля студента"""
        if len(command.params) < 1:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="profile_update",
                error="Недостаточно параметров для обновления профиля"
            )

        field_name = command.name.replace("update_", "")
        value = command.params[0] if command.params else None

        # Специальная обработка для JSON полей
        json_fields = ["known_languages", "learning_goals", "strong_areas", "weak_areas"]
        if field_name in json_fields and value:
            try:
                value = json.loads(value) if value.startswith('[') else [value]
            except json.JSONDecodeError:
                value = [value]

        # Обновляем профиль
        updates = {field_name: value}
        student.update_from_dict(updates)
        await self.student_repo.update(student)

        return CommandResult(
            command_name=command.name,
            success=True,
            type="profile_update",
            data={"field": field_name, "value": value}
        )

    async def _generate_learning_plan(self, command: Command, student: model.Student) -> CommandResult:
        """Генерирует персональный план обучения"""
        # Получаем все доступные темы
        topics = await self.topic_repo.get_all_topics()

        # Получаем промпт для генерации плана
        plan_prompt = await self.service.prompt_service.get_plan_generation_prompt(
            student_profile=student.__dict__,
            available_topics=topics
        )

        # Генерируем план с помощью LLM
        plan_result = await self.llm_client.generate(
            history=[],
            system_prompt=plan_prompt,
            temperature=0.5
        )

        try:
            # Парсим JSON ответ
            plan_data = json.loads(plan_result)

            # Обновляем профиль студента с планом
            student.skip_topics = plan_data.get("skip_topics", {})
            student.recommended_topics = plan_data.get("recommended_topics", {})
            student.focus_areas = plan_data.get("focus_areas", [])
            student.learning_path = plan_data.get("learning_path", [])

            # Устанавливаем первую тему для изучения
            if student.learning_path:
                first_topic = student.learning_path[0]
                student.current_topic_id = int(first_topic.get("topic_id", 0))

            await self.student_repo.update(student)

            return CommandResult(
                command_name=command.name,
                success=True,
                type="interview_control",
                data={
                    "plan_created": True,
                    "topics_count": len(student.recommended_topics),
                    "estimated_time": plan_data.get("total_estimated_time", "Не определено"),
                    "welcome_message": plan_data.get("welcome_message", "")
                }
            )

        except (json.JSONDecodeError, KeyError) as e:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="interview_control",
                error=f"Ошибка генерации плана обучения: {e}"
            )

    async def _complete_interview(self, command: Command, student: model.Student) -> CommandResult:
        """Завершает интервью"""
        student.interview_completed = True
        student.interview_stage = "COMPLETE"
        await self.student_repo.update(student)

        return CommandResult(
            command_name=command.name,
            success=True,
            type="interview_control",
            data={
                "interview_completed": True,
                "ready_for_learning": student.is_ready_for_learning()
            }
        )


class TeacherHandler(BaseExpertHandler):
    """Обработчик команд преподавателя"""

    async def _handle_specific_command(
            self,
            command: Command,
            student: model.Student,
            chat_id: int
    ) -> CommandResult:
        """Обрабатывает команды преподавателя"""

        # Навигация по контенту
        if command.type == CommandType.NAVIGATION:
            return await self._handle_navigation(command, student)

        # Управление прогрессом
        elif command.name.startswith("mark_") and "completed" in command.name:
            return await self._mark_completed(command, student)

        # Обучающие команды
        elif command.name in ["explain_concept", "give_example", "provide_analogy"]:
            return await self._handle_teaching_command(command, student)

        # Обновление профиля во время обучения
        elif command.name.startswith("student_"):
            return await self._handle_student_feedback(command, student)

        else:
            return CommandResult(
                command_name=command.name,
                success=False,
                type=command.type.value,
                error=f"Неизвестная команда для Teacher: {command.name}"
            )

    async def _handle_navigation(self, command: Command, student: model.Student) -> CommandResult:
        """Обрабатывает навигацию по контенту"""
        if not command.params:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="navigation",
                error="Не указан ID контента для навигации"
            )

        content_type = command.name.replace("nav_to_", "")
        content_id = int(command.params[0])

        # Обновляем текущую позицию студента
        if content_type == "topic":
            student.current_topic_id = content_id
            # Сбрасываем блок и главу при смене темы
            student.current_block_id = None
            student.current_chapter_id = None
        elif content_type == "block":
            student.current_block_id = content_id
            # Сбрасываем главу при смене блока
            student.current_chapter_id = None
        elif content_type == "chapter":
            student.current_chapter_id = content_id

        await self.student_repo.update(student)

        # Получаем информацию о контенте
        content_info = await self._get_content_info(content_type, content_id)

        return CommandResult(
            command_name=command.name,
            success=True,
            type="navigation",
            data={
                "content_type": content_type,
                "content_id": content_id,
                "content_name": content_info.get("name", "Неизвестно"),
                "content_description": content_info.get("description", "")
            }
        )

    async def _mark_completed(self, command: Command, student: model.Student) -> CommandResult:
        """Отмечает контент как завершенный"""
        if not command.params:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="progress",
                error="Не указан ID контента"
            )

        content_type = command.name.replace("mark_", "").replace("_completed", "")
        content_id = int(command.params[0])

        # Обновляем соответствующий словарь
        if content_type == "topic":
            if content_id in student.recommended_topics:
                student.approved_topics[content_id] = student.recommended_topics[content_id]
        elif content_type == "block":
            if content_id in student.recommended_blocks:
                student.approved_blocks[content_id] = student.recommended_blocks[content_id]
        elif content_type == "chapter":
            # Для глав просто добавляем ID и название
            chapter_info = await self._get_content_info("chapter", content_id)
            student.approved_chapters[content_id] = chapter_info.get("name", f"Chapter {content_id}")

        await self.student_repo.update(student)

        return CommandResult(
            command_name=command.name,
            success=True,
            type="progress",
            data={
                "content_type": content_type,
                "content_id": content_id,
                "completed": True,
                "total_completed": {
                    "topics": len(student.approved_topics),
                    "blocks": len(student.approved_blocks),
                    "chapters": len(student.approved_chapters)
                }
            }
        )

    async def _handle_teaching_command(self, command: Command, student: model.Student) -> CommandResult:
        """Обрабатывает обучающие команды"""
        concept = command.params[0] if command.params else "текущая тема"

        return CommandResult(
            command_name=command.name,
            success=True,
            type="teaching",
            data={
                "action": command.name,
                "concept": concept,
                "learning_style": student.learning_style
            }
        )

    async def _handle_student_feedback(self, command: Command, student: model.Student) -> CommandResult:
        """Обрабатывает обратную связь от студента"""
        feedback_type = command.name.replace("student_", "")

        if feedback_type == "knows_topic" and command.params:
            topic_id = int(command.params[0])
            student.skip_topics[topic_id] = "Студент уже знает эту тему"
            await self.student_repo.update(student)

        elif feedback_type == "struggling_with" and command.params:
            concept = command.params[0]
            if concept not in student.weak_areas:
                student.weak_areas.append(concept)
                await self.student_repo.update(student)

        elif feedback_type == "interested_in" and command.params:
            area = command.params[0]
            if area not in student.focus_areas:
                student.focus_areas.append(area)
                await self.student_repo.update(student)

        return CommandResult(
            command_name=command.name,
            success=True,
            type="student_feedback",
            data={
                "feedback_type": feedback_type,
                "processed": True
            }
        )

    async def _get_content_info(self, content_type: str, content_id: int) -> Dict[str, Any]:
        """Получает информацию о контенте"""
        try:
            if content_type == "topic":
                topic = await self.topic_repo.get_topic_by_id(content_id)
                return {"name": topic.name, "description": topic.intro} if topic else {}
            elif content_type == "block":
                block = await self.topic_repo.get_block_by_id(content_id)
                return {"name": block.name, "description": block.content[:200]} if block else {}
            elif content_type == "chapter":
                chapter = await self.topic_repo.get_chapter_by_id(content_id)
                return {"name": chapter.name, "description": chapter.content[:200]} if chapter else {}
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о контенте: {e}")
            return {}


class TestExpertHandler(BaseExpertHandler):
    """Обработчик команд эксперта по тестированию"""

    def __init__(self, service: EduChatService):
        super().__init__(service)
        # Храним активные сессии тестирования
        self.test_sessions: Dict[int, TestSession] = {}

    async def _handle_specific_command(
            self,
            command: Command,
            student: model.Student,
            chat_id: int
    ) -> CommandResult:
        """Обрабатывает команды тестирования"""

        # Создание тестов
        if command.name.startswith("create_") and "test" in command.name:
            return await self._create_test(command, student)

        # Управление тестированием
        elif command.name == "start_test":
            return await self._start_test(command, student)

        elif command.name == "evaluate_answer":
            return await self._evaluate_answer(command, student)

        elif command.name == "complete_test":
            return await self._complete_test(command, student)

        # Анализ результатов
        elif command.name in ["analyze_performance", "identify_knowledge_gaps"]:
            return await self._analyze_test_results(command, student)

        else:
            return CommandResult(
                command_name=command.name,
                success=False,
                type=command.type.value,
                error=f"Неизвестная команда для TestExpert: {command.name}"
            )

    async def _create_test(self, command: Command, student: model.Student) -> CommandResult:
        """Создает тест"""
        if not command.params:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="test_control",
                error="Не указан ID контента для теста"
            )

        content_id = int(command.params[0])
        test_type = command.name.replace("create_", "").replace("_test", "")

        # Здесь должна быть логика генерации вопросов
        # Пока создаем заглушку
        questions = [
            {
                "id": 1,
                "type": "multiple_choice",
                "question": "Пример вопроса 1",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A"
            },
            {
                "id": 2,
                "type": "open_question",
                "question": "Пример вопроса 2",
                "correct_answer": "Примерный ответ"
            }
        ]

        # Создаем сессию тестирования
        test_session = TestSession(
            id=chat_id,  # Используем chat_id как ID сессии
            student_id=student.id,
            test_type=test_type,
            questions=questions
        )

        self.test_sessions[student.id] = test_session

        return CommandResult(
            command_name=command.name,
            success=True,
            type="test_control",
            data={
                "test_created": True,
                "test_type": test_type,
                "questions_count": len(questions),
                "content_id": content_id
            }
        )

    async def _start_test(self, command: Command, student: model.Student) -> CommandResult:
        """Начинает тестирование"""
        test_session = self.test_sessions.get(student.id)
        if not test_session:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="test_control",
                error="Нет активной сессии тестирования"
            )

        # Возвращаем первый вопрос
        first_question = test_session.questions[0] if test_session.questions else None

        return CommandResult(
            command_name=command.name,
            success=True,
            type="test_control",
            data={
                "test_started": True,
                "current_question": first_question,
                "question_number": 1,
                "total_questions": len(test_session.questions)
            }
        )

    async def _evaluate_answer(self, command: Command, student: model.Student) -> CommandResult:
        """Оценивает ответ студента"""
        if len(command.params) < 2:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="test_control",
                error="Недостаточно параметров для оценки"
            )

        is_correct = command.params[0] == "correct"
        explanation = command.params[1] if len(command.params) > 1 else ""

        test_session = self.test_sessions.get(student.id)
        if not test_session:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="test_control",
                error="Нет активной сессии тестирования"
            )

        # Сохраняем ответ
        test_session.answers.append({
            "question_id": test_session.current_question_index,
            "is_correct": is_correct,
            "explanation": explanation
        })

        # Переходим к следующему вопросу
        test_session.current_question_index += 1

        # Получаем следующий вопрос
        next_question = None
        if test_session.current_question_index < len(test_session.questions):
            next_question = test_session.questions[test_session.current_question_index]

        return CommandResult(
            command_name=command.name,
            success=True,
            type="test_control",
            data={
                "answer_evaluated": True,
                "is_correct": is_correct,
                "explanation": explanation,
                "next_question": next_question,
                "progress": test_session.progress_percentage
            }
        )

    async def _complete_test(self, command: Command, student: model.Student) -> CommandResult:
        """Завершает тестирование"""
        test_session = self.test_sessions.get(student.id)
        if not test_session:
            return CommandResult(
                command_name=command.name,
                success=False,
                type="test_control",
                error="Нет активной сессии тестирования"
            )

        # Подсчитываем результат
        correct_answers = sum(1 for answer in test_session.answers if answer["is_correct"])
        total_questions = len(test_session.questions)
        score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0

        test_session.score = score
        test_session.completed_at = datetime.now()

        # Обновляем профиль студента
        student.assessment_score = score
        await self.student_repo.update(student)

        # Удаляем сессию
        del self.test_sessions[student.id]

        return CommandResult(
            command_name=command.name,
            success=True,
            type="test_control",
            data={
                "test_completed": True,
                "score": score,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "passed": score >= 60
            }
        )

    async def _analyze_test_results(self, command: Command, student: model.Student) -> CommandResult:
        """Анализирует результаты тестирования"""
        # Здесь должна быть более сложная логика анализа
        # Пока возвращаем базовый анализ

        weak_areas = []
        strong_areas = []

        if student.assessment_score:
            if student.assessment_score < 60:
                weak_areas = ["Требуется дополнительное изучение материала"]
            elif student.assessment_score >= 80:
                strong_areas = ["Отличное понимание материала"]
            else:
                weak_areas = ["Некоторые области требуют повторения"]

        return CommandResult(
            command_name=command.name,
            success=True,
            type="test_analysis",
            data={
                "analysis_complete": True,
                "weak_areas": weak_areas,
                "strong_areas": strong_areas,
                "recommendations": ["Повторите слабые темы", "Переходите к следующему разделу"]
            }
        )


class CareerConsultantHandler(BaseExpertHandler):
    """Обработчик команд карьерного консультанта"""

    async def _handle_specific_command(
            self,
            command: Command,
            student: model.Student,
            chat_id: int
    ) -> CommandResult:
        """Обрабатывает команды карьерного консультанта"""

        # Работа с резюме
        if "resume" in command.name:
            return await self._handle_resume_command(command, student)

        # Подготовка к собеседованию
        elif "interview" in command.name and "prep" in command.name:
            return await self._handle_interview_prep(command, student)

        # Анализ рынка труда
        elif command.name == "analyze_job_market":
            return await self._analyze_job_market(command, student)

        else:
            return CommandResult(
                command_name=command.name,
                success=False,
                type=command.type.value,
                error=f"Неизвестная команда для CareerConsultant: {command.name}"
            )

    async def _handle_resume_command(self, command: Command, student: model.Student) -> CommandResult:
        """Обрабатывает команды работы с резюме"""
        # Здесь должна быть логика создания/обновления резюме
        # Пока возвращаем заглушку

        return CommandResult(
            command_name=command.name,
            success=True,
            type="career_control",
            data={
                "action": command.name,
                "resume_status": "draft",
                "sections_completed": ["personal_info", "skills", "education"]
            }
        )

    async def _handle_interview_prep(self, command: Command, student: model.Student) -> CommandResult:
        """Обрабатывает подготовку к собеседованию"""
        position = command.params[0] if command.params else "Junior Developer"

        return CommandResult(
            command_name=command.name,
            success=True,
            type="career_control",
            data={
                "prep_started": True,
                "position": position,
                "topics_to_cover": ["algorithms", "system_design", "behavioral"]
            }
        )

    async def _analyze_job_market(self, command: Command, student: model.Student) -> CommandResult:
        """Анализирует рынок труда"""
        location = command.params[0] if command.params else "Remote"
        field = command.params[1] if len(command.params) > 1 else "Software Development"

        return CommandResult(
            command_name=command.name,
            success=True,
            type="career_control",
            data={
                "market_analyzed": True,
                "location": location,
                "field": field,
                "average_salary": "$60,000 - $80,000",
                "demand": "High",
                "required_skills": ["Python", "JavaScript", "SQL"]
            }
        )


class ProgressAnalystHandler(BaseExpertHandler):
    """Обработчик команд аналитика прогресса"""

    async def _handle_specific_command(
            self,
            command: Command,
            student: model.Student,
            chat_id: int
    ) -> CommandResult:
        """Обрабатывает команды аналитика"""

        # Анализ прогресса
        if command.name == "analyze_learning_progress":
            return await self._analyze_progress(command, student)

        # Генерация отчетов
        elif "report" in command.name:
            return await self._generate_report(command, student)

        # Рекомендации
        elif command.name.startswith("suggest_") or command.name.startswith("recommend_"):
            return await self._make_recommendations(command, student)

        else:
            return CommandResult(
                command_name=command.name,
                success=False,
                type=command.type.value,
                error=f"Неизвестная команда для ProgressAnalyst: {command.name}"
            )

    async def _analyze_progress(self, command: Command, student: model.Student) -> CommandResult:
        """Анализирует прогресс обучения"""
        # Подсчитываем базовые метрики
        total_topics = len(student.recommended_topics)
        completed_topics = len(student.approved_topics)
        completion_rate = (completed_topics / total_topics * 100) if total_topics > 0 else 0

        return CommandResult(
            command_name=command.name,
            success=True,
            type="analytics_control",
            data={
                "analysis_complete": True,
                "completion_rate": completion_rate,
                "completed_topics": completed_topics,
                "total_topics": total_topics,
                "current_level": student.programming_experience,
                "assessment_score": student.assessment_score
            }
        )

    async def _generate_report(self, command: Command, student: model.Student) -> CommandResult:
        """Генерирует отчет о прогрессе"""
        period = command.params[0] if command.params else "weekly"

        report = ProgressReport(
            student_id=student.id,
            period=period,
            metrics={
                "topics_completed": len(student.approved_topics),
                "blocks_completed": len(student.approved_blocks),
                "chapters_completed": len(student.approved_chapters),
                "assessment_score": student.assessment_score,
                "completion_percentage": student.get_profile_completion_percentage()
            },
            achievements=[
                f"Завершено {len(student.approved_topics)} тем",
                f"Текущий балл: {student.assessment_score or 0}"
            ],
            recommendations=[
                "Продолжайте в том же темпе",
                "Уделите внимание слабым областям"
            ]
        )

        return CommandResult(
            command_name=command.name,
            success=True,
            type="analytics_control",
            data={
                "report_generated": True,
                "period": period,
                "metrics": report.metrics,
                "achievements": report.achievements
            }
        )

    async def _make_recommendations(self, command: Command, student: model.Student) -> CommandResult:
        """Делает рекомендации по обучению"""
        recommendations = []

        # Анализируем текущее состояние и даем рекомендации
        if student.assessment_score and student.assessment_score < 60:
            recommendations.append("Рекомендуется повторить пройденный материал")

        if len(student.weak_areas) > 0:
            recommendations.append(f"Уделите внимание слабым областям: {', '.join(student.weak_areas)}")

        if not student.current_topic_id:
            recommendations.append("Выберите тему для изучения")

        return CommandResult(
            command_name=command.name,
            success=True,
            type="analytics_control",
            data={
                "recommendations": recommendations,
                "priority": "medium",
                "estimated_time": "1-2 недели"
            }
        )