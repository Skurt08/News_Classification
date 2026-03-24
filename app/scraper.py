import logging
from newspaper import Article
from newspaper.article import ArticleException
import requests

logger = logging.getLogger(__name__)

class ScraperError(Exception):
    pass


class PaywallError(ScraperError):
    pass


class TimeoutError(ScraperError):
    pass


class RequestError(ScraperError):
    pass


class EmptyArticleError(ScraperError):
    pass

def extract_article(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()

        if not article.text or not article.text.strip():
            raise EmptyArticleError("Article text is empty")

        return article.text

    except ArticleException as e:
        logger.exception(f"ArticleException for URL: {url}")

        if "401" in str(e) or "403" in str(e):
            raise PaywallError("Access denied or article behind paywall")

        raise ScraperError(f"Article parsing failed: {str(e)}")

    except requests.exceptions.Timeout:
        logger.exception(f"Timeout error for URL: {url}")
        raise TimeoutError("Request timed out")

    except requests.exceptions.RequestException as e:
        logger.exception(f"RequestException for URL: {url}")
        raise RequestError(f"Request failed: {str(e)}")

    except ScraperError:
        raise

    except Exception as e:
        logger.exception(f"Unexpected error for URL: {url}")
        raise ScraperError("Unexpected scraping error")