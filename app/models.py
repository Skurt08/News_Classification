from pydantic import BaseModel

class EvaluationResponse(BaseModel):
    url: str
    publisher: str
    title: str
    date: str
    paywall: str
    label: str
    reasoning: str
    confidence: float

class ResponseFormat(BaseModel):
    label: str
    confidence_score: float
    reasoning: str