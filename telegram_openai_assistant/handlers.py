import time
import re
import datetime
import logging
import requests
from telegram.ext import CallbackContext, ContextTypes
from telegram import Update
from openai import OpenAI
from .config import client_api_key
from .config import owner_chat_id
from .utils import get_message_count, update_message_count, save_qa, get_dialog_history,get_dialog_history_short
from .phoneNumberUtil import is_phone_number_exists, parse_name, parse_phone
from .config import (
    CRM_WEBHOOK,
    START_MESSAGE_STICKER,
    START_MESSAGE_TEXT,
    HELP_MESSAGE_TEXT,
    ERROR_MESSAGE_TEXT,
    USER_CALLBACK_CONFIRMATION_TEXT,
    USER_CALLBACK_SUCCEED_TEXT,
    USER_CALLBACK_REQUEST_TEXT,
    USER_CALLBACK_REQUEST_SUMMARY_TEXT,
    USER_DID_NOT_SEND_PHONE_TEXT,
    CHAT_OWNER_DIALOG_SUMMARY_REQUEST,
    CHAT_OWNER_READY_TO_BUY_DIALOG_ESTIMATION_REQUEST,
    CHAT_OWNER_READY_TO_BUY_DIALOG_DISKOUNT_MARKER,
    USER_DISCOUNT_PROVIDED_NOTIFICATIION,
    CHAT_OWNER_DISCOUNT_PROVIDED_NOTIFICATIION,
    PROMOCODE_DETAILS
)

INACTIVITY_TIMEOUT = 300  # 5 min

client = OpenAI(api_key=client_api_key)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(telegram_id)s - %(message)s',
    level=logging.ERROR 
)

class BotHandlers:
    def __init__(self, assistant_id: str, telegram_id: str, application):
        self.assistant_id = assistant_id
        self.telegram_id = telegram_id
        self.user_agreed_policies = False
        self.user_number_sent = False
        self.job_queue = application.job_queue 

    async def start(self, update: Update, context: CallbackContext) -> None:
        """Sends a welcome message to the user."""
        self.reset_state()
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
            max_prompt_tokens=8192 
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
    
    async def timeout_end(self, update: Update, context: CallbackContext):
        # This code will estimate user interes to product and suggest some discount to stir up customer interes
         dialog_str = get_dialog_history(update.effective_user.id, self.telegram_id)
         discount_estimation = self.get_answer(CHAT_OWNER_READY_TO_BUY_DIALOG_ESTIMATION_REQUEST + dialog_str)
         
         if CHAT_OWNER_READY_TO_BUY_DIALOG_DISKOUNT_MARKER in discount_estimation: 
             client_msg = USER_DISCOUNT_PROVIDED_NOTIFICATIION + update.effective_user.username
             chat_owner_msg = CHAT_OWNER_DISCOUNT_PROVIDED_NOTIFICATIION + update.effective_user.username
             await context.bot.send_message(chat_id=owner_chat_id,text=chat_owner_msg)
             await context.bot.send_message(chat_id=update.effective_chat.id, text=client_msg)

         
    async def process_message(self, update: Update, context: CallbackContext) -> None:
        """Processes a message from the user, gets an answer, and sends it back."""
        job_queue = context.application.job_queue
        job = job_queue.run_once(self.timeout_end, INACTIVITY_TIMEOUT, chat_id=update.effective_chat.id, name="inactivity_timeout")
        
        context.user_data["timeout_job"] = job
        if update.message is None:
            return  # Exit if the message is None
        
        dialog_promt = "This in the dialog history. Study the history of answers and questions of this user and all details on the product he is interested in. When giving an answer I use all the details of the dialogue history in order to form an answer. At the end of the message you will find a question that needs to be answered. " 
        dialog_str = get_dialog_history_short(update.effective_user.id, self.telegram_id)
        message_promt = " Answer this question on the language given in the question: "
        message_text = update.message.text
        

        final_promt = dialog_promt + dialog_str + message_promt + message_text
        print(f"final_promt: {final_promt}")
        message_data = get_message_count()
        count = message_data["count"]
        date = message_data["date"]
        today = str(datetime.date.today())

        if date != today:
            count = 0
        if count >= 100:
            return

        answerRaw = self.get_answer(final_promt)
        answer = self.parse_and_clean_response(answerRaw)
        
        if self.user_agreed_policies and not self.user_number_sent:
            
            if is_phone_number_exists(message_text):
                await self.process_callback_message(message_text, update, context)
                await context.bot.send_message(chat_id=update.effective_chat.id, text=USER_CALLBACK_SUCCEED_TEXT)
                
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=USER_DID_NOT_SEND_PHONE_TEXT)
                
            update_message_count(count + 1)     
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
            update_message_count(count + 1)
            
        if USER_CALLBACK_CONFIRMATION_TEXT in answer: 
            self.user_agreed_policies = True

        save_qa(
            update.effective_user.id,
            update.effective_user.username,
            message_text,
            answer,
            self.telegram_id  # Pass the bot's telegram_id to keep track
        )
        
    def parse_and_clean_response(self, response: str) -> str:
        """
        Parses text, removing content in square brackets if it's not a link.
        """
        import re

        def replacer(match):
            text = match.group(1)
            if re.match(r'^(https?://)', text, re.IGNORECASE):
                return f'[{text}]'
            return ''  # Remove text if it's not a link

        cleaned_response = re.sub(r'\[(.*?)\]', replacer, response)
        return cleaned_response  

    async def process_callback_message(self, message, update: Update, context: CallbackContext) -> None:
         self.user_number_sent = True 
         
         dialog_str = get_dialog_history(update.effective_user.id, self.telegram_id)
         dialog_summary = self.get_answer(CHAT_OWNER_DIALOG_SUMMARY_REQUEST + dialog_str)
         await context.bot.send_message(
            chat_id=owner_chat_id,
            text=USER_CALLBACK_REQUEST_TEXT + " " + message + " " + USER_CALLBACK_REQUEST_SUMMARY_TEXT + " " + dialog_summary
            )

         lead_data = {
            "fields": {
                "NAME": parse_name(message),
                "PHONE": [{"VALUE": parse_phone(message), "VALUE_TYPE": "WORK"}],
                "COMMENTS": dialog_summary 
            },
            "params": {"REGISTER_SONET_EVENT": "Y"}
            }

         result = self.send_message_crm(CRM_WEBHOOK, "crm.lead.add", lead_data)
    
         if result:
            print("Lead added!")
            print("ID:", result)
            await context.bot.send_message(
                chat_id=owner_chat_id,
                text=message +  " lead added to srm"
            )
         else:
            print("error adding lead.")
            await context.bot.send_message(
                chat_id=owner_chat_id,
                text=USER_CALLBACK_REQUEST_TEXT + " " + message + " lead are not added to srm"
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
        
    def send_message_crm(self, webhook_url, method: str, data: dict):

        url = f"{webhook_url}"
        print(f"Отправляем запрос на URL: {url}")
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()  # exception for 4xx/5xx
            result = response.json()
            
            if "result" in result:
                return result["result"]
            else:
                print(f"Error in response: {result.get('error_description', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
