from llm import client

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
                "are affected at the same time) and state the direction of the effect."
                "When you have your result for the classification, confidence score and reasoning, provide your answer according to the response format."
                )
response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "news_classification",
                "schema": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "enum": ["good", "bad"]
                        },
                        "confidence_score": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1
                        },
                        "reasoning": {
                            "type": "string"
                        }
                    },
                    "required": ["label", "confidence_score", "reasoning"],
                    "additionalProperties": False
                }
            }
        }

def classify(text: str, summary: str) -> str:
    summary_lower = summary.lower()

    keywords = {"wealth management": 2,
                "portfolio management": 2,
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

    score = 0
    for key_word in keywords.keys():
        score += summary_lower.count(key_word)*keywords[key_word]

    print(score)

    if score > 5:
        classification = client.responses.create(
            model="gpt-5.4",
            input=text,
            instructions=instructions,
            response_format=response_format
        )
    elif score > 3:
        classification = client.responses.create(
            model="gpt-5.4-mini",
            input=text,
            instructions=instructions,
            response_format=response_format
        )

    else:
        confidence_score = 1-(score / len(summary.split()))
        classification = {"label": "unrelated",
                          "confidence_score": confidence_score,
                          "reasoning": "number of keywords in article summary too small"
            }

    return classification