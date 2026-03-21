from pydantic import BaseModel

class EvaluationResponse(BaseModel):
    label: str
    reasoning: str