from dataclasses import dataclass
from datetime import datetime


@dataclass
class Student:
    id: int
    login: str
    password: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                login=row.login,
                password=row.password,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


@dataclass
class EduProgress:
    id: int
    account_id: int
    approved_topic_ids: list[int]
    approved_block_ids: list[int]
    approved_chapter_ids: list[int]
    current_topic_id: int
    current_block_id: int
    current_chapter_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                account_id=row.account_id,
                approved_topic_ids=row.approved_topic_ids or [],
                approved_block_ids=row.approved_block_ids or [],
                approved_chapter_ids=row.approved_chapter_ids or [],
                current_topic_id=row.current_topic_id,
                current_block_id=row.current_block_id,
                current_chapter_id=row.current_chapter_id,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


@dataclass
class Topic:
    id: int
    name: str
    intro: str
    edu_plan: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                name=row.name,
                intro=row.intro,
                edu_plan=row.edu_plan,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


@dataclass
class Block:
    id: int
    topic_id: int
    name: str
    content: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                topic_id=row.topic_id,
                name=row.name,
                content=row.content,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


@dataclass
class Chapter:
    id: int
    topic_id: int
    block_id: int
    name: str
    content: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                topic_id=row.topic_id,
                block_id=row.block_id,
                name=row.name,
                content=row.content,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]


@dataclass
class EduChat:
    id: int
    account_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                account_id=row.account_id,
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
    created_at: datetime
    updated_at: datetime

    @classmethod
    def serialize(cls, rows) -> list:
        return [
            cls(
                id=row.id,
                edu_chat_id=row.edu_chat_id,
                text=row.text,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]
