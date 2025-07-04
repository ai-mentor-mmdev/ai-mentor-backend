from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional


@dataclass
class Student:
    id: int
    account_id: int

    login: str
    password: str

    # Состояние интервью
    interview_stage: str = "WELCOME"  # WELCOME, BACKGROUND, GOALS, PREFERENCES, ASSESSMENT, PLAN_GENERATION, COMPLETE
    interview_completed: bool = False

    # Бэкграунд
    programming_experience: Optional[str] = None  # "beginner", "intermediate", "advanced"
    known_languages: List[str] = field(default_factory=list)
    work_experience: Optional[str] = None
    education_background: Optional[str] = None

    # Цели
    learning_goals: List[str] = field(default_factory=list)
    career_goals: Optional[str] = None
    timeline: Optional[str] = None  # "1 month", "3 months", "6 months", etc.

    # Предпочтения
    learning_style: Optional[str] = None  # "visual", "hands-on", "reading", "mixed"
    time_availability: Optional[str] = None  # "1-2 hours/day", "weekends only", etc.
    preferred_difficulty: Optional[str] = None  # "gradual", "challenging", "mixed"

    # Адаптация контента
    skip_topics: Dict[int, str] = field(default_factory=dict)  # {id: name} темы, которые можно пропустить
    skip_blocks: Dict[int, str] = field(default_factory=dict)  # {id: name} блоки, которые можно пропустить
    focus_areas: List[str] = field(default_factory=list)  # Области для углубленного изучения

    recommended_topics: Dict[int, str] = field(default_factory=dict)  # {id: name} тем в порядке изучения
    recommended_blocks: Dict[int, str] = field(default_factory=dict)  # {id: name} блоков в порядке изучения

    approved_topics: Dict[int, str] = field(default_factory=dict)  # {id: name} тем, которые уже изучены
    approved_blocks: Dict[int, str] = field(default_factory=dict)  # {id: name} блоков, которые уже изучены
    approved_chapters: Dict[int, str] = field(default_factory=dict)  # {id: name} глав, которые уже изучены

    # Оценка уровня
    assessment_score: Optional[int] = None  # 0-100
    strong_areas: List[str] = field(default_factory=list)
    weak_areas: List[str] = field(default_factory=list)

    # Персональный план обучения
    learning_path: List[Dict] = field(default_factory=list)  # Детальный план обучения
    current_topic_id: Optional[int] = None
    current_block_id: Optional[int] = None
    current_chapter_id: Optional[int] = None

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def create_new(cls, account_id: int, login: str, password: str) -> 'Student':
        """Создает нового студента с базовыми настройками"""
        return cls(
            id=0,  # Будет установлен при сохранении в БД
            account_id=account_id,
            login=login,
            password=password,
            interview_stage="WELCOME",
            interview_completed=False
        )

    def update_from_dict(self, updates: dict) -> None:
        """Обновляет поля студента из словаря"""
        for field_name, value in updates.items():
            if value is not None and hasattr(self, field_name):
                setattr(self, field_name, value)
        self.updated_at = datetime.now()

    def is_ready_for_learning(self) -> bool:
        """Проверяет, готов ли студент к обучению"""
        return (
                self.interview_completed and
                self.programming_experience is not None and
                len(self.learning_goals) > 0 and
                len(self.recommended_topics) > 0
        )

    def get_profile_completion_percentage(self) -> int:
        """Возвращает процент заполненности профиля"""
        total_fields = 12
        filled_fields = 0

        fields_to_check = [
            self.programming_experience,
            self.work_experience,
            self.education_background,
            self.career_goals,
            self.timeline,
            self.learning_style,
            self.time_availability,
            self.preferred_difficulty
        ]

        filled_fields += sum(1 for field in fields_to_check if field is not None)
        filled_fields += 1 if len(self.known_languages) > 0 else 0
        filled_fields += 1 if len(self.learning_goals) > 0 else 0
        filled_fields += 1 if self.assessment_score is not None else 0
        filled_fields += 1 if len(self.recommended_topics) > 0 else 0

        return int((filled_fields / total_fields) * 100)

    @classmethod
    def serialize(cls, rows) -> List['Student']:
        """Сериализация из результатов БД"""
        return [
            cls(
                id=row.id,
                account_id=row.account_id,
                login=row.login,
                password=row.password,
                interview_stage=row.interview_stage,
                interview_completed=row.interview_completed,
                programming_experience=row.programming_experience,
                known_languages=row.known_languages or [],
                work_experience=row.work_experience,
                education_background=row.education_background,
                learning_goals=row.learning_goals or [],
                career_goals=row.career_goals,
                timeline=row.timeline,
                learning_style=row.learning_style,
                time_availability=row.time_availability,
                preferred_difficulty=row.preferred_difficulty,
                skip_topics=row.skip_topics or {},
                skip_blocks=row.skip_blocks or {},
                focus_areas=row.focus_areas or [],
                recommended_topics=row.recommended_topics or {},
                recommended_blocks=row.recommended_blocks or {},
                approved_topics=row.approved_topics or {},
                approved_blocks=row.approved_blocks or {},
                approved_chapters=row.approved_chapters or {},
                assessment_score=row.assessment_score,
                strong_areas=row.strong_areas or [],
                weak_areas=row.weak_areas or [],
                learning_path=row.learning_path or [],
                current_topic_id=row.current_topic_id,
                current_block_id=row.current_block_id,
                current_chapter_id=row.current_chapter_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]