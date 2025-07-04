from abc import abstractmethod
from typing import Protocol, Optional
from internal import model


class IStudentRepo(Protocol):
    @abstractmethod
    async def create_student(self, student: model.Student) -> int:
        """Создает нового студента и возвращает его ID"""
        pass

    @abstractmethod
    async def get_by_id(self, student_id: int) -> list[model.Student]:
        """Получает студента по ID"""
        pass

    @abstractmethod
    async def get_by_account_id(self, account_id: int) -> list[model.Student]:
        """Получает студента по account_id"""
        pass

    @abstractmethod
    async def update(self, student: model.Student) -> None:
        """Обновляет данные студента"""
        pass

    @abstractmethod
    async def set_interview_stage(self, student_id: int, stage: str) -> None:
        """Устанавливает текущий этап интервью"""
        pass


class IStudentService(Protocol):
    @abstractmethod
    async def create_student(self, account_id: int, login: str, password: str) -> model.Student:
        """Создает нового студента с базовым профилем"""
        pass

    @abstractmethod
    async def get_or_create_student(self, account_id: int) -> model.Student:
        """Получает существующего студента или создает нового"""
        pass

    @abstractmethod
    async def update_student_profile(self, student_id: int, updates: dict) -> None:
        """Обновляет профиль студента на основе анализа диалога"""
        pass

    @abstractmethod
    async def generate_learning_plan(self, student_id: int) -> dict:
        """Генерирует персональный план обучения"""
        pass

    @abstractmethod
    async def apply_learning_plan(self, student_id: int, plan: dict) -> None:
        """Применяет сгенерированный план обучения к профилю студента"""
        pass