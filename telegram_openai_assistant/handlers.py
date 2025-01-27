import time
import datetime
import logging
from telegram.ext import CallbackContext, ContextTypes
from telegram import Update
from openai import OpenAI
from .config import client_api_key
from .config import owner_chat_id
from .utils import get_message_count, update_message_count, save_qa
from .phoneNumberUtil import is_phone_number_exists, parse_name, parse_phone
from .config import (
    START_MESSAGE_STICKER,
    START_MESSAGE_TEXT,
    HELP_MESSAGE_TEXT,
    ERROR_MESSAGE_TEXT,
    USER_CALLBACK_CONFIRMATION_TEXT,
    USER_CALLBACK_SUCCEED_TEXT,
    USER_CALLBACK_REQUEST_TEXT,
    USER_CALLBACK_REQUEST_SUMMARY_TEXT,
    USER_DID_NOT_SEND_PHONE_TEXT
)
client = OpenAI(api_key=client_api_key)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(telegram_id)s - %(message)s',
    level=logging.ERROR 
)

class BotHandlers:
    def __init__(self, assistant_id: str, telegram_id: str):
        self.assistant_id = assistant_id
        self.telegram_id = telegram_id
        self.user_agreed_policies = False
        self.user_number_sent = False

    async def start(self, update: Update, context: CallbackContext) -> None:
        """Sends a welcome message to the user."""
        await context.bot.send_sticker(update.effective_chat.id, START_MESSAGE_STICKER)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=START_MESSAGE_TEXT
        )

    def reset_state(self):
        """Resets the state of the bot's flags."""
        self.user_agreed_policies = False
        self.user_number_sent = False
        
    async def help_command(self, update: Update, context: CallbackContext) -> None:
        """Sends a help message to the user."""
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=HELP_MESSAGE_TEXT,
        )

    def get_answer(self, message_str) -> None:
        """Get answer from assistant using the assistant_id."""
        thread = client.beta.threads.create()
        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=message_str
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.assistant_id,  # Use the assistant_id passed when creating the handler
        )

        # Poll for the response (this could be improved with async calls)
        while True:
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run.status == "completed":
                break
            time.sleep(1)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = messages.dict()["data"][0]["content"][0]["text"]["value"]
        return response

    async def process_message(self, update: Update, context: CallbackContext) -> None:
        """Processes a message from the user, gets an answer, and sends it back."""
        if update.message is None:
            return  # Exit if the message is None

        previous_message = context.user_data.get("previous_user_message")
        
        message_text = update.message.text

        message_data = get_message_count()
        count = message_data["count"]
        date = message_data["date"]
        today = str(datetime.date.today())

        if date != today:
            count = 0
        if count >= 100:
            return

        answer = self.get_answer(message_text)
        
        if USER_CALLBACK_CONFIRMATION_TEXT in answer: 
            self.user_agreed_policies = True
       
        if self.user_agreed_policies and not self.user_number_sent:
            
            # Processing callback intention
            #if previous_message is not None and is_phone_number_exists(previous_message):
                #await self.process_callback_message(previous_message, context)
                #await context.bot.send_message(chat_id=update.effective_chat.id, text=USER_CALLBACK_SUCCEED_TEXT)
                
            if is_phone_number_exists(message_text):
                await self.process_callback_message(message_text, context)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=USER_CALLBACK_SUCCEED_TEXT)
                
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=USER_DID_NOT_SEND_PHONE_TEXT)
                
            update_message_count(count + 1)     
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
            update_message_count(count + 1)
            
        context.user_data["previous_user_message"] = message_text
            
        save_qa(
            update.effective_user.id,
            update.effective_user.username,
            message_text,
            answer,
            self.telegram_id  # Pass the bot's telegram_id to keep track
        )
        
    async def process_callback_message(self, message, context: CallbackContext) -> None:
         self.user_number_sent = True 
         await context.bot.send_message(
            chat_id=owner_chat_id,
            text=USER_CALLBACK_REQUEST_TEXT + " " + message
            )


    async def error_handler(self, update,  context: ContextTypes.DEFAULT_TYPE):

        logging.error("Error: %s", context.error)
        """Sends a error message to the user."""
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=ERROR_MESSAGE_TEXT,
        )
        await context.bot.send_message(
            chat_id=owner_chat_id,
            text=f"Error: {context.error}"
        )
