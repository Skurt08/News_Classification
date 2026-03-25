from unittest.mock import patch
#import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import EvaluationResponse
from app.scraper import PaywallError, TimeoutError, EmptyArticleError, RequestError, ScraperError


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestRootEndpoint:
    def test_root_returns_service_info(self):
        response = client.get("/")
        data = response.json()

        assert response.status_code == 200
        assert data["service"] == "News Classification API"
        assert "POST /classify" in data["endpoints"]
        assert "GET /latest" in data["endpoints"]
        assert "GET /health" in data["endpoints"]


class TestLatestEndpoint:
    def test_latest_returns_404_when_empty(self):
        import app.main as main_module
        main_module.latest_result = None

        response = client.get("/latest")
        assert response.status_code == 404

    def test_latest_returns_result_after_classify(self):
        import app.main as main_module
        main_module.latest_result = EvaluationResponse(
            url="https://example.com/test",
            label="GOOD_NEWS",
            confidence_score=0.9,
            reasoning="Test reasoning",
            relevant_topics=["compliance"],
            processed_at="2026-03-24 12:00:00"
        )

        response = client.get("/latest")
        assert response.status_code == 200
        assert response.json()["label"] == "GOOD_NEWS"


class TestClassifyEndpoint:
    @patch("app.main.classify_article")
    @patch("app.main.extract_article")
    def test_classify_success(self, mock_extract, mock_classify):
        mock_extract.return_value = "Article text about wealth management"
        mock_classify.return_value = EvaluationResponse(
            url="https://example.com/article",
            label="GOOD_NEWS",
            confidence_score=0.85,
            reasoning="Positive for wealth tech",
            relevant_topics=["business opportunities"],
            processed_at="2026-03-24 12:00:00"
        )

        response = client.post("/classify", json={"url": "https://example.com/article"})

        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "GOOD_NEWS"
        assert data["confidence_score"] == 0.85
        assert data["url"] == "https://example.com/article"

    @patch("app.main.extract_article")
    def test_classify_timeout_returns_408(self, mock_extract):
        mock_extract.side_effect = TimeoutError("timed out")

        response = client.post("/classify", json={"url": "https://example.com/slow"})
        assert response.status_code == 408

    @patch("app.main.extract_article")
    def test_classify_paywall_returns_403(self, mock_extract):
        mock_extract.side_effect = PaywallError("paywall")

        response = client.post("/classify", json={"url": "https://example.com/paywall"})
        assert response.status_code == 403

    @patch("app.main.extract_article")
    def test_classify_empty_returns_422(self, mock_extract):
        mock_extract.side_effect = EmptyArticleError("empty")

        response = client.post("/classify", json={"url": "https://example.com/empty"})
        assert response.status_code == 422

    @patch("app.main.extract_article")
    def test_classify_request_error_returns_400(self, mock_extract):
        mock_extract.side_effect = RequestError("connection refused")

        response = client.post("/classify", json={"url": "https://example.com/down"})
        assert response.status_code == 400

    @patch("app.main.extract_article")
    def test_classify_scraper_error_returns_422(self, mock_extract):
        mock_extract.side_effect = ScraperError("parse failed")

        response = client.post("/classify", json={"url": "https://example.com/broken"})
        assert response.status_code == 422

    @patch("app.main.extract_article")
    def test_classify_unexpected_error_returns_500(self, mock_extract):
        mock_extract.side_effect = RuntimeError("unexpected")

        response = client.post("/classify", json={"url": "https://example.com/crash"})
        assert response.status_code == 500

    def test_classify_invalid_url_returns_422(self):
        response = client.post("/classify", json={"url": "not-a-url"})
        assert response.status_code == 422

    def test_classify_missing_url_returns_422(self):
        response = client.post("/classify", json={})
        assert response.status_code == 422

    @patch("app.main.classify_article")
    @patch("app.main.extract_article")
    def test_classify_updates_latest(self, mock_extract, mock_classify):
        import app.main as main_module

        expected = EvaluationResponse(
            url="https://example.com/new",
            label="BAD_NEWS",
            confidence_score=0.7,
            reasoning="Negative impact",
            relevant_topics=["regulation"],
            processed_at="2026-03-24 12:00:00"
        )
        mock_extract.return_value = "some text"
        mock_classify.return_value = expected

        client.post("/classify", json={"url": "https://example.com/new"})

        assert main_module.latest_result == expected
