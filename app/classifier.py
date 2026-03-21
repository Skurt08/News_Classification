from typing import Tuple

def classify(text: str) -> Tuple[str, str]:
    text_lower = text.lower()

    negative_keywords = ["war", "crisis", "death", "conflict", "disaster"]
    positive_keywords = ["innovation", "growth", "breakthrough", "success", "improvement"]

    neg_hits = sum(word in text_lower for word in negative_keywords)
    pos_hits = sum(word in text_lower for word in positive_keywords)

    if neg_hits > pos_hits:
        return "BAD_NEWS", f"Detected {neg_hits} negative indicators"
    elif pos_hits > neg_hits:
        return "GOOD_NEWS", f"Detected {pos_hits} positive indicators"
    else:
        return "UNRELATED", "No strong sentiment indicators found"