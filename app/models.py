from pydantic import BaseModel, HttpUrl

class EvaluationResponse(BaseModel):
    url: str
    label: str
    confidence_score: float
    reasoning: str
    relevant_topics: list[str]
    processed_at: str

class UrlRequest(BaseModel):
    url: HttpUrl