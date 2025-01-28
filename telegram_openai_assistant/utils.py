# utils.py
import json
from pathlib import Path
import datetime

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

def save_qa(telegram_id, username, question, answer, bot_name):
    """Save question and answer pairs to a file with user information for each bot."""
    # Specify the file for each bot's Q&A data
    qa_file = Path(f"{telegram_id}_questions_answers.json")
    
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
