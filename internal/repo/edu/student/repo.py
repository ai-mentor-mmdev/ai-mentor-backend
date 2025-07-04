import json
import logging
from typing import Optional, Dict, Any
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface, model
from .query import *


class StudentRepo(interface.IStudentRepo):
    def __init__(
            self,
            db: interface.IDB,
            tel: interface.ITelemetry
    ):
        self.db = db
        self.tracer = tel.tracer()
        self.logger = tel.logger()

    async def create(self, student: model.Student) -> int:
        with self.tracer.start_as_current_span(
                "StudentRepo.create",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": student.account_id,
                    "login": student.login
                }
        ) as span:
            try:
                params = self._student_to_db_params(student)
                student_id = await self.db.insert(CREATE_STUDENT_QUERY, params)

                span.set_status(Status(StatusCode.OK))
                self.logger.info(f"Создан новый студент с ID: {student_id}")
                return student_id

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка создания студента: {err}")
                raise err

    async def get_by_id(self, student_id: int) -> Optional[model.Student]:
        with self.tracer.start_as_current_span(
                "StudentRepo.get_by_id",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                rows = await self.db.select(GET_STUDENT_BY_ID_QUERY, {"student_id": student_id})

                if not rows:
                    span.set_status(Status(StatusCode.OK))
                    return None

                students = model.Student.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return students[0] if students else None

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка получения студента по ID {student_id}: {err}")
                raise err

    async def get_by_account_id(self, account_id: int) -> Optional[model.Student]:
        with self.tracer.start_as_current_span(
                "StudentRepo.get_by_account_id",
                kind=SpanKind.INTERNAL,
                attributes={"account_id": account_id}
        ) as span:
            try:
                rows = await self.db.select(GET_STUDENT_BY_ACCOUNT_ID_QUERY, {"account_id": account_id})

                if not rows:
                    span.set_status(Status(StatusCode.OK))
                    return None

                students = model.Student.serialize(rows)
                span.set_status(Status(StatusCode.OK))
                return students[0] if students else None

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка получения студента по account_id {account_id}: {err}")
                raise err

    async def update(self, student: model.Student) -> None:
        with self.tracer.start_as_current_span(
                "StudentRepo.update",
                kind=SpanKind.INTERNAL,
                attributes={
                    "student_id": student.id,
                    "interview_stage": student.interview_stage
                }
        ) as span:
            try:
                params = self._student_to_db_params(student)
                params["id"] = student.id

                await self.db.update(UPDATE_STUDENT_QUERY, params)

                span.set_status(Status(StatusCode.OK))
                self.logger.info(f"Обновлен профиль студента {student.id}")

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка обновления студента {student.id}: {err}")
                raise err

    async def update_profile_fields(self, student_id: int, updates: dict) -> None:
        with self.tracer.start_as_current_span(
                "StudentRepo.update_profile_fields",
                kind=SpanKind.INTERNAL,
                attributes={
                    "student_id": student_id,
                    "fields_count": len(updates)
                }
        ) as span:
            try:
                if not updates:
                    span.set_status(Status(StatusCode.OK))
                    return

                # Формируем динамический запрос для обновления только нужных полей
                set_clauses = []
                params = {"student_id": student_id}

                for field, value in updates.items():
                    if hasattr(model.Student, field):
                        set_clauses.append(f"{field} = :{field}")
                        params[field] = self._serialize_field_value(value)

                if not set_clauses:
                    span.set_status(Status(StatusCode.OK))
                    return

                query = UPDATE_PROFILE_FIELDS_QUERY.format(
                    fields_to_update=", ".join(set_clauses)
                )

                await self.db.update(query, params)

                span.set_status(Status(StatusCode.OK))
                self.logger.info(f"Обновлены поля профиля студента {student_id}: {list(updates.keys())}")

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка обновления полей профиля студента {student_id}: {err}")
                raise err

    async def set_interview_stage(self, student_id: int, stage: str) -> None:
        with self.tracer.start_as_current_span(
                "StudentRepo.set_interview_stage",
                kind=SpanKind.INTERNAL,
                attributes={
                    "student_id": student_id,
                    "stage": stage
                }
        ) as span:
            try:
                await self.db.update(SET_INTERVIEW_STAGE_QUERY, {
                    "student_id": student_id,
                    "stage": stage
                })

                span.set_status(Status(StatusCode.OK))
                self.logger.info(f"Установлен этап интервью {stage} для студента {student_id}")

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка установки этапа интервью для студента {student_id}: {err}")
                raise err

    async def is_interview_completed(self, student_id: int) -> bool:
        with self.tracer.start_as_current_span(
                "StudentRepo.is_interview_completed",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                rows = await self.db.select(CHECK_INTERVIEW_COMPLETED_QUERY, {"student_id": student_id})

                if not rows:
                    span.set_status(Status(StatusCode.OK))
                    return False

                result = bool(rows[0].interview_completed) if rows[0].interview_completed is not None else False
                span.set_status(Status(StatusCode.OK))
                return result

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка проверки завершения интервью для студента {student_id}: {err}")
                raise err

    def _student_to_db_params(self, student: model.Student) -> Dict[str, Any]:
        """Преобразует объект Student в параметры для БД"""
        return {
            "account_id": student.account_id,
            "login": student.login,
            "password": student.password,
            "interview_stage": student.interview_stage,
            "interview_completed": student.interview_completed,
            "programming_experience": student.programming_experience,
            "known_languages": json.dumps(student.known_languages) if student.known_languages else None,
            "work_experience": student.work_experience,
            "education_background": student.education_background,
            "learning_goals": json.dumps(student.learning_goals) if student.learning_goals else None,
            "career_goals": student.career_goals,
            "timeline": student.timeline,
            "learning_style": student.learning_style,
            "time_availability": student.time_availability,
            "preferred_difficulty": student.preferred_difficulty,
            "skip_topics": json.dumps(student.skip_topics) if student.skip_topics else None,
            "skip_blocks": json.dumps(student.skip_blocks) if student.skip_blocks else None,
            "focus_areas": json.dumps(student.focus_areas) if student.focus_areas else None,
            "recommended_topics": json.dumps(student.recommended_topics) if student.recommended_topics else None,
            "recommended_blocks": json.dumps(student.recommended_blocks) if student.recommended_blocks else None,
            "approved_topics": json.dumps(student.approved_topics) if student.approved_topics else None,
            "approved_blocks": json.dumps(student.approved_blocks) if student.approved_blocks else None,
            "approved_chapters": json.dumps(student.approved_chapters) if student.approved_chapters else None,
            "assessment_score": student.assessment_score,
            "strong_areas": json.dumps(student.strong_areas) if student.strong_areas else None,
            "weak_areas": json.dumps(student.weak_areas) if student.weak_areas else None,
            "learning_path": json.dumps(student.learning_path) if student.learning_path else None,
            "current_topic_id": student.current_topic_id,
            "current_block_id": student.current_block_id,
            "current_chapter_id": student.current_chapter_id,
        }

    def _serialize_field_value(self, value: Any) -> Any:
        """Сериализует значение поля для сохранения в БД"""
        if isinstance(value, (list, dict)):
            return json.dumps(value)
        return value