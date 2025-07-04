from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Student:
    id: int
    account_id: int

    login: str
    password: str

    # Бэкграунд
    programming_experience: str  # "beginner", "intermediate", "advanced"
    known_languages: list[str]
    work_experience: str
    education_background: str

    # Цели
    learning_goals: list[str]
    career_goals: str
    timeline: str  # "1 month", "3 months", "6 months", etc.

    # Предпочтения
    learning_style: str  # "visual", "hands-on", "reading", "mixed"
    time_availability: str  # "1-2 hours/day", "weekends only", etc.
    preferred_difficulty: str  # "gradual", "challenging", "mixed"

    # Адаптация контента
    skip_topics: dict[int, str]  # {id: name} темы, которые можно пропустить
    skip_blocks: dict[int, str]  # {id: name} блоки, которые можно пропустить
    focus_areas: list[str]  # Области для углубленного изучения

    recommended_topics: dict[int, str]  # {id: name} тем в порядке изучения
    recommended_blocks: dict[int, str]  # {id: name} блоков в порядке изучения

    approved_topics: dict[int, str]  # {id: name} тем, которые уже изучены
    approved_blocks: dict[int, str]  # {id: name} блоков, которые уже изучены
    approved_courses: dict[int, str]  # {id: name} курсов, которые уже изучены

    # Оценка уровня
    assessment_score: int  # 0-100
    strong_areas: list[str]
    weak_areas: list[str]

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)