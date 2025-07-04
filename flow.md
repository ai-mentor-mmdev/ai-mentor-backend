# Система команд AI-ментора

## Обзор экспертов и их ролей

1. **Регистратор** — авторизация и онбординг
2. **Эксперт по интервью** — профилирование студента
3. **Преподаватель** — обучение и объяснение материала
4. **Эксперт по тестированию** — проверка знаний
5. **Карьерный консультант** — резюме и подготовка к трудоустройству
6. **Аналитик прогресса** — анализ и рекомендации

## 1. РЕГИСТРАТОР

### Основные функции
- Регистрация новых пользователей
- Авторизация существующих
- Онбординг и знакомство с системой
- Проверка статуса интервью

### Команды регистратора

#### Команды регистрации
```python
#collect_login:[login]                    # Сбор логина
#collect_password:[password]              # Сбор пароля
#validate_credentials                     # Проверка уникальности
#create_account:[account_id]:[login]:[password]  # Создание аккаунта
#hash_password:[password]                 # Хеширование пароля
```

#### Команды авторизации
```python
#check_login:[login]                      # Проверка существования логина
#verify_password:[login]:[password]       # Проверка пароля
#authenticate_user:[account_id]           # Авторизация пользователя
#load_student_profile:[account_id]        # Загрузка профиля
```

#### Команды навигации
```python
#check_interview_status:[student_id]      # Проверка статуса интервью
#switch_to_interview                      # Переход к интервью
#switch_to_learning                       # Переход к обучению (если интервью пройдено)
#show_welcome_message                     # Приветственное сообщение
```

#### Команды ошибок
```python
#error_login_exists                       # Логин уже существует
#error_invalid_credentials               # Неверные данные для входа
#error_weak_password                     # Слабый пароль
```

---

## 2. ЭКСПЕРТ ПО ИНТЕРВЬЮ

### Основные функции
- Проведение первичного интервью
- Переинтервьюирование (обновление профиля)
- Анализ диалога и извлечение данных
- Генерация персонального плана обучения

### Команды эксперта по интервью

#### Команды этапов интервью
```python
#set_interview_stage:[WELCOME|BACKGROUND|GOALS|PREFERENCES|ASSESSMENT|PLAN_GENERATION|COMPLETE]
#check_current_stage                      # Проверка текущего этапа
#move_to_next_stage                       # Переход к следующему этапу
#complete_interview                       # Завершение интервью
```

#### Команды анализа диалога
```python
#analyze_dialogue:[chat_history]          # Анализ диалога
#extract_profile_data:[dialogue_text]     # Извлечение данных профиля
#update_profile:[field]:[value]           # Обновление поля профиля
#validate_profile_completeness            # Проверка полноты профиля
```

#### Команды работы с профилем
```python
#update_programming_experience:[level]    # Обновление опыта программирования
#update_known_languages:[languages_json] # Обновление известных языков
#update_learning_goals:[goals_json]       # Обновление целей обучения
#update_career_goals:[goals]              # Обновление карьерных целей
#update_timeline:[timeline]               # Обновление временных рамок
#update_learning_style:[style]            # Обновление стиля обучения
#update_time_availability:[availability]  # Обновление доступности времени
#update_preferred_difficulty:[difficulty] # Обновление предпочитаемой сложности
```

#### Команды оценки
```python
#conduct_assessment                       # Проведение мини-оценки
#evaluate_answer:[score]:[explanation]    # Оценка ответа
#calculate_assessment_score:[total_score] # Подсчет общего балла
#identify_strong_areas:[areas_json]       # Определение сильных сторон
#identify_weak_areas:[areas_json]         # Определение слабых сторон
```

#### Команды планирования
```python
#generate_learning_plan:[student_profile] # Генерация плана обучения
#select_recommended_topics:[topics_json]  # Выбор рекомендуемых тем
#select_skip_topics:[topics_json]         # Выбор тем для пропуска
#set_focus_areas:[areas_json]             # Установка областей фокуса
#create_learning_path:[path_json]         # Создание пути обучения
#set_current_content:[topic_id]:[block_id]:[chapter_id] # Установка текущего контента
```

#### Команды переинтервьюирования
```python
#start_reinterview                        # Начало переинтервьюирования
#compare_old_new_profile                  # Сравнение старого и нового профиля
#update_learning_plan                     # Обновление плана обучения
#preserve_progress                        # Сохранение текущего прогресса
```

#### Команды завершения
```python
#finalize_profile                         # Финализация профиля
#switch_to_teacher                        # Переход к преподавателю
#send_welcome_to_learning                 # Отправка приветственного сообщения
```

