# config.py
from dotenv import load_dotenv
import os

# Load the environment variables from the .env file.
load_dotenv()

# Retrieve TELEGRAM_TOKEN as a comma-separated string and split it into a list
telegram_token_bots = os.getenv("TELEGRAM_TOKEN_BOT", "").split(",")

# Retrieve ASSISTANT_ID as a comma-separated string and split it into a list
assistant_id_bots = os.getenv("ASSISTANT_ID_BOT", "").split(",")
client_api_key = os.getenv("CLIENT_API_KEY")
owner_chat_id = os.getenv("OWNER_CHAT_ID")
# Optional: Clean up whitespace from each item in the lists
telegram_token_bots = [token.strip() for token in telegram_token_bots if token.strip()]
assistant_id_bots = [aid.strip() for aid in assistant_id_bots if aid.strip()]

# Debugging print to verify the lists (remove in production)
print("Telegram Tokens:", telegram_token_bots)
print("Assistant IDs:", assistant_id_bots)
print("Client API Key:", client_api_key)
print("Owner chat id:", owner_chat_id)

CRM_WEBHOOK = os.getenv("CRM_WEBHOOK")
START_MESSAGE_STICKER = os.getenv("START_MESSAGE_STICKER")

START_MESSAGE_TEXT = os.getenv("START_MESSAGE_TEXT")

HELP_MESSAGE_TEXT = os.getenv("HELP_MESSAGE_TEXT")

ERROR_MESSAGE_TEXT = os.getenv("ERROR_MESSAGE_TEXT")

USER_CALLBACK_CONFIRMATION_TEXT = os.getenv("USER_CALLBACK_CONFIRMATION_TEXT")

USER_CALLBACK_SUCCEED_TEXT = os.getenv("USER_CALLBACK_SUCCEED_TEXT")

USER_CALLBACK_REQUEST_TEXT = os.getenv("USER_CALLBACK_REQUEST_TEXT")

USER_CALLBACK_REQUEST_SUMMARY_TEXT = os.getenv("USER_CALLBACK_REQUEST_SUMMARY_TEXT")
USER_DID_NOT_SEND_PHONE_TEXT = os.getenv("USER_DID_NOT_SEND_PHONE_TEXT")
CHAT_OWNER_DIALOG_SUMMARY_REQUEST = os.getenv("CHAT_OWNER_DIALOG_SUMMARY_REQUEST")
CHAT_OWNER_READY_TO_BUY_DIALOG_ESTIMATION_REQUEST = os.getenv("CHAT_OWNER_READY_TO_BUY_DIALOG_ESTIMATION_REQUEST")
CHAT_OWNER_READY_TO_BUY_DIALOG_DISKOUNT_MARKER = os.getenv("CHAT_OWNER_READY_TO_BUY_DIALOG_DISKOUNT_MARKER")
USER_DISCOUNT_PROVIDED_NOTIFICATIION = os.getenv("USER_DISCOUNT_PROVIDED_NOTIFICATIION")
CHAT_OWNER_DISCOUNT_PROVIDED_NOTIFICATIION = os.getenv("CHAT_OWNER_DISCOUNT_PROVIDED_NOTIFICATIION")
PROMOCODE_DETAILS = os.getenv("PROMOCODE_DETAILS")