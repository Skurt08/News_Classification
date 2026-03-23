from fastapi import FastAPI, HTTPException
from app.scraper import extract_article
from app.classifier import classify
from app.models import EvaluationResponse

app = FastAPI(title="News Evaluator API")

@app.get("/evaluate", response_model=EvaluationResponse)
def evaluate(url: str):
    try:
        art_info = extract_article(url)
        label, reasoning = classify(art_info["text"], art_info["summary"])

        return EvaluationResponse(
            url=url,
            publisher=art_info["publisher"],
            title=art_info["title"],
            date=art_info["date"],
            paywall=art_info["paywall"],
            label=label,
            reasoning=reasoning
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
def root():
    return {"message": "News Evaluator API is running"}