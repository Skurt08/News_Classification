import os
from dotenv import load_dotenv
from openai import OpenAI



load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))

'''
class Outputformat(BaseModel):
    name: str
    date: str
    activity: str

instructions = "Derive from the input who is doing which activity on which time and summarise it in few words"
chatbot_input = "Someone named Carl is playing a game called football on a time from tomorrow at 7 pm."
model = "gpt-5.4"

response = client.responses.parse(
    model=model,
    input=chatbot_input,
    instructions=instructions,
    text_format=Outputformat
)

print(response.output_text)
'''