---

## 3. ПРЕПОДАВАТЕЛЬ

### Основные функции
- Обучение и объяснение материала
- Навигация по контенту
- Адаптация под стиль обучения
- Отслеживание прогресса

### Команды преподавателя

#### Команды навигации по контенту
```python
#load_current_content                     # Загрузка текущего контента
#nav_to_topic:[topic_id]                  # Переход к теме
#nav_to_block:[block_id]                  # Переход к блоку
#nav_to_chapter:[chapter_id]              # Переход к главе
#show_topic_list                          # Показать список тем
#show_available_blocks:[topic_id]         # Показать доступные блоки
#show_available_chapters:[block_id]       # Показать доступные главы
```

#### Команды управления прогрессом
```python
#mark_topic_completed:[topic_id]          # Отметить тему как завершенную
#mark_block_completed:[block_id]          # Отметить блок как завершенный
#mark_chapter_completed:[chapter_id]      # Отметить главу как завершенную
#update_current_position:[topic_id]:[block_id]:[chapter_id] # Обновить текущую позицию
#show_progress_summary                    # Показать сводку прогресса
```

#### Команды обучения
```python
#explain_concept:[concept]                # Объяснить концепцию
#give_example:[topic]                     # Дать пример
#provide_analogy:[concept]                # Дать аналогию
#show_practical_application:[topic]       # Показать практическое применение
#adapt_explanation:[learning_style]       # Адаптировать объяснение под стиль
```

#### Команды проверки понимания
```python
#ask_comprehension_question:[topic]       # Задать вопрос на понимание
#evaluate_understanding:[level]           # Оценить уровень понимания
#suggest_review:[topics_to_review]        # Предложить повторение
#recommend_practice:[exercises]           # Рекомендовать практику
```

#### Команды адаптации
```python
#adapt_to_learning_style:[style]          # Адаптация под стиль обучения
#adjust_difficulty:[level]                # Корректировка сложности
#provide_additional_resources:[resources] # Предоставить дополнительные ресурсы
#suggest_study_schedule:[schedule]        # Предложить расписание занятий
```

#### Команды обновления профиля (во время обучения)
```python
#student_knows_topic:[topic_id]           # Студент знает тему
#student_struggling_with:[concept]        # Студент испытывает трудности
#student_interested_in:[area]             # Студент заинтересован в области
#student_time_changed:[new_availability]  # Изменилась доступность времени
#student_goal_changed:[new_goal]          # Изменились цели
#trigger_reinterview                      # Запустить переинтервьюирование
```

#### Команды переключения экспертов
```python
#suggest_testing                          # Предложить тестирование
#switch_to_test_expert                    # Переключиться на эксперта по тестированию
#suggest_career_prep                      # Предложить карьерную подготовку
#switch_to_career_consultant              # Переключиться на карьерного консультанта
```

---

## 4. ЭКСПЕРТ ПО ТЕСТИРОВАНИЮ

### Основные функции
- Создание тестов и вопросов
- Оценка ответов студента
- Анализ результатов
- Рекомендации по улучшению

### Команды эксперта по тестированию

#### Команды создания тестов
```python
#create_test:[topic_id]                   # Создать тест по теме
#create_block_test:[block_id]             # Создать тест по блоку
#create_chapter_test:[chapter_id]         # Создать тест по главе
#generate_questions:[difficulty]:[count]  # Сгенерировать вопросы
#select_question_types:[types_json]       # Выбрать типы вопросов
```

#### Команды проведения тестирования
```python
#start_test:[test_type]                   # Начать тестирование
#present_question:[question_id]           # Представить вопрос
#collect_answer:[answer]                  # Собрать ответ
#evaluate_answer:[correct|incorrect]:[explanation] # Оценить ответ
#move_to_next_question                    # Перейти к следующему вопросу
```

#### Команды анализа результатов
```python
#calculate_test_score:[correct_answers]:[total_questions] # Подсчитать результат
#analyze_performance:[answers_data]       # Проанализировать выполнение
#identify_knowledge_gaps:[weak_topics]    # Выявить пробелы в знаниях
#compare_with_previous_results            # Сравнить с предыдущими результатами
```

#### Команды обратной связи
```python
#provide_detailed_feedback:[feedback]     # Дать детальную обратную связь
#explain_correct_answer:[question_id]     # Объяснить правильный ответ
#suggest_study_materials:[topics]         # Предложить материалы для изучения
#recommend_review_topics:[topics_json]    # Рекомендовать темы для повторения
```

