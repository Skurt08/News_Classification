from app.llm import client
from app.models import ResponseFormat

instructions = ("You are the manager of a company that develops software for wealth and asset managers."
                "Your product is a connected platform that unifies data, systems and workflows."
                "The product spans over portfolio management, reporting, compliance, integration and AI-enabled operations."
                "Among your customers are wealth and asset managers, private banks, financial institutions, family offices and advisory platforms."
                "All your customers depend on your solution as their backbone of daily operations."
                "Your task is to evaluate whether the news you will read are net positive or net negative for your business."
                "The following aspects can be relevant for the business: 1) compliance and revised regulations:"
                "Is financial regulation such as DORA, MiFID II, FiDA or similar being tightened (negative impact) or relaxed (positive impact)"
                "2) competition: are there any new competitors, was there m&a activity in the industry or did an existing competitor release a new product (negative impact)"
                "or did competition become easier (positive impact)"
                "3) business opportunities: do potential customers work on inhouse solutions (negative impact) or are there new potential customers (positive impact)"
                "Classify the content of the newspaper article as good news or bad news for the business."
                "Provide a confidence score between 0 and 1 and give a short reasoning by stating which of the aspects is mainly affected (it is possible that more than 1"
                "are affected at the same time). The reasoning should not be longer than 100 characters."
                )

keywords = {"wealth management": 2,
            "portfolio management": 2,
            "spm":  1,
            "fintech": 1,
            "analytics": 1,
            "platform": 1,
            "software": 1,
            "dora": 1,
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

def classify(text: str) -> str:
    text_lower = text.lower()

    score = 0
    for key_word in keywords.keys():
        score += text_lower.count(key_word)*keywords[key_word]

    if score > 50:
        llm_call = client.responses.parse(
            model="gpt-5.4",
            input=text,
            instructions=instructions,
            text_format=ResponseFormat
        )
        classification = llm_call.output_text
    elif score >= 20:
        llm_call = client.responses.parse(
            model="gpt-5-mini",
            input=text,
            instructions=instructions,
            text_format=ResponseFormat
        )
        classification = llm_call.output_text
    else:
        confidence_score = 1-(score / 20)
        classification = {"label": "unrelated",
                          "confidence_score": confidence_score,
                          "reasoning": "number of keywords in article text too small"
            }

    return classification