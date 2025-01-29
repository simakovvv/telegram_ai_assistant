# storage.py
# Handles storing and retrieving questions/answers

import json
from pathlib import Path

# Define the path to the Q&A file
qa_file = Path("questions_answers.json")

# Ensure the Q&A file exists
if not qa_file.is_file():
    try:
        with open(qa_file, "w") as file:
            json.dump([], file)
        print(f"File {qa_file} created successfully.")
    except Exception as e:
        print(f"Failed to create file {qa_file}: {e}")
        
def save_qa(telegram_id, username, question, answer):
    """Save question and answer pairs to a file along with user information."""
    print("Q&A save start." +  qa_file.is_file())
    qa_file.is_file()
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
    print("Q&A save end.")
