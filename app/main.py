from fastapi import FastAPI, HTTPException
from app.scraper import extract_article
from app.classifier import classify
from app.models import EvaluationResponse

app = FastAPI(title="News Evaluator API")

@app.get("/evaluate", response_model=EvaluationResponse)
def evaluate(url: str):
    try:
        text = extract_article(url)
        label, reasoning = classify(text)

        return EvaluationResponse(
            label=label,
            reasoning=reasoning
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
def root():
    return {"message": "News Evaluator API is running"}