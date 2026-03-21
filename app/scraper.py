from newspaper import Article
from newspaper.article import ArticleException
import requests
from urllib.parse import urlparse
import logging

def extract_article(url: str) -> dict:

    logging.basicConfig(level=logging.ERROR, filename='error.log', filemode='w',
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
            if article.text.count(" ") >= 200:
                result["paywalled"] = "unlikely"
            else: result["paywalled"] = "likely"
        else:
            result["error"] = "empty_text"

    except ArticleException as e:
        if "401" in str(e) or "403" in str(e):
            result["paywalled"] = "yes"
            result["error"] = "access_denied"
        else:
            result["error"] = str(e)

    #except requests.exceptions.Timeout as e:


    return result

art = Article("https://www.handelsblatt.com/politik/international/iran-krieg-wir-koennen-nicht-fuehrende-mittelmacht-sein-wollen-und-dann-nichts-tun-01/100209719.html")
art.download()
art.parse()
#print(art.title)
print(urlparse(art.source_url).netloc)
print(art.url)