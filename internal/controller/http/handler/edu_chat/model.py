from pydantic import BaseModel


class SendMessageToExpert(BaseModel):
    account_id: int
    text: str


class SendMessageToExpertResponse(BaseModel):
    llm_response: str