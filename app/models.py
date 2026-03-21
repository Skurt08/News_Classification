from pydantic import BaseModel

class EvaluationResponse(BaseModel):
    url: str
    publisher: str
    title: str
    date: str
    paywall: str
    label: str
    reasoning: str