from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Student:
    id: int
    account_id: int

    current_expert: str = None

    # Состояние интервью
    # WELCOME, BACKGROUND, GOALS, PREFERENCES, ASSESSMENT, PLAN_GENERATION, COMPLETE
    interview_stage: str = "WELCOME"
    interview_completed: bool = False

    # Бэкграунд
    # "beginner", "intermediate", "advanced"
    programming_experience: str = None
    known_languages: list[str] = field(default_factory=list)
    work_experience: str = None
    education_background: str = None

    # Цели
    learning_goals: list[str] = field(default_factory=list)
    career_goals: str = None
    # "1 month", "3 months", "6 months", etc.
    timeline: str = None

    # Предпочтения
    # "visual", "hands-on", "reading", "mixed"
    learning_style: str = None
    # "1-2 hours/day", "weekends only", etc.
    time_availability: str = None
    # "gradual", "challenging", "mixed"
    preferred_difficulty: str = None

    # Адаптация контента
    # {id: name} темы, которые можно пропустить
    skip_topics: dict[int, str] = field(default_factory=dict)
    # {id: name} блоки, которые можно пропустить
    skip_blocks: dict[int, str] = field(default_factory=dict)
    focus_areas: list[str] = field(default_factory=list)  # Области для углубленного изучения

    # {id: name} тем в порядке изучения
    recommended_topics: dict[int, str] = field(default_factory=dict)
    # {id: name} блоков в порядке изучения
    recommended_blocks: dict[int, str] = field(default_factory=dict)

    # {id: name} тем, которые уже изучены
    approved_topics: dict[int, str] = field(default_factory=dict)
    # {id: name} блоков, которые уже изучены
    approved_blocks: dict[int, str] = field(default_factory=dict)
    # {id: name} глав, которые уже изучены
    approved_chapters: dict[int, str] = field(default_factory=dict)

    # Оценка уровня
    # 0-100
    assessment_score: int = None
    strong_areas: list[str] = field(default_factory=list)
    weak_areas: list[str] = field(default_factory=list)

    # Персональный план обучения
    # Детальный план обучения
    learning_path: list[dict] = field(default_factory=list)
    current_topic_id: int = None
    current_block_id: int = None
    current_chapter_id: int = None

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def update_from_dict(self, updates: dict) -> None:
        for field_name, value in updates.items():
            if value is not None and hasattr(self, field_name):
                setattr(self, field_name, value)
        self.updated_at = datetime.now()

    def is_ready_for_learning(self) -> bool:
        return (
                self.interview_completed and
                self.programming_experience is not None and
                len(self.learning_goals) > 0 and
                len(self.recommended_topics) > 0
        )

    def get_profile_completion_percentage(self) -> int:
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
    def serialize(cls, rows) -> list['Student']:
        """Сериализация из результатов БД"""
        return [
            cls(
                id=row.id,
                account_id=row.account_id,
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