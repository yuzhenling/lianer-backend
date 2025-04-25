from pydantic import BaseModel


class ExamRequest(BaseModel):
    q: str
