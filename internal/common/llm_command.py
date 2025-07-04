class EduPersonalizationCommand:
    """Команды для персонализации обучения"""
    # Создание профиля студента
    create_student_profile = "EDU_CREATE_STUDENT_PROFILE"
    update_student_profile = "EDU_UPDATE_STUDENT_PROFILE"

    # Генерация плана обучения
    generate_personal_plan = "EDU_GENERATE_PERSONAL_PLAN"
    update_learning_path = "EDU_UPDATE_LEARNING_PATH"

    # Управление целями
    set_learning_goals = "EDU_SET_LEARNING_GOALS"
    update_goals_progress = "EDU_UPDATE_GOALS_PROGRESS"

    # Оценка уровня
    assess_current_level = "EDU_ASSESS_CURRENT_LEVEL"
    save_assessment_results = "EDU_SAVE_ASSESSMENT_RESULTS"

class EduContentCommand:
    """Команды для управления контентом"""
    recommend_topics = "EDU_RECOMMEND_TOPICS"
    prioritize_content = "EDU_PRIORITIZE_CONTENT"
    adjust_difficulty = "EDU_ADJUST_DIFFICULTY"
    create_custom_learning_path = "EDU_CREATE_CUSTOM_LEARNING_PATH"

class EduInterviewStage:
    """Этапы интервью"""
    welcome = "INTERVIEW_STAGE_WELCOME"
    background_assessment = "INTERVIEW_STAGE_BACKGROUND"
    goals_clarification = "INTERVIEW_STAGE_GOALS"
    preferences_discovery = "INTERVIEW_STAGE_PREFERENCES"
    plan_generation = "INTERVIEW_STAGE_PLAN_GENERATION"
    plan_presentation = "INTERVIEW_STAGE_PLAN_PRESENTATION"
    handoff_to_teacher = "INTERVIEW_STAGE_HANDOFF"