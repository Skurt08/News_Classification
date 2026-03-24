from fastapi import FastAPI, HTTPException
from app.scraper import extract_article
from app.classifier import classify_article
from app.models import EvaluationResponse

app = FastAPI(title="News Evaluator API")

latest_result = None

@app.post("/classify", response_model=EvaluationResponse)
def classify_endpoint(url: str):
    global latest_result
    try:
        art_info = extract_article(url)

        if not art_info or not art_info.get("text"):
            raise HTTPException(status_code=422, detail="Article content is empty")

        result = classify_article(art_info["text"], url)

        latest_result = result
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
def root():
    return {"message": "News Evaluator API is running"}

@app.get("/latest", response_model=EvaluationResponse)
def latest():
    if latest_result is None:
        raise HTTPException(status_code=404, detail="No classification yet")
    return latest_result