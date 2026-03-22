from math import sqrt
from llm import client

instructions = ("You are the manager of a company that develops software for wealth and asset managers."
                "Your product is a connected platform that unifies data, systems and workflows."
                "The product spans over portfolio management, reporting, compliance, integration and AI-enabled operations."
                "Among your customers are wealth and asset managers, private banks, financial institutions, family offices and advisory platforms."
                "All your customers depends on your solution as their backbone of daily operations."
                "Your task is to evaluate whether the news you will read are net positive or net negative for your business."
                "The following aspects can be relevant for the business: 1) compliance and revised regulations:"
                "Is financial regulation such as DORA, MiFID II, FiDA or similar being tightened (negative impact) or relaxed (positive impact)"
                "2) competition: are there any new competitors, was there m&a activity in the industry or did an existing competitor release a new product (negative impact)"
                "or did competition become easier (positive impact)"
                "3) business opportunities: do potential customers work on inhouse solutions (negative impact) or are there new potential customers (positive impact)"
                )
chatbot_input = ("Classify the content of the newspaper article as positive or negative for the business."
                "Provide a confidence score between 0 and 1 and give a short reasoning by stating which of the aspects is mainly affected (it is possible that more than 1"
                "are affected at the same time) and state the direction of the effect")

def classify(text: str) -> str:
    text_lower = text.lower()

    regulation_keywords = {"dora": 1,
                           "mifid": 1,
                           "fida": 1,
                           "basel ii": 0.5,
                           "esma": 0.5,
                           "compliance": 0.25,
                           "directive": 0.25,
                           "regulation": 0.25,
                           "oversight": 0.25,
                           "reporting": 0.25,
                           "authorities": 0.25,
                           "regulators": 0.25,
                           "eu commission": 0.5,
                           "central bank": 0.5}

    competition_keywords = {"wealth management": 2,
                            "portfolio management": 2,
                            "platform": 0.5,
                            "software": 0.5,
                            "fintech": 1,
                            "analytics": 1}

    regulation_score = 0
    for key_word in regulation_keywords:
        regulation_score += text_lower.count(key_word)*regulation_keywords[key_word]

    competition_score = 0
    for key_word in competition_keywords:
        competition_score += text_lower.count(key_word)*competition_keywords[key_word]

    total_score = sqrt((regulation_score + competition_score) / (text_lower.count(" ") + 1))

    if total_score > 5:
        classification = client.responses.create(
            model="gpt-5.4",
            input=chatbot_input,
            instructions=instructions,
        )
    elif total_score > 3:
        classification = client.responses.create(
            model="gpt-5.4-mini",
            input=chatbot_input,
            instructions=instructions
        )

    else:
        confidence_score = 1-total_score
        classification = f"label: unrelated with confidence score {confidence_score} and reasoning number of keywords in text is too small"


    return classification