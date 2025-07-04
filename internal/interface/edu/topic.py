from typing import Protocol, List, Optional
from abc import abstractmethod
from internal import model


class ITopicRepo(Protocol):
    @abstractmethod
    async def get_all_topics(self) -> List[model.Topic]:
        """Получает все доступные темы"""
        pass

    @abstractmethod
    async def get_topic_by_id(self, topic_id: int) -> Optional[model.Topic]:
        """Получает тему по ID"""
        pass

    @abstractmethod
    async def get_topics_by_ids(self, topic_ids: List[int]) -> List[model.Topic]:
        """Получает темы по списку ID"""
        pass

    @abstractmethod
    async def get_blocks_by_topic_id(self, topic_id: int) -> List[model.Block]:
        """Получает все блоки темы"""
        pass

    @abstractmethod
    async def get_block_by_id(self, block_id: int) -> Optional[model.Block]:
        """Получает блок по ID"""
        pass

    @abstractmethod
    async def get_chapters_by_block_id(self, block_id: int) -> List[model.Chapter]:
        """Получает все главы блока"""
        pass

    @abstractmethod
    async def get_chapter_by_id(self, chapter_id: int) -> Optional[model.Chapter]:
        """Получает главу по ID"""
        pass

    @abstractmethod
    async def create_topic(self, topic: model.Topic) -> int:
        """Создает новую тему"""
        pass

    @abstractmethod
    async def create_block(self, block: model.Block) -> int:
        """Создает новый блок"""
        pass

    @abstractmethod
    async def create_chapter(self, chapter: model.Chapter) -> int:
        """Создает новую главу"""
        pass

    @abstractmethod
    async def search_topics_by_name(self, name_pattern: str) -> List[model.Topic]:
        """Ищет темы по названию"""
        pass

    @abstractmethod
    async def get_topic_prerequisites(self, topic_id: int) -> List[int]:
        """Получает список ID тем-предпосылок"""
        pass