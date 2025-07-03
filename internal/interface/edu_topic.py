from abc import abstractmethod
from typing import Protocol, Optional, List
from internal import model


class ITopicRepo(Protocol):
    @abstractmethod
    async def create_topic(self, name: str, intro: str, edu_plan: str) -> int:
        pass

    @abstractmethod
    async def get_topic_by_id(self, topic_id: int) -> Optional[model.Topic]:
        pass

    @abstractmethod
    async def get_all_topics(self) -> List[model.Topic]:
        pass

    @abstractmethod
    async def update_topic(self, topic_id: int, name: str = None, intro: str = None, edu_plan: str = None) -> None:
        pass

    @abstractmethod
    async def delete_topic(self, topic_id: int) -> None:
        pass

    # Операции с блоками (Blocks)
    @abstractmethod
    async def create_block(self, topic_id: int, name: str, content: str) -> int:
        pass

    @abstractmethod
    async def get_block_by_id(self, block_id: int) -> Optional[model.Block]:
        pass

    @abstractmethod
    async def get_blocks_by_topic_id(self, topic_id: int) -> List[model.Block]:
        pass

    @abstractmethod
    async def update_block(self, block_id: int, name: str = None, content: str = None) -> None:
        pass

    @abstractmethod
    async def delete_block(self, block_id: int) -> None:
        pass

    # Операции с главами (Chapters)
    @abstractmethod
    async def create_chapter(self, topic_id: int, block_id: int, name: str, content: str) -> int:
        pass

    @abstractmethod
    async def get_chapter_by_id(self, chapter_id: int) -> Optional[model.Chapter]:
        pass

    @abstractmethod
    async def get_chapters_by_block_id(self, block_id: int) -> List[model.Chapter]:
        pass

    @abstractmethod
    async def get_chapters_by_topic_id(self, topic_id: int) -> List[model.Chapter]:
        pass

    @abstractmethod
    async def update_chapter(self, chapter_id: int, name: str = None, content: str = None) -> None:
        pass

    @abstractmethod
    async def delete_chapter(self, chapter_id: int) -> None:
        pass
