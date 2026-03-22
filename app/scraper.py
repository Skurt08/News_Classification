from newspaper import Article
from newspaper.article import ArticleException
from urllib.parse import urlparse
import logging
import requests

logging.basicConfig(
    level=logging.ERROR,
    filename='error.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def extract_article(url: str) -> dict:
    result = {
        "publisher": None,
        "title": None,
        "date": None,
        "text": None,
        "paywalled": None,
        "error": None
    }

    try:
        article = Article(url)
        article.download()
        article.parse()

        result["publisher"] = urlparse(article.source_url).netloc
        result["title"] = article.title
        result["date"] = article.publish_date

        if article.text:
            result["text"] = article.text
            if len(article.text.split()) >= 200:
                result["paywalled"] = "unlikely"
            else:
                result["paywalled"] = "likely"
        else:
            result["error"] = "empty_text"
            logger.error(f"Empty text for URL: {url}")

    except ArticleException as e:
        logger.exception(f"ArticleException for URL: {url}")

        if "401" in str(e) or "403" in str(e):
            result["paywalled"] = "yes"
            result["error"] = "access_denied"
        else:
            result["error"] = str(e)

    except requests.exceptions.Timeout as e:
        logger.exception(f"Timeout error for URL: {url}")
        result["error"] = "timeout"

    except requests.exceptions.RequestException as e:
        logger.exception(f"RequestException for URL: {url}")
        result["error"] = "request_error"

    except Exception as e:
        # Catch-all for unexpected issues
        logger.exception(f"Unexpected error for URL: {url}")
        result["error"] = "unknown_error"

    return result

art = Article("https://worldbusinessoutlook.com/top-10-fintech-wealth-management-platforms-in-2026/?utm_source=chatgpt.com")
art.download()
art.parse()
print(art.title)
print(type(art.text))
#print(urlparse(art.source_url).netloc)
#print(art.url)