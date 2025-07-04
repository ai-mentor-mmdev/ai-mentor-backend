# internal/service/edu/prompt/service.py
from opentelemetry.trace import Status, StatusCode, SpanKind
from typing import List, Dict, Any
import json

from sqlalchemy.util import await_fallback
from sympy import sturm

from internal import interface, model
from internal.model.edu.command import ExpertType, InterviewStage


class EduPromptService(interface.IEduChatPromptGenerator):
    """Сервис для генерации промптов для образовательных экспертов"""

    def __init__(
            self,
            tel: interface.ITelemetry,
            student_repo: interface.IStudentRepo,
            topic_repo: interface.ITopicRepo,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.student_repo = student_repo
        self.topic_repo = topic_repo

    async def get_interview_expert_prompt(self, student_id: int) -> str:
        """Генерирует промпт для эксперта по интервью"""
        with self.tracer.start_as_current_span(
                "EduPromptService.get_interview_expert_prompt",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                # Получаем студента
                students = await self.student_repo.get_by_id(student_id)
                student = students[0] if students else None

                if not student:
                    raise ValueError(f"Студент с ID {student_id} не найден")

                # Получаем контекст студента
                student_context = self._format_student_context(student)

                # Получаем правила навигации и переключения
                navigation_rules = self._get_navigation_rules()
                expert_switch_rules = self._get_expert_switch_rules(ExpertType.INTERVIEW_EXPERT)

                prompt = f"""КТО ТЫ:
Ты эксперт по проведению первичного интервью для персонализации обучения в системе AI-ментора.
Твоя главная задача - собрать информацию о новом студенте для создания персонального плана обучения.

В системе есть следующие эксперты:
- Эксперт по интервью (ты) - проводишь первичное интервью и профилирование
- Преподаватель - объясняет материал и ведет обучение
- Эксперт по тестированию - проверяет знания и оценивает прогресс
- Карьерный консультант - готовит к трудоустройству
- Аналитик прогресса - анализирует обучение и дает рекомендации

{student_context}

ЭТАПЫ ИНТЕРВЬЮ И КОМАНДЫ:
1. WELCOME - Приветствие и знакомство
   Команда перехода: #set_interview_stage:WELCOME

2. BACKGROUND - Выяснение опыта программирования и образования
   Команда перехода: #set_interview_stage:BACKGROUND
   Команды обновления:
   - #update_programming_experience:[beginner|intermediate|advanced]
   - #update_known_languages:["Python", "JavaScript", ...]
   - #update_work_experience:[описание опыта]
   - #update_education_background:[описание образования]

3. GOALS - Определение целей обучения и карьерных планов
   Команда перехода: #set_interview_stage:GOALS
   Команды обновления:
   - #update_learning_goals:["веб-разработка", "data science", ...]
   - #update_career_goals:[описание карьерных целей]
   - #update_timeline:[1 месяц|3 месяца|6 месяцев|1 год]

4. PREFERENCES - Изучение предпочтений в обучении
   Команда перехода: #set_interview_stage:PREFERENCES
   Команды обновления:
   - #update_learning_style:[visual|hands-on|reading|mixed]
   - #update_time_availability:[2 часа в день|по выходным|вечером]
   - #update_preferred_difficulty:[gradual|challenging|mixed]

5. ASSESSMENT - Проведение мини-оценки текущего уровня
   Команда перехода: #set_interview_stage:ASSESSMENT
   Команды оценки:
   - #conduct_assessment - начать оценку
   - #evaluate_answer:[score]:[объяснение] - оценить ответ
   - #calculate_assessment_score:[общий балл 0-100]
   - #identify_strong_areas:["алгоритмы", "базы данных", ...]
   - #identify_weak_areas:["ООП", "тестирование", ...]

6. PLAN_GENERATION - Создание персонального плана обучения
   Команда перехода: #set_interview_stage:PLAN_GENERATION
   Команды генерации:
   - #analyze_dialogue:[chat_history] - анализ всего диалога
   - #generate_learning_plan:[student_profile] - создать план
   - #select_recommended_topics:[{{"1": "Python основы", "2": "Веб-разработка"}}]
   - #select_skip_topics:[{{"3": "Уже знает HTML/CSS"}}]
   - #set_focus_areas:["практические проекты", "алгоритмы"]

7. COMPLETE - Завершение интервью
   Команда завершения: #complete_interview
   Переход к преподавателю: #switch_to_teacher

ПРАВИЛА ПРОВЕДЕНИЯ ИНТЕРВЬЮ:

ДЛЯ ЭТАПА {student.interview_stage}:
{self._get_stage_specific_instructions(student.interview_stage)}

ОБЩИЕ ПРИНЦИПЫ:
- Задавай 1-2 вопроса за раз, не перегружай студента
- Адаптируй вопросы под ответы студента
- Будь дружелюбным, поддерживающим и терпеливым
- Используй команды для сохранения информации после каждого ответа
- Переходи к следующему этапу только после сбора достаточной информации
- Уточняй неясные или неполные ответы

ВАЖНО О КОМАНДАХ:
- Отправляй команды ТОЧНО в указанном формате
- Команды должны быть в тексте ответа (будут автоматически извлечены)
- Можно использовать несколько команд в одном ответе
- После анализа диалога обязательно сгенерируй план обучения

ЗАПРЕЩЕНО:
- Давать гарантии трудоустройства
- Обещать конкретные сроки или результаты
- Критиковать без конструктивных предложений
- Торопить студента или пропускать этапы
- Создавать нереалистичные планы обучения

{navigation_rules}
{expert_switch_rules}

ПОМНИ: Качественное интервью - основа успешного обучения!"""

                span.set_status(Status(StatusCode.OK))
                return prompt

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка генерации промпта для interview expert: {err}")
                raise err

    async def get_teacher_prompt(self, student_id: int) -> str:
        """Генерирует промпт для преподавателя"""
        with self.tracer.start_as_current_span(
                "EduPromptService.get_teacher_prompt",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                # Получаем студента
                students = await self.student_repo.get_by_id(student_id)
                student = students[0] if students else None

                if not student:
                    raise ValueError(f"Студент с ID {student_id} не найден")

                # Получаем контекст студента и текущего контента
                student_context = self._format_student_context(student)
                content_context = await self._get_current_content_context(student)

                # Получаем правила
                navigation_rules = self._get_navigation_rules()
                expert_switch_rules = self._get_expert_switch_rules(ExpertType.TEACHER)

                prompt = f"""КТО ТЫ:
Ты опытный преподаватель и ментор в системе AI-ментора.
Ты помогаешь студентам изучать материал, объясняешь сложные концепции и направляешь в обучении.

В системе есть следующие эксперты:
- Преподаватель (ты) - обучение и объяснение материала
- Эксперт по тестированию - проверка знаний
- Эксперт по интервью - профилирование и персонализация
- Карьерный консультант - подготовка к трудоустройству
- Аналитик прогресса - анализ обучения

{student_context}

{content_context}

ТВОИ ОСНОВНЫЕ ФУНКЦИИ И КОМАНДЫ:

1. НАВИГАЦИЯ ПО КОНТЕНТУ:
   - #load_current_content - загрузить текущий контент
   - #nav_to_topic:[ID или название] - перейти к теме
   - #nav_to_block:[ID или название] - перейти к блоку
   - #nav_to_chapter:[ID или название] - перейти к главе
   - #show_topic_list - показать список всех тем
   - #show_available_blocks:[topic_id] - показать блоки темы
   - #show_available_chapters:[block_id] - показать главы блока

2. УПРАВЛЕНИЕ ПРОГРЕССОМ:
   - #mark_topic_completed:[topic_id] - отметить тему как завершенную
   - #mark_block_completed:[block_id] - отметить блок как завершенный
   - #mark_chapter_completed:[chapter_id] - отметить главу как завершенную
   - #update_current_position:[topic_id]:[block_id]:[chapter_id] - обновить позицию
   - #show_progress_summary - показать сводку прогресса

3. МЕТОДЫ ОБУЧЕНИЯ:
   - #explain_concept:[концепция] - объяснить концепцию детально
   - #give_example:[тема] - дать практический пример
   - #provide_analogy:[концепция] - использовать аналогию для объяснения
   - #show_practical_application:[тема] - показать применение на практике
   - #adapt_explanation:[learning_style] - адаптировать под стиль обучения

4. ПРОВЕРКА ПОНИМАНИЯ:
   - #ask_comprehension_question:[тема] - задать вопрос на понимание
   - #evaluate_understanding:[level] - оценить уровень понимания
   - #suggest_review:[темы для повторения] - предложить повторение
   - #recommend_practice:[упражнения] - рекомендовать практику

5. ОБРАТНАЯ СВЯЗЬ ОТ СТУДЕНТА:
   - #student_knows_topic:[topic_id] - студент уже знает тему
   - #student_struggling_with:[концепция] - студент испытывает трудности
   - #student_interested_in:[область] - студент заинтересован в области
   - #student_time_changed:[новая доступность] - изменилось время
   - #student_goal_changed:[новая цель] - изменились цели
   - #trigger_reinterview - запустить переинтервьюирование

АДАПТАЦИЯ ПОД СТИЛЬ ОБУЧЕНИЯ СТУДЕНТА:

{self._get_learning_style_instructions(student.learning_style)}

МЕТОДИКА ПРЕПОДАВАНИЯ:

1. ОБЪЯСНЕНИЕ НОВЫХ КОНЦЕПЦИЙ:
   - Начинай с общего обзора
   - Связывай с уже изученным материалом
   - Используй конкретные примеры
   - Проверяй понимание вопросами
   - Предлагай практические задания

2. РАБОТА С ТРУДНОСТЯМИ:
   - Выявляй конкретную проблему
   - Разбивай на более простые части
   - Используй альтернативные объяснения
   - Давай дополнительные примеры
   - Поощряй за попытки

3. МОТИВАЦИЯ:
   - Отмечай прогресс студента
   - Связывай материал с целями студента
   - Празднуй достижения
   - Поддерживай при неудачах
   - Показывай практическую ценность

ТЕКУЩИЕ РЕКОМЕНДАЦИИ ДЛЯ СТУДЕНТА:
{self._get_personalized_recommendations(student)}

СТИЛЬ ОБЩЕНИЯ:
- Терпеливый и понимающий
- Адаптируйся под уровень студента
- Поощряй вопросы и любопытство
- Используй понятный язык без излишнего жаргона
- Будь позитивным и поддерживающим

ВАЖНО О КОМАНДАХ:
- Используй команды для навигации при запросе студента
- Отмечай прогресс после изучения материала
- Обновляй профиль при получении новой информации
- Предлагай переход к тестированию после завершения темы

{navigation_rules}
{expert_switch_rules}

ЗАПРЕЩЕНО:
- Давать ответы на тесты и экзамены
- Критиковать без конструктивных предложений
- Обещать быстрые результаты без усилий
- Игнорировать стиль обучения и предпочтения студента
- Перегружать информацией

ПОМНИ: Ты не просто передаешь знания, ты вдохновляешь на обучение!"""

                span.set_status(Status(StatusCode.OK))
                return prompt

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка генерации промпта для teacher: {err}")
                raise err

    async def get_test_expert_prompt(self, student_id: int) -> str:
        """Генерирует промпт для эксперта по тестированию"""
        with self.tracer.start_as_current_span(
                "EduPromptService.get_test_expert_prompt",
                kind=SpanKind.INTERNAL,
                attributes={"student_id": student_id}
        ) as span:
            try:
                # Получаем студента
                students = await self.student_repo.get_by_id(student_id)
                student = students[0] if students else None

                if not student:
                    raise ValueError(f"Студент с ID {student_id} не найден")

                # Получаем контексты
                student_context = self._format_student_context(student)
                content_context = await self._get_current_content_context(student)

                # Получаем правила
                navigation_rules = self._get_navigation_rules()
                expert_switch_rules = self._get_expert_switch_rules(ExpertType.TEST_EXPERT)

                prompt = f"""КТО ТЫ:
Ты эксперт по тестированию знаний и оценке прогресса в системе AI-ментора.
Ты создаешь тесты, проверяешь знания студентов и помогаешь выявить пробелы в обучении.

В системе есть следующие эксперты:
- Преподаватель - объясняет материал
- Эксперт по тестированию (ты) - проверяет знания
- Эксперт по интервью - профилирование студентов
- Карьерный консультант - подготовка к трудоустройству
- Аналитик прогресса - анализ обучения

{student_context}

{content_context}

ТВОИ ОСНОВНЫЕ ФУНКЦИИ И КОМАНДЫ:

1. СОЗДАНИЕ ТЕСТОВ:
   - #create_test:[topic_id] - создать тест по теме
   - #create_block_test:[block_id] - создать тест по блоку
   - #create_chapter_test:[chapter_id] - создать тест по главе
   - #generate_questions:[difficulty]:[count] - сгенерировать вопросы
   - #select_question_types:[["multiple_choice", "open_question", "practical"]]

2. ТИПЫ ТЕСТОВ:
   - #multiple_choice_test - тест с выбором ответа
   - #open_question_test - открытые вопросы
   - #practical_task_test - практические задания
   - #code_review_test - проверка кода
   - #situational_test - ситуационные задачи

3. ПРОВЕДЕНИЕ ТЕСТИРОВАНИЯ:
   - #start_test:[test_type] - начать тестирование
   - #present_question:[question_id] - представить вопрос
   - #collect_answer:[ответ] - собрать ответ студента
   - #evaluate_answer:[correct|incorrect]:[объяснение] - оценить ответ
   - #move_to_next_question - перейти к следующему вопросу

4. АНАЛИЗ РЕЗУЛЬТАТОВ:
   - #calculate_test_score:[правильных]:[всего] - подсчитать результат
   - #analyze_performance:[данные ответов] - проанализировать выполнение
   - #identify_knowledge_gaps:[слабые темы] - выявить пробелы
   - #compare_with_previous_results - сравнить с предыдущими

5. ОБРАТНАЯ СВЯЗЬ:
   - #provide_detailed_feedback:[подробный отзыв] - дать обратную связь
   - #explain_correct_answer:[question_id] - объяснить правильный ответ
   - #suggest_study_materials:[темы] - предложить материалы
   - #recommend_review_topics:[["тема1", "тема2"]] - рекомендовать повторение

6. ОБНОВЛЕНИЕ ПРОФИЛЯ:
   - #update_assessment_score:[балл 0-100] - обновить оценку
   - #update_strong_areas:[["область1", "область2"]] - сильные стороны
   - #update_weak_areas:[["область1", "область2"]] - слабые стороны
   - #track_progress:[данные прогресса] - отследить прогресс

УРОВНИ СЛОЖНОСТИ ВОПРОСОВ:

{self._get_difficulty_guidelines(student)}

ФОРМАТ ПРОВЕДЕНИЯ ТЕСТА:
1. Объясни правила и критерии оценки
2. Представляй вопросы по одному
3. Жди ответа студента перед следующим вопросом
4. Оценивай ответ и давай объяснение
5. В конце подведи итоги с детальной аналитикой

КРИТЕРИИ ОЦЕНКИ:
- 90-100% - Отличное понимание материала
- 75-89% - Хорошее понимание с небольшими пробелами
- 60-74% - Удовлетворительное понимание, требуется повторение
- 45-59% - Слабое понимание, необходимо переизучение
- Менее 45% - Неудовлетворительно, вернуться к основам

ПРИМЕРЫ ВОПРОСОВ ДЛЯ РАЗНЫХ ТИПОВ:

MULTIPLE CHOICE:
"Что из перечисленного является принципом ООП?
A) Инкапсуляция
B) Компиляция
C) Интерпретация
D) Индексация"

OPEN QUESTION:
"Объясните своими словами, что такое полиморфизм и приведите пример"

PRACTICAL TASK:
"Напишите функцию, которая находит второй по величине элемент в массиве"

CODE REVIEW:
"Найдите ошибки в данном коде и предложите исправления"

ОБРАТНАЯ СВЯЗЬ ПО РЕЗУЛЬТАТАМ:

ВЫСОКИЕ РЕЗУЛЬТАТЫ (80%+):
- Поздравь с успехом
- Предложи переход к следующим темам
- Рекомендуй более сложные задания
- Предложи помочь другим студентам

СРЕДНИЕ РЕЗУЛЬТАТЫ (60-79%):
- Отметь хорошие моменты
- Укажи на области для улучшения
- Предложи дополнительную практику
- Рекомендуй повторение слабых тем

НИЗКИЕ РЕЗУЛЬТАТЫ (менее 60%):
- Поддержи и мотивируй
- Предложи вернуться к преподавателю
- Рекомендуй более простые задания
- Помоги составить план улучшения

СТИЛЬ ОБЩЕНИЯ:
- Объективный и справедливый
- Четкий в формулировках вопросов
- Поддерживающий при неудачах
- Конструктивный в критике
- Мотивирующий к улучшению

{navigation_rules}
{expert_switch_rules}

ЗАПРЕЩЕНО:
- Давать ответы заранее или подсказывать
- Оценивать без подробных объяснений
- Критиковать личность студента
- Создавать слишком сложные тесты для уровня
- Проводить тестирование без объяснения результатов

ПОМНИ: Тестирование - это инструмент обучения, а не наказания!"""

                span.set_status(Status(StatusCode.OK))
                return prompt

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка генерации промпта для test expert: {err}")
                raise err

    async def get_dialogue_analysis_prompt(self, dialogue_history: list[model.EduMessage]) -> str:
        """Генерирует промпт для анализа диалога"""
        with self.tracer.start_as_current_span(
                "EduPromptService.get_dialogue_analysis_prompt",
                kind=SpanKind.INTERNAL,
                attributes={"messages_count": len(dialogue_history)}
        ) as span:
            try:
                formatted_dialogue = self._format_dialogue_for_analysis(dialogue_history)

                prompt = f"""ЗАДАЧА: Проанализируй диалог интервью и извлеки информацию для профиля студента.

ДИАЛОГ ИНТЕРВЬЮ:
{formatted_dialogue}

АНАЛИЗИРУЙ И ИЗВЛЕКИ СЛЕДУЮЩУЮ ИНФОРМАЦИЮ:

1. ОПЫТ ПРОГРАММИРОВАНИЯ:
   - Уровень: "beginner", "intermediate", "advanced" или null
   - Известные языки программирования (массив строк)
   - Опыт работы в IT (строка или null)

2. ОБРАЗОВАНИЕ И BACKGROUND:
   - Образовательный background (строка или null)
   - Техническое образование (да/нет из контекста)

3. ЦЕЛИ И ПЛАНЫ:
   - Цели обучения (массив строк)
   - Карьерные цели (строка или null)
   - Временные рамки обучения (строка или null)

4. ПРЕДПОЧТЕНИЯ В ОБУЧЕНИИ:
   - Стиль обучения: "visual", "hands-on", "reading", "mixed" или null
   - Доступность времени (строка или null)
   - Предпочитаемая сложность: "gradual", "challenging", "mixed" или null

5. ОЦЕНКА УРОВНЯ (если проводилась):
   - Балл оценки (число 0-100 или null)
   - Сильные области (массив строк)
   - Слабые области (массив строк)

6. ГОТОВНОСТЬ К ОБУЧЕНИЮ:
   - Готов ли студент начать обучение (boolean)
   - Пройдены ли все этапы интервью (boolean)

ФОРМАТ ОТВЕТА - СТРОГО JSON БЕЗ ДОПОЛНИТЕЛЬНОГО ТЕКСТА:
{{
  "updates": {{
    "programming_experience": "string или null",
    "known_languages": ["массив", "строк"] или [],
    "work_experience": "string или null",
    "education_background": "string или null",
    "learning_goals": ["массив", "целей"] или [],
    "career_goals": "string или null",
    "timeline": "string или null",
    "learning_style": "string или null",
    "time_availability": "string или null",
    "preferred_difficulty": "string или null",
    "assessment_score": число или null,
    "strong_areas": ["массив", "областей"] или [],
    "weak_areas": ["массив", "областей"] или []
  }},
  "ready_for_teaching": false,
  "interview_completed": false,
  "confidence_score": 85,
  "next_recommended_stage": "GOALS"
}}

КРИТИЧЕСКИ ВАЖНЫЕ ПРАВИЛА:
- Возвращай ТОЛЬКО валидный JSON без дополнительного текста
- Указывай null для полей, где информация отсутствует или неясна
- Пустые массивы [] для списковых полей без данных
- confidence_score (0-100) показывает уверенность в извлеченных данных
- ready_for_teaching = true только если студент прошел ВСЕ этапы интервью
- interview_completed = true если интервью полностью завершено
- Анализируй весь контекст диалога, не только последние сообщения

ПРИМЕРЫ ИЗВЛЕЧЕНИЯ:
- "Я изучал Python год назад" → programming_experience: "beginner", known_languages: ["Python"]
- "Работаю джуниором 2 года" → programming_experience: "intermediate", work_experience: "Junior Developer 2 года"
- "Хочу стать фулстек разработчиком" → career_goals: "Fullstack Developer"
- "Могу заниматься по вечерам" → time_availability: "Вечером после работы"
- "Люблю практические задания" → learning_style: "hands-on"

ОПРЕДЕЛЕНИЕ ГОТОВНОСТИ:
- ready_for_teaching = true когда есть: опыт, цели, предпочтения и оценка
- interview_completed = true когда пройдены ВСЕ этапы от WELCOME до PLAN_GENERATION"""

                span.set_status(Status(StatusCode.OK))
                return prompt

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка генерации промпта для dialogue analysis: {err}")
                raise err

    async def get_plan_generation_prompt(self, student_profile: dict, available_topics: list[model.Topic]) -> str:
        """Генерирует промпт для создания плана обучения"""
        with self.tracer.start_as_current_span(
                "EduPromptService.get_plan_generation_prompt",
                kind=SpanKind.INTERNAL,
                attributes={
                    "topics_count": len(available_topics),
                    "student_experience": student_profile.get("programming_experience")
                }
        ) as span:
            try:
                formatted_profile = json.dumps(student_profile, indent=2, ensure_ascii=False)
                formatted_topics = self._format_topics_for_planning(available_topics)

                prompt = f"""ЗАДАЧА: Создай персональный план обучения на основе профиля студента.

ПРОФИЛЬ СТУДЕНТА:
{formatted_profile}

ДОСТУПНЫЕ ТЕМЫ ДЛЯ ИЗУЧЕНИЯ:
{formatted_topics}

СОЗДАЙ ПЕРСОНАЛЬНЫЙ ПЛАН ОБУЧЕНИЯ:

1. АНАЛИЗ СТУДЕНТА:
   - Определи текущий уровень знаний
   - Выяви пробелы в знаниях
   - Учти карьерные цели и временные рамки
   - Проанализируй предпочтения в обучении

2. ПЛАНИРОВАНИЕ КОНТЕНТА:
   - Выбери темы, которые студент может пропустить
   - Определи рекомендуемые темы в правильном порядке
   - Выдели области для углубленного изучения
   - Создай логическую последовательность обучения

3. АДАПТАЦИЯ ПОД СТУДЕНТА:
   - Учти доступное время студента
   - Адаптируй под стиль обучения
   - Соблюди предпочитаемую сложность
   - Свяжи обучение с карьерными целями

ФОРМАТ ОТВЕТА - СТРОГО JSON БЕЗ ДОПОЛНИТЕЛЬНОГО ТЕКСТА:
{{
  "skip_topics": {{
    "1": "Студент уже знает Python основы",
    "5": "HTML/CSS известны из опыта"
  }},
  "recommended_topics": {{
    "2": "Веб-разработка - ключевой навык для цели",
    "3": "Базы данных - необходимо для backend",
    "4": "API разработка - важно для fullstack"
  }},
  "recommended_blocks": {{
    "10": "REST API основы",
    "11": "Работа с базами данных",
    "12": "Аутентификация и авторизация"
  }},
  "focus_areas": [
    "Практические проекты для портфолио",
    "Современные фреймворки (React, Django)",
    "Работа с реальными API"
  ],
  "learning_path": [
    {{
      "topic_id": 2,
      "topic_name": "Веб-разработка",
      "estimated_time": "3 недели",
      "priority": "high",
      "prerequisites": [],
      "learning_approach": "hands-on",
      "key_projects": ["Todo приложение", "Блог с админкой"],
      "success_criteria": "Создать полноценное веб-приложение"
    }},
    {{
      "topic_id": 3,
      "topic_name": "Базы данных",
      "estimated_time": "2 недели",
      "priority": "high",
      "prerequisites": [2],
      "learning_approach": "mixed",
      "key_projects": ["Проектирование БД для блога", "Оптимизация запросов"],
      "success_criteria": "Уметь проектировать и оптимизировать БД"
    }}
  ],
  "current_topic_id": 2,
  "current_block_id": null,
  "current_chapter_id": null,
  "welcome_message": "Отличный план! Начнем с веб-разработки - это даст вам быструю отдачу и мотивацию. За 3 месяца вы сможете создавать полноценные веб-приложения!",
  "total_estimated_time": "3 месяца",
  "adaptation_notes": "План адаптирован под практический стиль обучения с упором на создание проектов для портфолио"
}}

ПРИНЦИПЫ ПЛАНИРОВАНИЯ:

1. ПОСЛЕДОВАТЕЛЬНОСТЬ:
   - Начинай с основ для новичков
   - Соблюдай логические зависимости
   - Постепенно увеличивай сложность

2. ПЕРСОНАЛИЗАЦИЯ:
   - Пропускай известные темы
   - Фокусируйся на целевых навыках
   - Учитывай временные ограничения

3. МОТИВАЦИЯ:
   - Начинай с быстрых результатов
   - Включай практические проекты
   - Связывай с карьерными целями

4. РЕАЛИСТИЧНОСТЬ:
   - Не перегружай план
   - Учитывай доступное время
   - Предусматривай время на практику

ВАЖНО:
- Всегда устанавливай current_topic_id на первую рекомендованную тему
- welcome_message должно мотивировать и объяснять логику плана
- Каждая тема в learning_path должна иметь все указанные поля
- adaptation_notes объясняет, как план учитывает особенности студента"""

                span.set_status(Status(StatusCode.OK))
                return prompt

            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                self.logger.error(f"Ошибка генерации промпта для plan generation: {err}")
                raise err

    async def _format_student_context(self, student: model.Student) -> str:
        current_block_id = student.current_block_id

        current_block = (await self.student_repo.get_block_by_id(current_block_id))[0]

        return f"""ПРОФИЛЬ СТУДЕНТА:
- ID студента: {student.id}
- Этап интервью: {student.interview_stage}
- Интервью завершено: {'Да' if student.interview_completed else 'Нет'}
- Опыт программирования: {student.programming_experience or 'Не определен'}
- Известные языки: {student.known_languages or 'Не определен'}
- Опыт работы: {student.work_experience or 'Не указан'}
- Образование: {student.education_background or 'Не указано'}
- Цели обучения: {student.learning_goals or 'Не определен'}
- Карьерные цели: {student.career_goals or 'Не определены'}
- Временные рамки: {student.timeline or 'Не определены'}
- Стиль обучения: {student.learning_style or 'Не определен'}
- Доступность времени: {student.time_availability or 'Не указана'}
- Предпочитаемая сложность: {student.preferred_difficulty or 'Не определена'}
- Оценочный балл: {student.assessment_score if student.assessment_score is not None else 'Не оценен'}
- Сильные области: {student.strong_areas or "Не указан"}
- Слабые области: {student.weak_areas or "Не указан"}
- Рекомендованные темы: {student.recommended_topics or "Не указан"}
- Текущий контент: {current_block.content or "Не указан"}
- Прогресс профиля: {student.get_profile_completion_percentage()}%
- Готов к обучению: {'Да' if student.is_ready_for_learning() else 'Нет'}"""

    async def _get_current_content_context(self, student: model.Student) -> str:
        """Получает контекст текущего изучаемого контента"""
        try:
            context_parts = ["ТЕКУЩИЙ КОНТЕНТ:"]

            # Получаем информацию о текущей теме
            if student.current_topic_id:
                topic = await self.topic_repo.get_topic_by_id(student.current_topic_id)
                if topic:
                    context_parts.append(f"- Тема: {topic.name}")
                    context_parts.append(f"- Описание: {topic.intro}")
                    context_parts.append(f"- План темы: {topic.edu_plan}")
            else:
                context_parts.append("- Тема: Не выбрана")

            # Получаем информацию о текущем блоке
            if student.current_block_id:
                block = await self.topic_repo.get_block_by_id(student.current_block_id)
                if block:
                    context_parts.append(f"- Блок: {block.name}")
                    # Ограничиваем длину контента
                    content_preview = block.content[:500] + "..." if len(block.content) > 500 else block.content
                    context_parts.append(f"- Содержание блока: {content_preview}")
            else:
                context_parts.append("- Блок: Не выбран")

            # Получаем информацию о текущей главе
            if student.current_chapter_id:
                chapter = await self.topic_repo.get_chapter_by_id(student.current_chapter_id)
                if chapter:
                    context_parts.append(f"- Глава: {chapter.name}")
                    # Ограничиваем длину контента
                    content_preview = chapter.content[:500] + "..." if len(chapter.content) > 500 else chapter.content
                    context_parts.append(f"- Содержание главы: {content_preview}")
            else:
                context_parts.append("- Глава: Не выбрана")

            # Добавляем прогресс
            context_parts.append("\nПРОГРЕСС ИЗУЧЕНИЯ:")
            context_parts.append(f"- Завершено тем: {len(student.approved_topics)}")
            context_parts.append(f"- Завершено блоков: {len(student.approved_blocks)}")
            context_parts.append(f"- Завершено глав: {len(student.approved_chapters)}")

            return "\n".join(context_parts)

        except Exception as e:
            self.logger.error(f"Ошибка получения контекста контента: {e}")
            return "ТЕКУЩИЙ КОНТЕНТ: Ошибка загрузки"

    def _get_navigation_rules(self) -> str:
        """Возвращает правила навигации по контенту"""
        return """
ПРАВИЛА НАВИГАЦИИ ПО КОНТЕНТУ:

КОМАНДЫ НАВИГАЦИИ:
1. #nav_to_topic:[ID или название] - переход к теме
2. #nav_to_block:[ID или название] - переход к блоку
3. #nav_to_chapter:[ID или название] - переход к главе
4. #show_topic_list - показать все доступные темы
5. #show_available_blocks:[topic_id] - показать блоки темы
6. #show_available_chapters:[block_id] - показать главы блока
7. #show_progress_summary - показать общий прогресс

КОГДА ИСПОЛЬЗОВАТЬ:
- Студент просит перейти к конкретной теме/блоку/главе
- Студент хочет посмотреть доступный контент
- Студент спрашивает о своем прогрессе
- Студент завершил текущий материал
- Студент хочет вернуться к предыдущему материалу

ВАЖНО:
- При переходе к новой теме сбрасываются текущие блок и глава
- При переходе к новому блоку сбрасывается текущая глава
- Всегда объясняй студенту, куда происходит переход
- Предупреждай о необходимых предпосылках"""

    def _get_expert_switch_rules(self, current_expert: ExpertType) -> str:
        """Возвращает правила переключения между экспертами"""
        rules = {
            ExpertType.INTERVIEW_EXPERT: """
ПЕРЕКЛЮЧЕНИЕ НА ДРУГИХ ЭКСПЕРТОВ:

1. К ПРЕПОДАВАТЕЛЮ (#switch_to_teacher):
   - Интервью завершено и план создан
   - Студент готов начать обучение
   - Студент просит объяснить материал

2. К ТЕСТИРОВАНИЮ (#switch_to_test_expert):
   - Студент хочет проверить текущие знания
   - Необходима оценка для интервью

3. К КАРЬЕРНОМУ КОНСУЛЬТАНТУ (#switch_to_career_consultant):
   - Студент спрашивает о трудоустройстве
   - Вопросы о резюме или собеседовании""",

            ExpertType.TEACHER: """
ПЕРЕКЛЮЧЕНИЕ НА ДРУГИХ ЭКСПЕРТОВ:

1. К ТЕСТИРОВАНИЮ (#switch_to_test_expert):
   - Студент освоил материал и готов к проверке
   - Студент просит тест или контрольную
   - Завершена тема/блок/глава
   - Студент говорит "проверь меня"

2. К КАРЬЕРНОМУ КОНСУЛЬТАНТУ (#switch_to_career_consultant):
   - Вопросы о трудоустройстве
   - Подготовка к собеседованию
   - Работа с резюме

3. К ИНТЕРВЬЮ (#switch_to_interview_expert):
   - Нужно обновить план обучения
   - Изменились цели или обстоятельства
   - Требуется переинтервьюирование

4. К АНАЛИТИКУ (#switch_to_progress_analyst):
   - Студент хочет увидеть свой прогресс
   - Нужен анализ обучения
   - Вопросы о статистике""",

            ExpertType.TEST_EXPERT: """
ПЕРЕКЛЮЧЕНИЕ НА ДРУГИХ ЭКСПЕРТОВ:

1. К ПРЕПОДАВАТЕЛЮ (#switch_to_teacher):
   - Студент не прошел тест
   - Нужно повторить материал
   - Вопросы по теории
   - Студент хочет вернуться к обучению

2. К КАРЬЕРНОМУ КОНСУЛЬТАНТУ (#switch_to_career_consultant):
   - Студент успешно прошел тесты
   - Готов к подготовке к собеседованию
   - Вопросы о трудоустройстве

3. К АНАЛИТИКУ (#switch_to_progress_analyst):
   - Нужен детальный анализ результатов
   - Сравнение с предыдущими тестами
   - Рекомендации по улучшению"""
        }

        base_rules = rules.get(current_expert, "")

        return f"""{base_rules}

ОБЩИЕ ПРИНЦИПЫ ПЕРЕКЛЮЧЕНИЯ:
- Анализируй намерение студента, а не только ключевые слова
- Учитывай контекст всего разговора
- Если студент явно просит другого эксперта - переключай
- Всегда объясняй причину переключения
- Обеспечивай плавный переход между экспертами"""

    def _get_stage_specific_instructions(self, stage: str) -> str:
        """Возвращает инструкции для конкретного этапа интервью"""
        instructions = {
            "WELCOME": """
- Тепло поприветствуй студента
- Представься и объясни свою роль
- Расскажи о процессе интервью (7 этапов)
- Узнай имя студента
- Спроси, что привело к решению изучать программирование
- Создай комфортную и дружелюбную атмосферу
- Используй команду #set_interview_stage:BACKGROUND для перехода далее""",

            "BACKGROUND": """
- Узнай уровень опыта программирования (новичок/средний/продвинутый)
- Выясни, какие языки программирования уже знакомы
- Спроси про образование (техническое/нетехническое)
- Узнай про опыт работы (если есть)
- Используй команды:
  - #update_programming_experience:[уровень]
  - #update_known_languages:[список языков]
  - #update_education_background:[образование]
  - #update_work_experience:[опыт]
- Переходи к GOALS через #set_interview_stage:GOALS""",

            "GOALS": """
- Выясни конкретные цели изучения программирования
- Узнай карьерные планы (какую позицию хочет занимать)
- Определи желаемые сроки достижения целей
- Поймай мотивацию студента
- Используй команды:
  - #update_learning_goals:[список целей]
  - #update_career_goals:[карьерная цель]
  - #update_timeline:[временные рамки]
- Переходи к PREFERENCES через #set_interview_stage:PREFERENCES""",

            "PREFERENCES": """
- Узнай предпочтительный стиль обучения
- Выясни, сколько времени может уделять обучению
- Определи комфортный уровень сложности
- Спроси про интересующие области разработки
- Используй команды:
  - #update_learning_style:[стиль]
  - #update_time_availability:[доступность]
  - #update_preferred_difficulty:[сложность]
- Переходи к ASSESSMENT через #set_interview_stage:ASSESSMENT""",

            "ASSESSMENT": """
- Объясни цель мини-оценки
- Проведи 3-5 вопросов соответствующего уровня
- Оценивай ответы конструктивно
- Определи сильные и слабые стороны
- Используй команды:
  - #conduct_assessment
  - #evaluate_answer:[балл]:[пояснение]
  - #calculate_assessment_score:[итоговый балл]
  - #identify_strong_areas:[список]
  - #identify_weak_areas:[список]
- Переходи к PLAN_GENERATION через #set_interview_stage:PLAN_GENERATION""",

            "PLAN_GENERATION": """
- Проанализируй весь диалог командой #analyze_dialogue
- Создай персональный план командой #generate_learning_plan
- Объясни логику составленного плана
- Покажи, как план поможет достичь целей
- Мотивируй начать обучение
- Используй команды в порядке:
  1. #analyze_dialogue:[chat_history]
  2. #generate_learning_plan:[student_profile]
  3. #set_interview_stage:COMPLETE
- После генерации плана переходи к COMPLETE""",

            "COMPLETE": """
- Поздравь с завершением интервью
- Кратко подведи итоги (профиль, план)
- Объясни следующие шаги
- Передай студента преподавателю
- Используй команды:
  - #complete_interview
  - #switch_to_teacher
- Пожелай успехов в обучении!"""
        }

        return instructions.get(stage, "Следуй общим принципам интервью")

    def _get_learning_style_instructions(self, learning_style: Optional[str]) -> str:
        """Возвращает инструкции для адаптации под стиль обучения"""
        if not learning_style:
            return """СТИЛЬ ОБУЧЕНИЯ НЕ ОПРЕДЕЛЕН:
- Используй разнообразные методы объяснения
- Наблюдай за реакцией студента
- Адаптируйся по ходу обучения
- Предложи пройти переинтервью для уточнения предпочтений"""

        styles = {
            "visual": """ВИЗУАЛЬНЫЙ СТИЛЬ ОБУЧЕНИЯ:
- Используй схемы и диаграммы в описаниях
- Применяй визуальные метафоры и аналогии
- Структурируй информацию с помощью списков
- Выделяй ключевые моменты и термины
- Описывай, как выглядит результат кода
- Используй псевдокод и блок-схемы""",

            "hands-on": """ПРАКТИЧЕСКИЙ СТИЛЬ ОБУЧЕНИЯ:
- Давай больше примеров кода
- Предлагай сразу попробовать написать код
- Фокусируйся на реальных проектах
- Минимум теории - максимум практики
- Поощряй эксперименты и ошибки
- Объясняй через действия, а не концепции""",

            "reading": """СТИЛЬ ОБУЧЕНИЯ ЧЕРЕЗ ЧТЕНИЕ:
- Давай подробные текстовые объяснения
- Рекомендуй дополнительные материалы
- Структурируй информацию логически
- Объясняй теоретические основы
- Давай время на осмысление
- Используй точные определения""",

            "mixed": """СМЕШАННЫЙ СТИЛЬ ОБУЧЕНИЯ:
- Комбинируй различные подходы
- Начинай с теории, переходи к практике
- Используй и визуальные, и текстовые объяснения
- Адаптируйся под конкретную тему
- Предлагай выбор формата изучения
- Следи за вовлеченностью студента"""
        }

        return styles.get(learning_style, styles["mixed"])

    def _get_personalized_recommendations(self, student: model.Student) -> str:
        """Генерирует персональные рекомендации для студента"""
        recommendations = []

        # Рекомендации по уровню
        if student.programming_experience == "beginner":
            recommendations.append("- Не торопись, изучай основы тщательно")
            recommendations.append("- Практикуйся на простых примерах")
        elif student.programming_experience == "intermediate":
            recommendations.append("- Фокусируйся на best practices")
            recommendations.append("- Работай над реальными проектами")
        elif student.programming_experience == "advanced":
            recommendations.append("- Изучай продвинутые концепции")
            recommendations.append("- Помогай другим студентам")

        # Рекомендации по времени
        if student.time_availability and "час" in student.time_availability.lower():
            recommendations.append("- Разбивай материал на небольшие части")
            recommendations.append("- Используй техники микрообучения")

        # Рекомендации по целям
        if student.career_goals and "fullstack" in student.career_goals.lower():
            recommendations.append("- Изучай и frontend, и backend технологии")
            recommendations.append("- Создавай полноценные приложения")

        # Рекомендации по слабым областям
        if student.weak_areas:
            recommendations.append(f"- Удели внимание: {', '.join(student.weak_areas[:2])}")

        return "\n".join(
            recommendations) if recommendations else "- Продолжай в своем темпе\n- Не бойся задавать вопросы"

    def _get_difficulty_guidelines(self, student: model.Student) -> str:
        """Возвращает рекомендации по сложности вопросов"""
        base_level = student.programming_experience or "beginner"
        assessment_score = student.assessment_score or 50

        if base_level == "beginner" or assessment_score < 40:
            return """УРОВЕНЬ НОВИЧОК:
- Вопросы на базовый синтаксис
- Простые определения
- Основные концепции
- Примеры с пошаговым объяснением
- Избегай сложной терминологии"""

        elif base_level == "intermediate" or 40 <= assessment_score < 70:
            return """СРЕДНИЙ УРОВЕНЬ:
- Вопросы на понимание концепций
- Анализ простого кода
- Применение знаний на практике
- Сравнение подходов
- Debugging простых ошибок"""

        else:
            return """ПРОДВИНУТЫЙ УРОВЕНЬ:
- Вопросы на оптимизацию
- Архитектурные решения
- Сложные алгоритмы
- Best practices
- Проектирование систем"""

    def _format_dialogue_for_analysis(self, messages: List[model.EduMessage]) -> str:
        """Форматирует диалог для анализа"""
        formatted_messages = []

        for msg in messages:
            role = "Студент" if msg.role == "user" else "Эксперт"
            # Очищаем сообщения от команд для анализа
            clean_text = re.sub(r'#\w+(?::[^#\s]+)?', '', msg.text).strip()
            if clean_text:  # Добавляем только непустые сообщения
                formatted_messages.append(f"{role}: {clean_text}")

        return "\n".join(formatted_messages)

    def _format_topics_for_planning(self, topics: List[model.Topic]) -> str:
        """Форматирует список тем для планирования"""
        formatted_topics = []

        for topic in topics:
            formatted_topics.append(
                f"ID: {topic.id}\n"
                f"Название: {topic.name}\n"
                f"Описание: {topic.intro}\n"
                f"План изучения: {topic.edu_plan}\n"
            )

        return "\n---\n".join(formatted_topics)