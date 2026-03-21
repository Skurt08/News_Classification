from newspaper import Article

def extract_article(url: str) -> str:
    article = Article(url)
    article.download()
    article.parse()

    if not article.text:
        raise ValueError("Could not extract article content")

    return article.text