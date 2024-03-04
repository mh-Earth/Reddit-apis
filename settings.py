from dotenv import load_dotenv
from os import environ
load_dotenv()

CLIENT_ID=environ.get("client_id")
CLIENT_SECRET=environ.get("client_secret")
USER_AGENT=environ.get("user_agent")
API_KEY=environ.get("api_key")
