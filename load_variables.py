import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
    )

# Initialize Groq LLM
from langchain_groq import ChatGroq

llm = ChatGroq(
    model_name="llama-3.1-8b-instant",
    temperature=0.0
)