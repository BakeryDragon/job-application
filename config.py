import os
from dotenv import load_dotenv

load_dotenv()
DATABASE = "database.db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
