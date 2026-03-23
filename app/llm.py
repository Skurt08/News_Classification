import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

'''
instructions = ""
chatbot_input = ""
model = "gpt-5.4"

response = client.responses.create(
    model=model,
    input=chatbot_input,
    instructions=instructions
)

print(response.output_text)
'''