class EduNavigationCommand:
    """Команды навигации по образовательному контенту"""
    to_topic = "EDU_NAVIGATE_TO_TOPIC"
    to_block = "EDU_NAVIGATE_TO_BLOCK"
    to_chapter = "EDU_NAVIGATE_TO_CHAPTER"
    show_topics = "EDU_SHOW_TOPICS"
    show_blocks = "EDU_SHOW_BLOCKS"
    show_chapters = "EDU_SHOW_CHAPTERS"
    show_progress = "EDU_SHOW_PROGRESS"


class EduStateSwitchCommand:
    """Команды переключения между экспертами"""
    to_teacher = "EDU_SWITCH_TO_TEACHER"
    to_test_expert = "EDU_SWITCH_TO_TEST_EXPERT"
    to_interview_expert = "EDU_SWITCH_TO_INTERVIEW_EXPERT"


class EduProgressAction:
    """Действия для обновления прогресса студента"""
    complete_topic = "EDU_COMPLETE_TOPIC"
    complete_block = "EDU_COMPLETE_BLOCK"
    complete_chapter = "EDU_COMPLETE_CHAPTER"
    start_topic = "EDU_START_TOPIC"
    start_block = "EDU_START_BLOCK"
    start_chapter = "EDU_START_CHAPTER"

class Roles:
    """Роли в системе чата"""
    user = "user"
    assistant = "assistant"
    system = "system"
