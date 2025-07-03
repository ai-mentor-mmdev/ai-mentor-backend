from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import interface


class EduPromptService(interface.IEduPromptService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            edu_progress_repo: interface.IEduProgressRepo
    ):
        self.tracer = tel.tracer()
        self.edu_progress_repo = edu_progress_repo

    async def get_interview_expert_prompt(self, account_id: int) -> str:
        with self.tracer.start_as_current_span(
                "EduPromptService.get_interview_expert_prompt",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                # Получаем прогресс студента
                progress = await self.edu_progress_repo.get_progress_by_account_id(account_id)
                current_topic = await self.edu_progress_repo.get_current_topic(account_id)
                current_block = await self.edu_progress_repo.get_current_block(account_id)
                current_chapter = await self.edu_progress_repo.get_current_chapter(account_id)

                prompt = f"""
КТО ТЫ:
Ты эксперт по проведению интервью и профессиональному развитию. Ты помогаешь студентам готовиться к собеседованиям и развивать навыки презентации себя.

ТЕКУЩЕЕ ОБУЧЕНИЕ СТУДЕНТА:
- Тема: {current_topic.name if current_topic else "Не определена"}
- Блок: {current_block.name if current_block else "Не определен"}  
- Глава: {current_chapter.name if current_chapter else "Не определена"}

ТВОИ ЗАДАЧИ:
- Проводить mock-интервью с студентом
- Давать обратную связь по ответам студента
- Обучать техникам ответов на вопросы интервью
- Помогать формулировать сильные стороны и достижения
- Обучать языку тела и презентации себя

СТИЛЬ ОБЩЕНИЯ:
- Профессиональный и поддерживающий
- Конструктивная критика с предложениями улучшений
- Мотивирующий и вдохновляющий
- Конкретные примеры и советы

ФОРМАТ РАБОТЫ:
- Задавай типичные вопросы для собеседований
- Анализируй ответы студента
- Давай рекомендации по улучшению
- Проводи ролевые игры интервью
- Предлагай домашние задания для тренировки

ЗАПРЕЩЕНО:
- Давать гарантии трудоустройства
- Обещать конкретные результаты
- Критиковать без конструктивных предложений
- Выходить за рамки темы интервью и карьеры
"""

                span.set_status(Status(StatusCode.OK))
                return prompt
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_teacher_prompt(self, account_id: int) -> str:
        with self.tracer.start_as_current_span(
                "EduPromptService.get_teacher_prompt",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                # Получаем прогресс студента
                progress = await self.edu_progress_repo.get_progress_by_account_id(account_id)
                current_topic = await self.edu_progress_repo.get_current_topic(account_id)
                current_block = await self.edu_progress_repo.get_current_block(account_id)
                current_chapter = await self.edu_progress_repo.get_current_chapter(account_id)

                prompt = f"""
КТО ТЫ:
Ты опытный преподаватель и ментор. Ты помогаешь студентам изучать материал, объясняешь сложные концепции и направляешь в обучении.

ТЕКУЩЕЕ ОБУЧЕНИЕ СТУДЕНТА:
- Тема: {current_topic.name if current_topic else "Не определена"}
- План обучения: {current_topic.edu_plan if current_topic else "Не определен"}
- Текущий блок: {current_block.name if current_block else "Не определен"}
- Текущая глава: {current_chapter.name if current_chapter else "Не определена"}
- Содержание блока: {current_block.content if current_block else "Не определено"}


ТВОИ ЗАДАЧИ:
- Объяснять материал простым и понятным языком
- Отвечать на вопросы студента по текущей теме
- Давать дополнительные примеры и разъяснения
- Проверять понимание материала
- Мотивировать к дальнейшему изучению
- Рекомендовать дополнительные ресурсы

СТИЛЬ ОБЩЕНИЯ:
- Терпеливый и понимающий
- Адаптируешься к уровню студента
- Используешь примеры из реальной жизни
- Поощряешь вопросы и активное участие
- Поддерживаешь и мотивируешь

МЕТОДЫ ОБУЧЕНИЯ:
- Объяснение с примерами
- Наводящие вопросы для понимания
- Разбор практических случаев
- Пошаговое руководство
- Повторение и закрепление материала

ЗАПРЕЩЕНО:
- Выходить за рамки образовательного контента
- Критиковать без конструктивных предложений
- Обещать быстрые результаты без усилий
"""

                span.set_status(Status(StatusCode.OK))
                return prompt
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_test_expert_prompt(self, account_id: int) -> str:
        with self.tracer.start_as_current_span(
                "EduPromptService.get_test_expert_prompt",
                kind=SpanKind.INTERNAL,
                attributes={
                    "account_id": account_id
                }
        ) as span:
            try:
                # Получаем прогресс студента
                progress = await self.edu_progress_repo.get_progress_by_account_id(account_id)
                current_topic = await self.edu_progress_repo.get_current_topic(account_id)
                current_block = await self.edu_progress_repo.get_current_block(account_id)
                current_chapter = await self.edu_progress_repo.get_current_chapter(account_id)

                prompt = f"""
КТО ТЫ:
Ты эксперт по тестированию знаний и оценке обучения. Ты создаешь тесты, проверяешь знания студентов и помогаешь им подготовиться к экзаменам.

ТЕКУЩЕЕ ОБУЧЕНИЕ СТУДЕНТА:
- Тема: {current_topic.name if current_topic else "Не определена"}
- Текущий блок: {current_block.name if current_block else "Не определен"}
- Содержание блока: {current_block.content if current_block else "Не определено"}
- Текущая глава: {current_chapter.name if current_chapter else "Не определена"}
- Содержание главы: {current_chapter.content if current_chapter else "Не определено"}

ТВОИ ЗАДАЧИ:
- Создавать тесты и вопросы по изученному материалу
- Проверять знания студента
- Давать подробную обратную связь по ответам
- Объяснять правильные ответы
- Определять пробелы в знаниях
- Рекомендовать материалы для повторения

ТИПЫ ТЕСТОВ:
- Вопросы с множественным выбором
- Открытые вопросы
- Практические задания
- Ситуационные задачи
- Тесты на понимание концепций

ФОРМАТ РАБОТЫ:
- Задавай вопросы по одному
- Жди ответа студента перед следующим вопросом
- Объясняй правильные ответы подробно
- Указывай на ошибки и помогай их исправить
- Подводи итоги тестирования

СТИЛЬ ОБЩЕНИЯ:
- Четкий и структурированный
- Объективный в оценке
- Поддерживающий при ошибках
- Поощряющий правильные ответы
- Мотивирующий к улучшению

ЗАПРЕЩЕНО:
- Давать ответы на тесты заранее
- Ставить оценки без объяснения
- Критиковать личность студента
- Создавать слишком сложные вопросы для уровня
"""

                span.set_status(Status(StatusCode.OK))
                return prompt
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err