import os

from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/alma-uploads")
FORM_URL = "https://mendrika-alma.github.io/form-submission/"
