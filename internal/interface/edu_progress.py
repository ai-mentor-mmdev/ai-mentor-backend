from abc import abstractmethod
from typing import Protocol

from internal import model


class IEduProgressRepo(Protocol):
    @abstractmethod
    async def get_progress_by_account_id(self, account_id: int) -> list[model.EduProgress]:
        pass

    @abstractmethod
    async def get_progress_by_chat_id(self, edu_chat_id: int) -> list[model.EduProgress]:
        pass

    @abstractmethod
    async def get_current_topic_id(self, account_id: int) -> int:
        pass

    @abstractmethod
    async def get_current_block_id(self, account_id: int) -> int:
        pass

    @abstractmethod
    async def get_current_chapter_id(self, account_id: int) -> int:
        pass

    @abstractmethod
    async def get_approved_topic_ids(self, progress_id: int) -> list[int]:
        pass

    @abstractmethod
    async def get_approved_block_ids(self, progress_id: int) -> list[int]:
        pass

    @abstractmethod
    async def get_approved_chapter_ids(self, progress_id: int) -> list[int]:
        pass

    @abstractmethod
    async def update_current_topic_id(self, progress_id: int, topic_id: int):
        pass

    @abstractmethod
    async def update_current_block_id(self, progress_id: int, block_id: int):
        pass

    @abstractmethod
    async def update_current_chapter_id(self, progress_id: int, chapter_id: int):
        pass

    @abstractmethod
    async def mark_topic_completed(self, progress_id: int, topic_id: int):
        pass

    @abstractmethod
    async def mark_block_completed(self, account_id: int, block_id: int):
        pass

    @abstractmethod
    async def mark_chapter_completed(self, account_id: int, chapter_id: int):
        pass


