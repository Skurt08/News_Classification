from unittest.mock import patch, MagicMock
import pytest
import requests
from newspaper.article import ArticleException

from app.scraper import (
    extract_article,
    PaywallError,
    TimeoutError,
    RequestError,
    EmptyArticleError,
    ScraperError,
)


class TestExtractArticleSuccess:
    @patch("app.scraper.Article")
    def test_returns_article_text(self, mock_article_class):
        mock_article = MagicMock()
        mock_article.text = "This is the article content."
        mock_article_class.return_value = mock_article

        result = extract_article("https://example.com/article")

        assert result == "This is the article content."
        mock_article.download.assert_called_once()
        mock_article.parse.assert_called_once()


class TestExtractArticleErrors:
    @patch("app.scraper.Article")
    def test_empty_article_raises_error(self, mock_article_class):
        mock_article = MagicMock()
        mock_article.text = ""
        mock_article_class.return_value = mock_article

        with pytest.raises(EmptyArticleError):
            extract_article("https://example.com/empty")

    @patch("app.scraper.Article")
    def test_whitespace_only_article_raises_error(self, mock_article_class):
        mock_article = MagicMock()
        mock_article.text = "   \n\t  "
        mock_article_class.return_value = mock_article

        with pytest.raises(EmptyArticleError):
            extract_article("https://example.com/whitespace")

    @patch("app.scraper.Article")
    def test_403_raises_paywall_error(self, mock_article_class):
        mock_article_class.return_value.download.side_effect = ArticleException("403 Forbidden")

        with pytest.raises(PaywallError):
            extract_article("https://example.com/paywall")

    @patch("app.scraper.Article")
    def test_401_raises_paywall_error(self, mock_article_class):
        mock_article_class.return_value.download.side_effect = ArticleException("401 Unauthorized")

        with pytest.raises(PaywallError):
            extract_article("https://example.com/auth")

    @patch("app.scraper.Article")
    def test_other_article_exception_raises_scraper_error(self, mock_article_class):
        mock_article_class.return_value.download.side_effect = ArticleException("Something else")

        with pytest.raises(ScraperError):
            extract_article("https://example.com/broken")

    @patch("app.scraper.Article")
    def test_timeout_raises_timeout_error(self, mock_article_class):
        mock_article_class.return_value.download.side_effect = requests.exceptions.Timeout()

        with pytest.raises(TimeoutError):
            extract_article("https://example.com/slow")

    @patch("app.scraper.Article")
    def test_request_exception_raises_request_error(self, mock_article_class):
        mock_article_class.return_value.download.side_effect = requests.exceptions.ConnectionError("refused")

        with pytest.raises(RequestError):
            extract_article("https://example.com/down")

    @patch("app.scraper.Article")
    def test_unexpected_exception_raises_scraper_error(self, mock_article_class):
        mock_article_class.return_value.download.side_effect = RuntimeError("unexpected")

        with pytest.raises(ScraperError):
            extract_article("https://example.com/crash")
