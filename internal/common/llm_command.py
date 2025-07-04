from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

class CommandType(Enum):
    """Типы команд в системе"""
    # Переключение экспертов
    SWITCH_EXPERT = "switch_expert"

    # Навигация по контенту
    NAVIGATION = "navigation"

    # Обновление профиля
    PROFILE_UPDATE = "profile_update"

    # Управление интервью
    INTERVIEW_CONTROL = "interview_control"

    # Тестирование
    TEST_CONTROL = "test_control"

    # Карьера
    CAREER_CONTROL = "career_control"

    # Аналитика
    ANALYTICS_CONTROL = "analytics_control"

    # Системные
    SYSTEM = "system"

class ExpertType(Enum):
    """Типы экспертов в системе"""
    REGISTRATOR = "registrator"
    INTERVIEW_EXPERT = "interview_expert"
    TEACHER = "teacher"
    TEST_EXPERT = "test_expert"
    CAREER_CONSULTANT = "career_consultant"
    PROGRESS_ANALYST = "progress_analyst"

class InterviewStage(Enum):
    """Этапы интервью"""
    WELCOME = "WELCOME"
    BACKGROUND = "BACKGROUND"
    GOALS = "GOALS"
    PREFERENCES = "PREFERENCES"
    ASSESSMENT = "ASSESSMENT"
    PLAN_GENERATION = "PLAN_GENERATION"
    COMPLETE = "COMPLETE"


@dataclass
class Command:
    """Базовая модель команды"""
    name: str
    type: CommandType
    params: list[str] = field(default_factory=list)
    raw: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_string(self) -> str:
        """Преобразует команду в строку для выполнения"""
        if self.params:
            return f"#{self.name}:{':'.join(self.params)}"
        return f"#{self.name}"

@dataclass
class CommandResult:
    """Результат выполнения команды"""
    command_name: str
    success: bool
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ExpertResponse:
    """Ответ эксперта"""
    expert: ExpertType
    message: str = ""
    commands_executed: List[Command] = field(default_factory=list)
    command_results: List[CommandResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DialogueAnalysis:
    """Результат анализа диалога"""
    profile_updates: Dict[str, Any]
    confidence_score: int
    ready_for_next_stage: bool
    extracted_info: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class LearningPlan:
    """Персональный план обучения"""
    skip_topics: Dict[int, str]  # topic_id: reason
    recommended_topics: Dict[int, str]  # topic_id: importance
    focus_areas: List[str]
    learning_path: List[Dict[str, Any]]
    welcome_message: str
    total_estimated_time: str
    adaptation_notes: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TestSession:
    """Сессия тестирования"""
    id: int
    student_id: int
    test_type: str
    questions: List[Dict[str, Any]]
    current_question_index: int = 0
    answers: List[Dict[str, Any]] = field(default_factory=list)
    score: Optional[int] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    @property
    def progress_percentage(self) -> int:
        if not self.questions:
            return 0
        return int((self.current_question_index / len(self.questions)) * 100)

@dataclass
class CareerDocument:
    """Документ для карьеры (резюме, сопроводительное письмо и т.д.)"""
    type: str  # resume, cover_letter, linkedin_summary
    content: Dict[str, Any]
    format: str  # pdf, markdown, plain_text
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class ProgressReport:
    """Отчет о прогрессе"""
    student_id: int
    period: str  # daily, weekly, monthly
    metrics: Dict[str, Any]
    achievements: List[str]
    recommendations: List[str]
    visualizations: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)