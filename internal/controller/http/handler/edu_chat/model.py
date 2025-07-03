from pydantic import BaseModel


class SendMessageToExpert(BaseModel):
    student_id: int
    text: str


class SendMessageToExpertResponse(BaseModel):
    llm_response: str