from fastapi import FastAPI, HTTPException
from app.scraper import (
    extract_article,
    ScraperError,
    PaywallError,
    TimeoutError,
    RequestError,
    EmptyArticleError,
)
from app.classifier import classify_article
from app.models import EvaluationResponse
import logging

app = FastAPI(title="News Evaluator API")

logger = logging.getLogger(__name__)

latest_result = None


@app.post("/classify", response_model=EvaluationResponse)
def classify_endpoint(url: str):
    global latest_result

    try:
        art_text = extract_article(url)

        result = classify_article(art_text, url)

        latest_result = result
        return result

    except TimeoutError:
        raise HTTPException(status_code=408, detail="Article request timed out")

    except PaywallError:
        raise HTTPException(status_code=403, detail="Article behind paywall or access denied")

    except EmptyArticleError:
        raise HTTPException(status_code=422, detail="Article content is empty")

    except RequestError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except ScraperError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except Exception:
        logger.exception("Unexpected error in /classify endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/latest", response_model=EvaluationResponse)
def latest():
    if latest_result is None:
        raise HTTPException(status_code=404, detail="No classification yet")
    return latest_result


@app.get("/health")
def health():
    return {"status": "ok"}