from abc import abstractmethod
from typing import Protocol

from internal import model


class ITopicRepo(Protocol):
    @abstractmethod
    async def update_current_topic(self, student_id: int, topic_id: int, topic_name: str): pass

    @abstractmethod
    async def update_current_block(self, student_id: int, block_id: int, block_name: str): pass

    @abstractmethod
    async def update_current_chapter(self, student_id: int, chapter_id: int, chapter_name: str): pass

    @abstractmethod
    async def get_topic_by_id(self, topic_id: int) -> list[model.Topic]: pass

    @abstractmethod
    async def get_block_by_id(self, block_id: int) -> list[model.Block]: pass

    @abstractmethod
    async def get_chapter_by_id(self, chapter_id: int) -> list[model.Chapter]: pass

    @abstractmethod
    async def get_all_topic(self) -> list[model.Topic]: pass

    @abstractmethod
    async def get_all_block(self) -> list[model.Block]: pass

    @abstractmethod
    async def get_all_chapter(self) -> list[model.Chapter]: pass
