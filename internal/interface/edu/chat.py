from abc import abstractmethod
from typing import Protocol
from internal.controller.http.handler.edu.chat.model import *
from internal import model


class IEduChatPromptGenerator(Protocol):
    pass


class IEduChatController(Protocol):
    pass


class IEduChatService(Protocol):
    pass


class IEduChatRepo(Protocol):
    pass
