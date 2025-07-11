import os
from dotenv import load_dotenv

# Load .env variables into the environment
load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