#### Команды обновления профиля
```python
#update_assessment_score:[score]          # Обновить оценочный балл
#update_strong_areas:[areas_json]         # Обновить сильные области
#update_weak_areas:[areas_json]           # Обновить слабые области
#track_progress:[progress_data]           # Отследить прогресс
```

#### Команды типов тестов
```python
#multiple_choice_test                     # Тест с множественным выбором
#open_question_test                       # Тест с открытыми вопросами
#practical_task_test                      # Практическое задание
#code_review_test                         # Тест на проверку кода
#situational_test                         # Ситуационный тест
```

#### Команды завершения тестирования
```python
#complete_test                           # Завершить тестирование
#generate_test_report:[results]          # Сгенерировать отчет по тесту
#switch_to_teacher                       # Вернуться к преподавателю
#suggest_next_steps:[recommendations]    # Предложить следующие шаги
```

---

## 5. КАРЬЕРНЫЙ КОНСУЛЬТАНТ

### Основные функции
- Создание и оптимизация резюме
- Подготовка к собеседованиям
- Карьерные советы и планирование
- Анализ рынка труда

### Команды карьерного консультанта

#### Команды создания резюме
```python
#start_resume_creation                    # Начать создание резюме
#collect_personal_info                    # Собрать личную информацию
#extract_skills_from_profile             # Извлечь навыки из профиля обучения
#generate_experience_section             # Сгенерировать раздел опыта
#create_projects_section                 # Создать раздел проектов
#optimize_resume_keywords:[job_description] # Оптимизировать ключевые слова
```

#### Команды анализа резюме
```python
#analyze_resume_strength                  # Проанализировать сильные стороны резюме
#identify_resume_gaps                     # Выявить пробелы в резюме
#suggest_resume_improvements              # Предложить улучшения
#check_resume_formatting                  # Проверить форматирование
#validate_resume_content                  # Валидировать содержание
```

#### Команды подготовки к собеседованию
```python
#start_interview_prep:[position]          # Начать подготовку к собеседованию
#generate_common_questions:[role]         # Сгенерировать частые вопросы
#conduct_mock_interview                   # Провести mock-интервью
#evaluate_interview_answer:[answer]       # Оценить ответ на собеседовании
#provide_answer_feedback:[feedback]       # Дать обратную связь по ответу
```

#### Команды карьерного планирования
```python
#analyze_career_readiness                 # Проанализировать готовность к карьере
#suggest_career_paths:[profile]           # Предложить карьерные пути
#identify_skill_gaps:[target_position]    # Выявить недостающие навыки
#create_learning_roadmap:[career_goal]    # Создать дорожную карту обучения
#suggest_certifications:[field]           # Предложить сертификации
```

#### Команды поиска работы
```python
#analyze_job_market:[location]:[field]    # Проанализировать рынок труда
#suggest_job_platforms                    # Предложить платформы поиска работы
#optimize_linkedin_profile               # Оптимизировать LinkedIn профиль
#create_cover_letter:[job_description]   # Создать сопроводительное письмо
#suggest_networking_strategies           # Предложить стратегии нетворкинга
```

#### Команды переговоров
```python
#prepare_salary_negotiation              # Подготовить переговоры о зарплате
#analyze_job_offer:[offer_details]       # Проанализировать предложение о работе
#suggest_negotiation_points              # Предложить пункты для переговоров
#create_counter_offer:[terms]            # Создать встречное предложение
```

#### Команды экспорта
```python
#export_resume_pdf                       # Экспортировать резюме в PDF
#export_linkedin_summary                 # Экспортировать резюме для LinkedIn
#generate_portfolio_description          # Сгенерировать описание портфолио
#create_skills_matrix                    # Создать матрицу навыков
```

#### Команды обновления профиля
```python
#update_career_goals:[new_goals]         # Обновить карьерные цели
#update_target_positions:[positions]     # Обновить целевые позиции
#update_salary_expectations:[range]      # Обновить ожидания по зарплате
#update_location_preferences:[locations] # Обновить предпочтения по локации
```

---

## 6. АНАЛИТИК ПРОГРЕССА

### Основные функции
- Анализ прогресса обучения
- Генерация отчетов и статистики
- Персональные рекомендации
- Планирование следующих шагов

### Команды аналитика прогресса

#### Команды анализа прогресса
```python
#analyze_learning_progress:[student_id]   # Проанализировать прогресс обучения
#calculate_completion_rate               # Подсчитать процент завершения
#analyze_time_spent:[period]             # Проанализировать потраченное время
#track_skill_development                 # Отследить развитие навыков
#measure_learning_velocity               # Измерить скорость обучения
```

