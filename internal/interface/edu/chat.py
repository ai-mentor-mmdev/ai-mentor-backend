from abc import abstractmethod
from typing import Protocol
from internal.controller.http.handler.edu.chat.model import *
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
        pass
