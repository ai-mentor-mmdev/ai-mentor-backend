from abc import abstractmethod
from typing import Protocol
from internal.controller.http.handler.edu_chat.model import *
from internal import model


class IEduChatController(Protocol):
    @abstractmethod
    async def send_message_to_interview_expert(self, body: SendMessageToExpert): pass

    @abstractmethod
    async def send_message_to_teacher(self, body: SendMessageToExpert): pass

    @abstractmethod
    async def send_message_to_test_expert(self, body: SendMessageToExpert): pass


class IEduChatService(Protocol):
    @abstractmethod
    async def send_message_to_interview_expert(self, student_id: int, text: str): pass

    @abstractmethod
    async def send_message_to_teacher(self, student_id: int, text: str): pass

    @abstractmethod
    async def send_message_to_test_expert(self, student_id: int, text: str): pass


class IEduPromptService(Protocol):
    @abstractmethod
    async def get_interview_expert_prompt(self, student_id: int) -> str: pass

    @abstractmethod
    async def get_teacher_prompt(self, student_id: int) -> str: pass

    @abstractmethod
    async def get_test_expert_prompt(self, student_id: int) -> str: pass


class IEduChatRepo(Protocol):
    @abstractmethod
    async def create_chat(self, student_id: int) -> int:
        pass

    @abstractmethod
    async def get_chat_by_student_id(self, student_id: int) -> list[model.EduChat]:
        pass

    @abstractmethod
    async def get_chat_by_id(self, chat_id: int) -> list[model.EduChat]:
        pass

    @abstractmethod
    async def add_message(self, edu_chat_id: int, text: str, role: str) -> int:
        pass

    @abstractmethod
    async def get_messages_by_chat_id(self, edu_chat_id: int, limit: int = 50) -> list[model.EduMessage]: pass
