from abc import abstractmethod
from typing import Protocol, Optional, List
from internal import model


class ITopicRepo(Protocol):
    """Интерфейс для работы с темами, блоками и главами"""

    # Операции с темами (Topics)
    @abstractmethod
    async def create_topic(self, name: str, intro: str, edu_plan: str) -> int:
        """Создает новую тему"""
        pass

    @abstractmethod
    async def get_topic_by_id(self, topic_id: int) -> Optional[model.Topic]:
        """Получает тему по ID"""
        pass

    @abstractmethod
    async def get_all_topics(self) -> List[model.Topic]:
        """Получает все темы"""
        pass

    @abstractmethod
    async def update_topic(self, topic_id: int, name: str = None, intro: str = None, edu_plan: str = None) -> None:
        """Обновляет тему"""
        pass

    @abstractmethod
    async def delete_topic(self, topic_id: int) -> None:
        """Удаляет тему"""
        pass

    # Операции с блоками (Blocks)
    @abstractmethod
    async def create_block(self, topic_id: int, name: str, content: str) -> int:
        """Создает новый блок"""
        pass

    @abstractmethod
    async def get_block_by_id(self, block_id: int) -> Optional[model.Block]:
        """Получает блок по ID"""
        pass

    @abstractmethod
    async def get_blocks_by_topic_id(self, topic_id: int) -> List[model.Block]:
        """Получает все блоки по ID темы"""
        pass

    @abstractmethod
    async def update_block(self, block_id: int, name: str = None, content: str = None) -> None:
        """Обновляет блок"""
        pass

    @abstractmethod
    async def delete_block(self, block_id: int) -> None:
        """Удаляет блок"""
        pass

    # Операции с главами (Chapters)
    @abstractmethod
    async def create_chapter(self, topic_id: int, block_id: int, name: str, content: str) -> int:
        """Создает новую главу"""
        pass

    @abstractmethod
    async def get_chapter_by_id(self, chapter_id: int) -> Optional[model.Chapter]:
        """Получает главу по ID"""
        pass

    @abstractmethod
    async def get_chapters_by_block_id(self, block_id: int) -> List[model.Chapter]:
        """Получает все главы по ID блока"""
        pass

    @abstractmethod
    async def get_chapters_by_topic_id(self, topic_id: int) -> List[model.Chapter]:
        """Получает все главы по ID темы"""
        pass

    @abstractmethod
    async def update_chapter(self, chapter_id: int, name: str = None, content: str = None) -> None:
        """Обновляет главу"""
        pass

    @abstractmethod
    async def delete_chapter(self, chapter_id: int) -> None:
        """Удаляет главу"""
        pass

    # Дополнительные методы
    @abstractmethod
    async def get_topics_with_statistics(self) -> List[dict]:
        """Получает темы с статистикой (количество блоков и глав)"""
        pass

    @abstractmethod
    async def get_topic_structure(self, topic_id: int) -> dict:
        """Получает полную структуру темы с блоками и главами"""
        pass


