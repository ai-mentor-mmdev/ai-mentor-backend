from .model import *
from internal import interface

class EduChatController:
    def __init__(
            self,
            edu_chat_service: interface.IEduChatService
    ):
        pass

    def send_message_to_interview_expert(self, body: SendMessageToExpert):
        pass

    def send_message_to_teacher(self, body: SendMessageToExpert):
        pass

    def send_message_to_test_expert(self, body: SendMessageToExpert):
        pass