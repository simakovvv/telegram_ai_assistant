import time
import datetime
import logging
from telegram.ext import CallbackContext, ContextTypes
from telegram import Update
from openai import OpenAI
from .config import client_api_key
from .config import owner_chat_id
from .utils import get_message_count, update_message_count, save_qa

client = OpenAI(api_key=client_api_key)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(telegram_id)s - %(message)s',
    level=logging.ERROR 
)

class BotHandlers:
    def __init__(self, assistant_id: str, telegram_id: str):
        self.assistant_id = assistant_id
        self.telegram_id = telegram_id

    async def start(self, update: Update, context: CallbackContext) -> None:
        """Sends a welcome message to the user."""
        await context.bot.send_sticker(update.effective_chat.id, "CAACAgIAAxkBAAEL3IhnkkzltKE9c7VWaAKQOCOAWBYu3QACY2IAAo_RkUgT75gxRA0-4jYE")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Здравствуйте! Меня зовут Дмитрий, я основатель компании Weform. Наша команда создала и обучила виртуального помощника, "
    "чтобы помочь вам с выбором банного чана и ответить на любые вопросы. Просто спросите, что вас интересует."
        )

    async def help_command(self, update: Update, context: CallbackContext) -> None:
        """Sends a help message to the user."""
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Помошник отвечает на любые вопросы касающиеся банных чанов. Если вы хотите, чтобы мы связались с вами - попросите ссылки на форму обратной связи или наш телефон.",
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
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
        update_message_count(count + 1)
        save_qa(
            update.effective_user.id,
            update.effective_user.username,
            message_text,
            answer,
            self.telegram_id  # Pass the bot's telegram_id to keep track
        )
    async def error_handler(self, update,  context: ContextTypes.DEFAULT_TYPE):

        logging.error("Произошла ошибка: %s", context.error)
        """Sends a error message to the user."""
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Сейчас ассистент отдыхает. Наша команда уже работает над его возвращением. Можете воспользоваться контактами на сайте что бы получить нужную информацию.",
        )
        try:
            await context.bot.send_message(
            chat_id=owner_chat_id,
            text=f"Произошла ошибка: {context.error}"
            )
        except Exception as e:
            logging.error(f"Не удалось уведомить владельца: {e}")
