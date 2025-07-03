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
    async def send_message_to_interview_expert(self, account_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_to_teacher(self, account_id: int, text: str) -> str: pass

    @abstractmethod
    async def send_message_to_test_expert(self, account_id: int, text: str) -> str: pass

    @abstractmethod
    async def get_or_create_chat(self, account_id: int) -> int: pass

    @abstractmethod
    async def create_message(self, edu_chat_id: int, text: str) -> int: pass


class IEduChatRepo(Protocol):
    @abstractmethod
    async def get_chat_by_account_id(self, account_id: int) -> list[model.EduChat]: pass

    @abstractmethod
    async def create_chat(self, account_id: int) -> int: pass

    @abstractmethod
    async def create_message(self, edu_chat_id: int, text: str) -> int: pass

    @abstractmethod
    async def get_messages_by_chat_id(self, edu_chat_id: int) -> list[model.EduMessage]: pass


class IEduProgressRepo(Protocol):
    @abstractmethod
    async def get_progress_by_account_id(self, account_id: int) -> model.EduProgress: pass

    @abstractmethod
    async def get_current_topic(self, account_id: int) -> model.Topic: pass

    @abstractmethod
    async def get_current_block(self, account_id: int) -> model.Block: pass

    @abstractmethod
    async def get_current_chapter(self, account_id: int) -> model.Chapter: pass


class IEduPromptService(Protocol):
    @abstractmethod
    async def get_interview_expert_prompt(self, account_id: int) -> str: pass

    @abstractmethod
    async def get_teacher_prompt(self, account_id: int) -> str: pass

    @abstractmethod
    async def get_test_expert_prompt(self, account_id: int) -> str: pass