from typing import Protocol
from abc import abstractmethod
from internal import model


class ITopicRepo(Protocol):
    @abstractmethod
    async def get_all_topic(self) -> list[model.Topic]: pass

    @abstractmethod
    async def get_all_block(self) -> list[model.Block]: pass

    @abstractmethod
    async def get_all_chapter(self) -> list[model.Chapter]: pass

    @abstractmethod
    async def get_block_by_id(self, block_id: int) -> list[model.Block]: pass

    @abstractmethod
    async def get_chapter_by_id(self, chapter_id: int) -> list[model.Chapter]: pass