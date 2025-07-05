from typing import Protocol


class IPromptGenerator(Protocol):
    pass


class IChatController(Protocol):
    pass


class IChatService(Protocol):
    pass


class IChatRepo(Protocol):
    pass
