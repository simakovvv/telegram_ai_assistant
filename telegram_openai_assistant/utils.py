# utils.py
import json
from pathlib import Path
import datetime
import re

# Paths to the files
message_count_file = Path("message_count.json")
qa_file = Path("questions_answers.json")

def get_message_count():
    """Retrieve the current message count."""
    if not message_count_file.exists():
        return {"date": str(datetime.date.today()), "count": 0}
    with open(message_count_file) as file:
        return json.load(file)

def update_message_count(new_count):
    """Update the message count in the file."""
    with open(message_count_file, 'w') as file:
        json.dump({"date": str(datetime.date.today()), "count": new_count}, file)

def sanitize_filename(name: str, max_length: int = 50) -> str:
    """
    Sanitizes a string to be used as a filename.
    Removes invalid characters and limits length.
    """
    name = re.sub(r'[^\w\-]', '_', name)
    return name[:max_length] 


def save_qa(telegram_id, username, question, answer, bot_name):
    """Save question and answer pairs to a file with user information for each bot."""
    # Specify the file for each bot's Q&A data
    file_name = sanitize_filename(bot_name)
    qa_file = Path(f"{file_name}_questions_answers.json")
    
    if not qa_file.exists():
        try:
            with open(qa_file, "w") as file:
                json.dump([], file)
            print(f"File {qa_file} created successfully.")
        except Exception as e:
            print(f"Failed to create file {qa_file}: {e}")
        
    try:
        with open(qa_file, "r+") as file:
            data = json.load(file)
            data.append({
                "telegram_id": telegram_id,
                "username": username,
                "question": question,
                "answer": answer
            })
            file.seek(0)
            json.dump(data, file, indent=4)
            print("Q&A saved successfully. File location: " + str(qa_file.resolve()))
    except Exception as e:
        print(f"Failed to save Q&A: {e}")
        
def get_dialog_history(telegram_id: int, bot_name) -> str:
    """Retrieve dialog history for a given Telegram ID as a JSON string."""
    file_name = sanitize_filename(bot_name)
    qa_file = Path(f"{file_name}_questions_answers.json")
    try:
        if not qa_file.exists():
            print(f"Error: Dialog history not found for bot: {bot_name}")
            return json.dumps({"error": "Dialog history not found."}) 
        
        with open(qa_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        user_dialogs = [entry for entry in data if entry.get("telegram_id") == telegram_id]

        message_count = len(user_dialogs)
        print(f"Found {message_count} messages for Telegram ID {telegram_id} in bot '{bot_name}'")

        return json.dumps(user_dialogs, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error: Failed to retrieve dialog history for Telegram ID {telegram_id}: {str(e)}")
        return json.dumps({"error": f"Failed to retrieve dialog history: {str(e)}"})

def get_dialog_history_short(telegram_id: int, bot_name) -> str:
    """Retrieve the last 10 dialog messages for a given Telegram ID as a JSON string without the 'answer' field."""
    file_name = sanitize_filename(bot_name)
    qa_file = Path(f"{file_name}_questions_answers.json")

    try:
        if not qa_file.exists():
            print(f"Error: Dialog history not found for bot: {bot_name}")
            return json.dumps({"error": "Dialog history not found."}) 
        
        with open(qa_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Filter messages for the given telegram_id
        user_dialogs = [entry for entry in data if entry.get("telegram_id") == telegram_id]

        # Get the last 10 messages
        last_10_messages = user_dialogs[-10:]

        # Create a new list with "answer" field removed while preserving the structure
        cleaned_messages = [{k: v for k, v in message.items() if k != "answer"} for message in last_10_messages]
        cleaned_messages = [{k: v for k, v in message.items() if k != "username"} for message in last_10_messages]
        cleaned_messages = [{k: v for k, v in message.items() if k != "telegram_id"} for message in last_10_messages]

        message_count = len(cleaned_messages)
        print(f"Found {message_count} messages for Telegram ID {telegram_id} in bot '{bot_name}' (without answers)")

        return json.dumps(cleaned_messages, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error: Failed to retrieve dialog history for Telegram ID {telegram_id}: {str(e)}")
        return json.dumps({"error": f"Failed to retrieve dialog history: {str(e)}"})
