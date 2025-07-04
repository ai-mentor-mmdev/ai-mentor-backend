from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class EduChat:
    id: int

    student_id: int

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                student_id=row.student_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


@dataclass
class EduMessage:
    id: int
    edu_chat_id: int
    text: str
    role: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                edu_chat_id=row.edu_chat_id,
                text=row.text,
                role=row.role,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]