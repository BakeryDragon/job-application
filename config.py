import os

from dotenv import load_dotenv

load_dotenv()
DATABASE = "database.db"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BACKUP_DIR = os.getenv("BACKUP_DIR")
