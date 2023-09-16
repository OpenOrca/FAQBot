import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OPENAI_API_BASE = 'http://localhost:8001/v1'
OPENAI_API_KEY = 'NONE'
POCKETBASE_URL = 'http://127.0.0.1:8091'