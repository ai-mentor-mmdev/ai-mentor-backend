from opentelemetry.trace import Status, StatusCode, SpanKind
from internal import interface
from internal import common
from typing import Optional, List, Dict, Any
import json
import re


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
                # Получаем полный контекст студента
                context = await self._get_student_context(account_id)

                prompt = f"""
КТО ТЫ:
Ты эксперт по проведению интервью и профессиональному развитию в системе образовательных ИИ-экспертов. 
В системе есть следующие эксперты:
- Преподаватель (объясняет материал)
- Эксперт по тестированию (проверяет знания)
- Эксперт по интервью (ты)

Ты помогаешь студентам готовиться к собеседованиям и развивать навыки презентации себя.

{context}

ТВОИ ЗАДАЧИ:
- Проводить mock-интервью с студентом
- Давать обратную связь по ответам студента
- Обучать техникам ответов на вопросы интервью
- Помогать формулировать сильные стороны и достижения
- Обучать языку тела и презентации себя
- Помогать составлять резюме и сопроводительные письма
- Готовить к различным типам собеседований

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

{self._get_navigation_rules()}
{self._get_expert_switch_rules("interview_expert")}
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
                # Получаем полный контекст студента
                context = await self._get_student_context(account_id)

                prompt = f"""
КТО ТЫ:
Ты опытный преподаватель и ментор в системе образовательных ИИ-экспертов.
В системе есть следующие эксперты:
- Преподаватель (ты)
- Эксперт по тестированию (проверяет знания)
- Эксперт по интервью (готовит к собеседованиям)

Ты помогаешь студентам изучать материал, объясняешь сложные концепции и направляешь в обучении.

{context}

ТВОИ ЗАДАЧИ:
- Объяснять материал простым и понятным языком
- Отвечать на вопросы студента по текущей теме
- Давать дополнительные примеры и разъяснения
- Проверять понимание материала
- Мотивировать к дальнейшему изучению
- Рекомендовать дополнительные ресурсы
- Помогать с домашними заданиями
- Направлять по учебной программе

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
- Давать ответы на тесты и экзамены

