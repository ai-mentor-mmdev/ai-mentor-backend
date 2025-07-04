# internal/service/edu_service.py
import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import asdict

from internal import model, interface


class EduService:
    def __init__(
            self,
            student_repo: interface.IStudentRepo,
            chat_repo: interface.IEduChatRepo,
            topic_repo: interface.ITopicRepo,
            llm_client: interface.ILLMClient,
    ):
        self.student_repo = student_repo
        self.chat_repo = chat_repo
        self.topic_repo = topic_repo
        self.llm_client = llm_client

        # Паттерн для поиска команд в тексте
        self.command_pattern = re.compile(r'#(\w+)(?::([^#\s]+))?')

        # Загружаем промпты
        self.prompts = self._load_prompts()

    async def process_message(
            self,
            chat_id: int,
            message: str,
            student_id: int
    ) -> Dict[str, Any]:
        student = (await self.student_repo.get_by_id(student_id))[0]
        chat = (await self.chat_repo.get_by_id(chat_id))[0]
        messages = await self.chat_repo.get_messages(chat_id)

        # 1. Формируем промпт
        system_prompt = self._build_system_prompt(student.current_expert, student)

        # 2. Получаем ответ от LLM
        llm_response = await self.llm_client.generate(
            system_prompt=system_prompt,
            history=messages + [{"role": "user", "content": message}]
        )

        commands = await self.llm_client.generate(
            system_prompt=system_prompt,
            history=messages + [{"role": "user", "content": message}]
        )

        # 4. Выполняем команды
        command_results = await self._execute_commands(
            student=student,
            chat_id=chat_id,
            commands=commands
        )

        # 5. Сохраняем сообщения
        await self._save_messages(chat_id, message, clean_response, student.current_expert)

        return {
            "response": clean_response,
            "expert": student.current_expert,
            "commands_executed": [cmd["name"] for cmd in command_results],
            "events": command_results
        }

    def _build_system_prompt(self, expert: str, student: model.Student) -> str:
        """Формирует системный промпт для текущего эксперта"""
        # Базовый контекст
        base_context = self.prompts["base_context"]

        # Контекст студента
        student_context = self._format_student_context(student)

        # Промпт эксперта
        expert_prompt = self.prompts[f"{expert}_prompt"]

        # Глобальные правила
        global_rules = self.prompts["global_rules"]

        return f"{base_context}\n\n{student_context}\n\n{expert_prompt}\n\n{global_rules}"

    def _format_student_context(self, student: model.Student) -> str:
        """Форматирует контекст студента для промпта"""
        topics = ", ".join([f"{id}:{name}" for id, name in student.recommended_topics.items()])
        current_topic = "Не выбрана"
        if student.current_topic_id and student.recommended_topics:
            current_topic = student.recommended_topics.get(student.current_topic_id, "Неизвестная")

        return f"""ПРОФИЛЬ СТУДЕНТА:
- ID студента: {student.id}
- Этап интервью: {student.interview_stage}
- Завершенность интервью: {'Да' if student.interview_completed else 'Нет'}
- Опыт программирования: {student.programming_experience or 'Не определен'}
- Известные языки: {', '.join(student.known_languages) if student.known_languages else 'Не указаны'}
- Опыт работы: {student.work_experience or 'Не указан'}
- Образование: {student.education_background or 'Не указано'}
- Цели обучения: {', '.join(student.learning_goals) if student.learning_goals else 'Не определены'}
- Карьерные цели: {student.career_goals or 'Не определены'}
- Временные рамки: {student.timeline or 'Не определены'}
- Стиль обучения: {student.learning_style or 'Не определен'}
- Доступность времени: {student.time_availability or 'Не указана'}
- Предпочитаемая сложность: {student.preferred_difficulty or 'Не определена'}
- Оценочный балл: {student.assessment_score or 'Не оценен'}
- Сильные области: {', '.join(student.strong_areas) if student.strong_areas else 'Не определены'}
- Слабые области: {', '.join(student.weak_areas) if student.weak_areas else 'Не определены'}
- Рекомендованные темы: {topics or 'Не определены'}
- Текущая тема: {current_topic}
- Прогресс завершения: {student.get_profile_completion_percentage()}%"""

    def _extract_commands(self, text: str) -> Tuple[List[Dict], str]:
        """Извлекает команды из текста и возвращает чистый текст"""
        commands = []
        clean_text = text

        for match in self.command_pattern.finditer(text):
            command_name = match.group(1)
            params = match.group(2).split(':') if match.group(2) else []

            commands.append({
                "name": command_name,
                "params": params,
                "raw": match.group(0)
            })

            # Убираем команду из текста
            clean_text = clean_text.replace(match.group(0), "")

        # Очищаем лишние пробелы
        clean_text = " ".join(clean_text.split())

        return commands, clean_text

    async def _execute_commands(
            self,
            student: model.Student,
            chat_id: int,
            commands: list[dict]
    ) -> list[dict[str, Any]]:
        """Выполняет извлеченные команды"""
        results = []

        for cmd in commands:
            try:
                result = await self._execute_single_command(
                    student=student,
                    chat_id=chat_id,
                    command=cmd
                )
                results.append(result)
            except Exception as e:
                results.append({
                    "name": cmd["name"],
                    "success": False,
                    "error": str(e)
                })

        return results

    async def _execute_single_command(
            self,
            student: model.Student,
            chat_id: int,
            command: Dict
    ) -> Dict[str, Any]:
        """Выполняет одну команду"""
        cmd_name = command["name"]
        params = command["params"]

        # Переключение экспертов
        if cmd_name.startswith("switch_to_"):
            new_expert = cmd_name.replace("switch_to_", "")
            self.chat_experts[chat_id] = new_expert
            return {
                "name": cmd_name,
                "success": True,
                "type": "expert_switch",
                "data": {"new_expert": new_expert}
            }

        # Обновление профиля студента
        if cmd_name.startswith("update_"):
            field_name = cmd_name.replace("update_", "")
            if params and hasattr(student, field_name):
                value = params[0]

                # Преобразование типов для списков
                if field_name in ["known_languages", "learning_goals", "strong_areas", "weak_areas"]:
                    value = json.loads(value) if value.startswith('[') else [value]

                # Преобразование для числовых полей
                if field_name == "assessment_score":
                    value = int(value)

                # Обновляем студента
                updates = {field_name: value}
                student.update_from_dict(updates)
                await self.student_repo.update(student)

                return {
                    "name": cmd_name,
                    "success": True,
                    "type": "profile_update",
                    "data": {"field": field_name, "value": value}
                }

        # Установка этапа интервью
        if cmd_name == "set_interview_stage" and params:
            student.interview_stage = params[0]
            await self.student_repo.update(student)
            return {
                "name": cmd_name,
                "success": True,
                "type": "interview_stage",
                "data": {"stage": params[0]}
            }

        # Завершение интервью
        if cmd_name == "complete_interview":
            student.interview_completed = True
            await self.student_repo.update(student)
            return {
                "name": cmd_name,
                "success": True,
                "type": "interview_complete",
                "data": {}
            }

        # Навигация по контенту
        if cmd_name.startswith("nav_to_"):
            content_type = cmd_name.replace("nav_to_", "")
            if params and content_type in ["topic", "block", "chapter"]:
                content_id = int(params[0])

                if content_type == "topic":
                    student.current_topic_id = content_id
                elif content_type == "block":
                    student.current_block_id = content_id
                elif content_type == "chapter":
                    student.current_chapter_id = content_id

                await self.student_repo.update(student)
                return {
                    "name": cmd_name,
                    "success": True,
                    "type": "navigation",
                    "data": {
                        "content_type": content_type,
                        "content_id": content_id
                    }
                }

        # Команда не распознана
        return {
            "name": cmd_name,
            "success": False,
            "error": f"Unknown command: {cmd_name}"
        }

    async def _save_messages(
            self,
            chat_id: int,
            user_message: str,
            assistant_message: str,
            expert: str
    ):
        """Сохраняет сообщения в БД"""
        # Сохраняем сообщение пользователя
        await self.chat_repo.add_message(
            chat_id=chat_id,
            text=user_message,
            role="user"
        )

        # Сохраняем ответ ассистента с меткой эксперта
        await self.chat_repo.add_message(
            chat_id=chat_id,
            text=f"[{expert}] {assistant_message}",
            role="assistant"
        )

    def _load_prompts(self) -> Dict[str, str]:
        """Загружает промпты из вашего документа"""
        # Здесь можно загрузить из файла или БД
        # Пока возвращаем заглушку
        return {
            "base_context": "СИСТЕМА AI-МЕНТОРА...",
            "registrar_prompt": "КТО ТЫ: Ты регистратор...",
            "interview_expert_prompt": "КТО ТЫ: Ты эксперт по интервью...",
            "teacher_prompt": "КТО ТЫ: Ты опытный преподаватель...",
            "test_expert_prompt": "КТО ТЫ: Ты эксперт по тестированию...",
            "career_consultant_prompt": "КТО ТЫ: Ты карьерный консультант...",
            "progress_analyst_prompt": "КТО ТЫ: Ты аналитик прогресса...",
            "global_rules": "КОМАНДЫ ПЕРЕКЛЮЧЕНИЯ ЭКСПЕРТОВ..."
        }