#### Команды генерации отчетов
```python
#generate_progress_report:[period]       # Сгенерировать отчет о прогрессе
#create_skills_assessment_report         # Создать отчет по оценке навыков
#generate_time_analysis_report           # Сгенерировать отчет по времени
#create_achievement_summary              # Создать сводку достижений
#export_learning_analytics               # Экспортировать аналитику обучения
```

#### Команды сравнительного анализа
```python
#compare_with_average:[metric]           # Сравнить со средними показателями
#benchmark_against_goals                 # Сравнить с поставленными целями
#analyze_improvement_trends              # Проанализировать тенденции улучшения
#compare_learning_paths                  # Сравнить пути обучения
```

#### Команды рекомендаций
```python
#suggest_next_topics:[current_progress]  # Предложить следующие темы
#recommend_study_schedule                # Рекомендовать расписание занятий
#suggest_difficulty_adjustment           # Предложить корректировку сложности
#recommend_additional_resources          # Рекомендовать дополнительные ресурсы
#suggest_career_preparation_timing       # Предложить время для карьерной подготовки
```

#### Команды выявления проблем
```python
#identify_learning_obstacles             # Выявить препятствия в обучении
#detect_knowledge_gaps                   # Обнаружить пробелы в знаниях
#analyze_stalled_progress                # Проанализировать застой в прогрессе
#identify_motivation_issues              # Выявить проблемы с мотивацией
```

#### Команды мотивации и достижений
```python
#track_achievements:[achievements]       # Отследить достижения
#celebrate_milestones                    # Отпраздновать важные этапы
#motivate_continued_learning             # Мотивировать продолжить обучение
#suggest_goals_adjustment                # Предложить корректировку целей
```

#### Команды прогнозирования
```python
#predict_completion_time:[current_pace]  # Спрогнозировать время завершения
#forecast_career_readiness               # Спрогнозировать готовность к карьере
#estimate_skill_mastery_time             # Оценить время освоения навыков
#predict_success_probability             # Спрогнозировать вероятность успеха
```

---

## ГЛОБАЛЬНЫЕ КОМАНДЫ (доступны всем экспертам)

### Команды переключения экспертов
```python
#switch_to_registrar                     # Переключиться на регистратора
#switch_to_interview_expert              # Переключиться на эксперта по интервью
#switch_to_teacher                       # Переключиться на преподавателя  
#switch_to_test_expert                   # Переключиться на эксперта по тестированию
#switch_to_career_consultant             # Переключиться на карьерного консультанта
#switch_to_progress_analyst              # Переключиться на аналитика прогресса
```

### Команды управления сессией
```python
#save_session_state                      # Сохранить состояние сессии
#load_session_state:[session_id]         # Загрузить состояние сессии
#reset_conversation_context              # Сбросить контекст беседы
#end_session                             # Завершить сессию
```

### Команды помощи и поддержки
```python
#get_help:[topic]                        # Получить помощь
#show_available_commands                 # Показать доступные команды
#explain_system_features                 # Объяснить возможности системы
#provide_technical_support               # Предоставить техническую поддержку
```

### Команды работы с профилем
```python
#show_full_profile                       # Показать полный профиль
#export_profile_data                     # Экспортировать данные профиля
#backup_profile                          # Создать резервную копию профиля
#restore_profile:[backup_id]             # Восстановить профиль из резервной копии
```

### Команды ошибок и восстановления
```python
#handle_error:[error_type]:[error_message] # Обработать ошибку
#request_clarification:[unclear_input]   # Запросить уточнение
#suggest_alternative_action              # Предложить альтернативное действие
#escalate_to_support                     # Эскалировать в техподдержку
```

---

## СХЕМА ФЛОУ И КОМАНД

```
РЕГИСТРАЦИЯ (#collect_login, #create_account)
    ↓
ИНТЕРВЬЮ (#set_interview_stage, #analyze_dialogue, #generate_learning_plan)
    ↓
ОБУЧЕНИЕ (#nav_to_topic, #explain_concept, #mark_completed)
    ↕
ТЕСТИРОВАНИЕ (#create_test, #evaluate_answer, #analyze_performance)
    ↕
КАРЬЕРА (#create_resume, #mock_interview, #analyze_job_market)
    ↕
АНАЛИЗ ПРОГРЕССА (#analyze_learning_progress, #suggest_next_topics)
    ↕
ПЕРЕИНТЕРВЬЮИРОВАНИЕ (#start_reinterview, #update_learning_plan)
```

Эта система команд покрывает весь жизненный цикл студента в AI-менторе от регистрации до трудоустройства с возможностью корректировки на любом этапе.