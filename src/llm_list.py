import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm_openai = ChatOpenAI(
    model="gpt-4o-mini-2024-07-18",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)