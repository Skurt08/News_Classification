# News Classification API

A Python-based backend service that classifies news articles by their relevance to the business of a wealth management software provider. Given an article URL, it scrapes the content, evaluates relevance through keyword scoring, and uses an LLM to determine sentiment.

## Architecture

The service uses the following pipeline:

```
URL  -->  Scraper  -->  Keyword Scoring  -->  LLM Classification  -->  JSON Response
          (newspaper3k)   (weighted dict)      (OpenAI, conditional)
```

### Step 1 — Scraping (`scraper.py`)

Uses `newspaper3k` to download and parse the article HTML into plain text. Handles five error cases with custom exceptions:
- `PaywallError` — 401/403 responses
- `TimeoutError` — request timeouts
- `RequestError` — general HTTP failures
- `EmptyArticleError` — page parsed but no text extracted
- `ScraperError` — catch-all for unexpected failures

### Step 2 — Keyword Scoring (`classifier.py`)

The extracted text is scored against a weighted keyword dictionary. Higher-weight terms are more domain-specific:

| Weight | Keywords |
|---|---|
| 2.0 | wealth management, portfolio management |
| 1.0 | spm, fintech, analytics, platform, software, dora, mifid, fida |
| 0.5 | basel ii, esma, eu commission, central bank |
| 0.25 | compliance, directive, regulation, oversight, reporting, authorities, regulators |

Each keyword occurrence is counted and multiplied by its weight to produce a total score.

### Step 3 — Classification (`classifier.py`)

The score determines the classification path:

| Score | Action |
|---|---|
| **> 50** | Classified by `gpt-5.4` (high relevance, use strongest model) |
| **20 -- 50** | Classified by `gpt-5-mini` (moderate relevance, lighter model) |
| **< 20** | Labeled `UNRELATED` automatically, no LLM call |

For LLM-classified articles, the model is instructed to evaluate the article from the perspective of a wealth management software company and assess impact across three dimensions:
1. **Compliance & regulation** — Is regulation being tightened or relaxed?
2. **Competition** — New competitors, M&A activity, or new product launches?
3. **Business opportunities** — New potential customers or clients building in-house?

The LLM returns a structured `EvaluationResponse` via OpenAI's structured output (`responses.parse`).

For `UNRELATED` articles, the confidence score is computed as `1 - (score / 20)` — essentially, it measures how close the article was to reach the threshold of 20 that is required to be treated as a related article.

### Step 4 — API Response (`main.py`)

The result is returned as JSON. The most recent classification is also stored in memory and accessible via `GET /latest`.

## Classification Labels

| Label | Meaning |
|---|---|
| `GOOD_NEWS` | Relevant and net positive for the business |
| `BAD_NEWS` | Relevant but net negative for the business |
| `UNRELATED` | Not materially relevant |

## API Endpoints

### `GET /`

Service info and list of available endpoints.

### `GET /health`

Health check. Returns `{"status": "ok"}`.

### `POST /classify`

Classify a news article.

**Request body:**
```json
{
  "url": "https://www.ft.com/content/example-article"
}
```

The `url` field is validated as a proper HTTP URL (`HttpUrl`).

**Success response (200):**
```json
{
  "url": "https://www.ft.com/content/example-article",
  "label": "BAD_NEWS",
  "confidence_score": 0.82,
  "reasoning": "EU tightens DORA enforcement, increasing compliance costs for wealth platforms",
  "relevant_topics": ["regulation", "compliance"],
  "processed_at": "2026-03-16 11:00:00"
}
```

**Error responses:**

| Status | Detail | Cause |
|---|---|---|
| 400 | Request failed: ... | HTTP error fetching the article |
| 403 | Article behind paywall or access denied | 401/403 from the source |
| 408 | Article request timed out | Source did not respond in time |
| 422 | Article content is empty | Page loaded but no text found |
| 422 | Article parsing failed: ... | `newspaper3k` could not parse the page |
| 500 | Internal server error | Unexpected failure |

### `GET /latest`

Returns the most recent classification result. Returns `404` with `"No classification yet"` if no article has been classified since the last restart.

## Tests

| File                 | Scope          | Description                                                         |
| -------------------- | -------------- | ------------------------------------------------------------------- |
| `test_api.py`        | API layer      | Tests FastAPI endpoints, request validation, and response structure |
| `test_classifier.py` | Business logic | Verifies keyword scoring, threshold logic, and LLM routing behavior |
| `test_scraper.py`    | Scraping layer | Tests article extraction and error handling for edge cases          |


## Setup

### Prerequisites

- Python 3.12+
- An OpenAI API key

### Installation

```bash
git clone https://github.com/Skurt08/News_Classification.git
cd News_Classification
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configuration

```bash
cp .env_example .env
```

Edit `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

### Running locally

```bash
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. Interactive Swagger docs at `http://localhost:8000/docs`.

### Example call

```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.ft.com/content/some-article"}'
```

## Deployment

Deployed on [Render](https://render.com/) at **https://news-classification-8gce.onrender.com**

Render configuration:
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment variable:** `OPEN_API_KEY`

Timestamps are returned in `Europe/Copenhagen` timezone.

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI endpoints and error handling
│   ├── scraper.py       # Article fetching via newspaper3k
│   ├── classifier.py    # Keyword scoring + LLM classification logic
│   ├── models.py        # Pydantic models (UrlRequest, EvaluationResponse)
│   └── llm.py           # OpenAI client initialization
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_classifier.py
│   └── test_scraper.py
├── .env_example         # Template for environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## Dependencies

| Package | Purpose |
|---|---|
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `newspaper3k` | Article scraping and text extraction |
| `lxml_html_clean` | HTML cleaning (newspaper3k dependency) |
| `openai` | LLM classification via OpenAI API |
| `pydantic` | Request/response validation and structured output |
| `python-dotenv` | Load `.env` variables |
| `requests` | HTTP client (used by newspaper3k) |
