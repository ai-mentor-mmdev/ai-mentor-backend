from dataclasses import dataclass
from datetime import datetime


@dataclass
class Student:
    id: int

    login: str
    password: str

    created_at: datetime
    updated_at: datetime


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


@dataclass
class Topic:
    id: int

    name: str
    intro: str
    edu_plan: str

    created_at: datetime
    updated_at: datetime


@dataclass
class Block:
    id: int
    topic_id: int

    name: str
    content: str

    created_at: datetime
    updated_at: datetime


@dataclass
class Chapter:
    id: int
    topic_id: int
    block_id: int

    name: str
    content: str

    created_at: datetime
    updated_at: datetime


@dataclass
class EduChat:
    id: int
    account_id: int

    created_at: datetime
    updated_at: datetime

@dataclass
class EduMessage:
    id: int
    edu_chat_id: int

    text: str
    created_at: datetime
    updated_at: datetime