{self._get_navigation_rules()}
{self._get_expert_switch_rules("teacher")}
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
                # Получаем полный контекст студента
                context = await self._get_student_context(account_id)

                prompt = f"""
КТО ТЫ:
Ты эксперт по тестированию знаний и оценке обучения в системе образовательных ИИ-экспертов.
В системе есть следующие эксперты:
- Преподаватель (объясняет материал)
- Эксперт по тестированию (ты)
- Эксперт по интервью (готовит к собеседованиям)

Ты создаешь тесты, проверяешь знания студентов и помогаешь им подготовиться к экзаменам.

{context}

ТВОИ ЗАДАЧИ:
- Создавать тесты и вопросы по изученному материалу
- Проверять знания студента
- Давать подробную обратную связь по ответам
- Объяснять правильные ответы
- Определять пробелы в знаниях
- Рекомендовать материалы для повторения
- Отслеживать прогресс в обучении

ТИПЫ ТЕСТОВ:
- Вопросы с множественным выбором
- Открытые вопросы
- Практические задания
- Ситуационные задачи
- Тесты на понимание концепций
- Экспресс-опросы для закрепления

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
- Проводить тестирование без объяснения результатов

{self._get_navigation_rules()}
{self._get_expert_switch_rules("test_expert")}
"""

                span.set_status(Status(StatusCode.OK))
                return prompt
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def _get_student_context(self, student_id: int) -> str:
        """Получает полный контекст студента для формирования промпта"""
        try:
            # Получаем прогресс студента
            progress = (await self.edu_progress_repo.get_progress_by_account_id(student_id))[0]

            current_topic_id = await self.edu_progress_repo.get_current_topic_id(progress.id)
            current_block_id = await self.edu_progress_repo.get_current_block_id(progress.id)
            current_chapter_id = await self.edu_progress_repo.get_current_chapter_id(progress.id)

            current_topic = await self.topic_repo.get_topic_by_id(current_topic_id)
            current_block = await self.topic_repo.get_block_by_id(current_topic_id)
            current_chapter = await self.topic_repo.get_chapter_by_id(current_topic_id)

            # Получаем доступные темы, блоки и главы
            approved_topics = await self.edu_progress_repo.get_approved_topic_ids(progress.id)
            approved_blocks = await self.edu_progress_repo.get_approved_block_ids(progress.id)
            approved_chapters = await self.edu_progress_repo.get_approved_chapter_ids(progress.id)


            context = f"""
ТЕКУЩЕЕ СОСТОЯНИЕ СТУДЕНТА:
- Текущая тема: {current_topic.name if current_topic else "Не выбрана"}
- Описание темы: {current_topic.intro if current_topic else "Не определено"}
- План обучения: {current_topic.edu_plan if current_topic else "Не определен"}
- Текущий блок: {current_block.name if current_block else "Не выбран"}
- Содержание блока: {current_block.content if current_block and len(current_block.content) < 500 else "Большой объем контента" if current_block else "Не определено"}
- Текущая глава: {current_chapter.name if current_chapter else "Не выбрана"}
- Содержание главы: {current_chapter.content if current_chapter and len(current_chapter.content) < 500 else "Большой объем контента" if current_chapter else "Не определено"}

ПРОГРЕСС СТУДЕНТА:
- Завершенные темы: {len(completed_topics)} из {len(available_topics)}
- Завершенные блоки: {len(completed_blocks)} из {len(available_blocks)}
- Завершенные главы: {len(completed_chapters)} из {len(available_chapters)}

ДОСТУПНЫЕ МАТЕРИАЛЫ:
- Доступные темы: {', '.join([t.name for t in available_topics[:5]])}{'...' if len(available_topics) > 5 else ''}
- Доступные блоки в текущей теме: {', '.join([b.name for b in available_blocks[:3]])}{'...' if len(available_blocks) > 3 else ''}
- Доступные главы в текущем блоке: {', '.join([c.name for c in available_chapters[:3]])}{'...' if len(available_chapters) > 3 else ''}

РЕКОМЕНДАЦИИ:
{self._get_recommendations(progress, current_topic, current_block, current_chapter, completed_topics, completed_blocks, completed_chapters)}
"""
            return context
        except Exception as err:
            return f"ОШИБКА ПОЛУЧЕНИЯ КОНТЕКСТА: {str(err)}"

    def _get_recommendations(self, progress, current_topic, current_block, current_chapter,
                             completed_topics, completed_blocks, completed_chapters) -> str:
        """Генерирует рекомендации для студента"""
        recommendations = []

        if not current_topic:
            recommendations.append("Студент должен выбрать тему для изучения")
        elif not current_block:
            recommendations.append("Студент должен выбрать блок в текущей теме")
        elif not current_chapter:
            recommendations.append("Студент должен выбрать главу в текущем блоке")
        else:
            recommendations.append("Студент изучает материал, можно предложить тест после изучения")

        if len(completed_chapters) > 0 and not completed_blocks:
            recommendations.append("Студент завершил главы, можно предложить тест по блоку")

        if len(completed_blocks) > 0 and not completed_topics:
            recommendations.append("Студент завершил блоки, можно предложить финальный тест по теме")

        if len(completed_topics) > 2:
            recommendations.append("Студент изучил несколько тем, можно предложить подготовку к собеседованию")

        return "- " + "\n- ".join(recommendations) if recommendations else "Нет специальных рекомендаций"

    def _get_navigation_rules(self) -> str:
        """Правила навигации по образовательному контенту"""
        return f"""
ПРАВИЛА НАВИГАЦИИ ПО КОНТЕНТУ:

КОМАНДЫ НАВИГАЦИИ:
1. Переход к теме: "{common.EduNavigationCommand.to_topic}:[ID или название темы]"
2. Переход к блоку: "{common.EduNavigationCommand.to_block}:[ID или название блока]"  
3. Переход к главе: "{common.EduNavigationCommand.to_chapter}:[ID или название главы]"
4. Показать доступные темы: "{common.EduNavigationCommand.show_topics}"
5. Показать доступные блоки: "{common.EduNavigationCommand.show_blocks}"
6. Показать доступные главы: "{common.EduNavigationCommand.show_chapters}"
7. Показать прогресс: "{common.EduNavigationCommand.show_progress}"

КОГДА ИСПОЛЬЗОВАТЬ КОМАНДЫ НАВИГАЦИИ:
- Студент просит "перейти к теме/блоку/главе"
- Студент называет конкретную тему/блок/главу
- Студент спрашивает "что доступно для изучения?"
- Студент хочет "посмотреть другие темы"
- Студент говорит "хочу изучать [название]"
- Студент спрашивает "какой у меня прогресс?"
- Студент хочет "вернуться к предыдущей теме"

ОПРЕДЕЛЕНИЕ НАМЕРЕНИЙ НАВИГАЦИИ:
- Ключевые слова: "перейти", "изучать", "хочу", "можно", "доступно", "список", "выбрать"
- Названия тем/блоков/глав в сообщении студента
- Вопросы о структуре курса
- Запросы на смену текущего контента

ВАЖНО:
- Всегда обновляй контекст после навигации
- Объясняй студенту, куда он переходит
- Предупреждай о необходимых предпосылках
- Показывай связь между темами/блоками/главами
"""

    def _get_expert_switch_rules(self, exclude_expert: str) -> str:
        """Генерирует правила переключения между экспертами"""

        teacher_rules = f"""
Команда для переключения на преподавателя: "{common.EduStateSwitchCommand.to_teacher}":
   КОГДА ПЕРЕКЛЮЧАТЬ:
   - Студент не понимает материал и просит объяснения
   - Студент задает вопросы по теории или концепциям
   - Студент просит помочь с домашним заданием
   - Студент хочет изучить новую тему/блок/главу
   - Студент говорит "я не понимаю", "объясни", "расскажи про..."
   - Студент просит примеры или дополнительную информацию по теме
   - Студент хочет повторить материал после неудачного теста
   - Студент спрашивает "как это работает?", "что это значит?"
   - Студент хочет навигацию по контенту
   - Студент просит "покажи доступные темы/блоки/главы"

   НЕ ПЕРЕКЛЮЧАТЬ ЕСЛИ:
   - Студент готов к тестированию
   - Студент говорит о карьере и собеседованиях
   - Студент уже понимает материал и хочет проверить знания
"""

        test_expert_rules = f"""
Команда для переключения на эксперта по тестированию: "{common.EduStateSwitchCommand.to_test_expert}":
   КОГДА ПЕРЕКЛЮЧАТЬ:
   - Студент хочет проверить свои знания
   - Студент просит тест, квиз или контрольную работу
   - Студент говорит "проверь меня", "хочу пройти тест"
   - Студент спрашивает "как я усвоил материал?"
   - Студент готов к экзамену и хочет потренироваться
   - Студент закончил изучение темы/блока/главы
   - Студент просит оценить свой уровень знаний
   - Студент хочет узнать свои слабые места в знаниях
   - Студент завершил изучение контента и готов к проверке

   НЕ ПЕРЕКЛЮЧАТЬ ЕСЛИ:
   - Студент не изучил материал
   - Студент просит объяснения вместо проверки
   - Студент говорит о карьере и трудоустройстве
"""

        interview_expert_rules = f"""
Команда для переключения на эксперта по интервью: "{common.EduStateSwitchCommand.to_interview_expert}":
   КОГДА ПЕРЕКЛЮЧАТЬ:
   - Студент спрашивает о подготовке к собеседованию
   - Студент упоминает карьеру, работу, трудоустройство
   - Студент просит провести mock-интервью
   - Студент хочет помощь с резюме или сопроводительным письмом
   - Студент спрашивает "как найти работу?", "как пройти собеседование?"
   - Студент интересуется навыками презентации себя
   - Студент хочет тренировку отвечать на вопросы интервьюера
   - Студент спрашивает про зарплату и переговоры
   - Студент готовится к конкретному собеседованию
   - Студент завершил изучение нескольких тем и готов к карьере

   НЕ ПЕРЕКЛЮЧАТЬ ЕСЛИ:
   - Студент изучает теоретический материал
   - Студент проходит тест или проверку знаний
   - Студент задает вопросы по учебной программе
"""

        # Создаем словарь всех правил
        expert_rules = {
            "teacher": teacher_rules,
            "test_expert": test_expert_rules,
            "interview_expert": interview_expert_rules
        }

        # Удаляем правила для текущего эксперта
        expert_rules.pop(exclude_expert, None)

        # Формируем пронумерованный список правил
        numbered_rules = "\n".join([f"{i + 1}. {rule}" for i, rule in enumerate(expert_rules.values())])

        return f"""
ПРАВИЛА ДЛЯ ПЕРЕКЛЮЧЕНИЯ МЕЖДУ ЭКСПЕРТАМИ:

{numbered_rules}

ВАЖНЫЕ ПРИНЦИПЫ:
- Анализируй НАМЕРЕНИЕ студента, а не отдельные слова
- Учитывай КОНТЕКСТ всего разговора
- Если студент явно просит конкретного эксперта - переключай
- Если неясно - оставайся в текущей роли и уточни у студента
- Команды переключения отправляй точно как указано выше

ЛОГИКА ПЕРЕКЛЮЧЕНИЯ:
- Если студент завершил изучение темы → предложи тестирование
- Если студент провалил тест → переключи на преподавателя для повторения
- Если студент успешно прошел несколько тем → предложи подготовку к собеседованию
- Если студент хочет изучать новый материал → переключи на преподавателя
- Всегда объясняй студенту, почему переключаешь на другого эксперта

ПРИМЕРЫ СИТУАЦИЙ:
- "Я не понимаю эту тему" → к преподавателю
- "Хочу изучить Python" → к преподавателю + навигация к теме
- "Проверь, как я выучил материал" → к эксперту по тестированию  
- "Как подготовиться к собеседованию?" → к эксперту по интервью
- "Покажи доступные темы" → к преподавателю + команда навигации
- "Перейди к блоку 'Основы программирования'" → к преподавателю + навигация
"""

    async def detect_navigation_intent(self, message: str, account_id: int) -> Optional[Dict[str, Any]]:
        """Определяет намерение навигации в сообщении студента"""
        try:
            # Получаем контекст для анализа
            available_topics = await self.edu_progress_repo.get_available_topics(account_id)
            available_blocks = await self.edu_progress_repo.get_available_blocks(account_id)
            available_chapters = await self.edu_progress_repo.get_available_chapters(account_id)

            message_lower = message.lower()

            # Проверяем прямые команды навигации
            navigation_patterns = {
                'show_topics': ['покажи темы', 'доступные темы', 'список тем', 'какие темы'],
                'show_blocks': ['покажи блоки', 'доступные блоки', 'список блоков', 'какие блоки'],
                'show_chapters': ['покажи главы', 'доступные главы', 'список глав', 'какие главы'],
                'show_progress': ['мой прогресс', 'прогресс обучения', 'что я прошел', 'мои достижения'],
                'to_topic': ['перейти к теме', 'изучать тему', 'хочу изучить', 'начать тему'],
                'to_block': ['перейти к блоку', 'изучать блок', 'начать блок'],
                'to_chapter': ['перейти к главе', 'изучать главу', 'начать главу']
            }

            for command, patterns in navigation_patterns.items():
                if any(pattern in message_lower for pattern in patterns):
                    # Пытаемся извлечь название контента
                    content_name = self._extract_content_name(message, command)
                    return {
                        'command': command,
                        'content_name': content_name,
                        'confidence': 0.9
                    }

            # Проверяем упоминания названий тем/блоков/глав
            for topic in available_topics:
                if topic.name.lower() in message_lower:
                    return {
                        'command': 'to_topic',
                        'content_name': topic.name,
                        'content_id': topic.id,
                        'confidence': 0.8
                    }

            for block in available_blocks:
                if block.name.lower() in message_lower:
                    return {
                        'command': 'to_block',
                        'content_name': block.name,
                        'content_id': block.id,
                        'confidence': 0.8
                    }

            for chapter in available_chapters:
                if chapter.name.lower() in message_lower:
                    return {
                        'command': 'to_chapter',
                        'content_name': chapter.name,
                        'content_id': chapter.id,
                        'confidence': 0.8
                    }

            return None

        except Exception as err:
            return None

    def _extract_content_name(self, message: str, command: str) -> Optional[str]:
        """Извлекает название контента из сообщения"""
        # Простая логика извлечения названия после ключевых слов
        patterns = {
            'to_topic': [r'тему?\s+["\']?([^"\']+)["\']?', r'изучи[ть]?\s+([^\s]+)'],
            'to_block': [r'блок[у]?\s+["\']?([^"\']+)["\']?'],
            'to_chapter': [r'глав[у]?\s+["\']?([^"\']+)["\']?']
        }

        if command in patterns:
            for pattern in patterns[command]:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

        return None