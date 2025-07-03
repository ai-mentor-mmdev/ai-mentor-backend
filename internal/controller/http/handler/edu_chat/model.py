from pydantic import BaseModel


class SendMessageToExpert(BaseModel):
    account_id: int
    text: str

