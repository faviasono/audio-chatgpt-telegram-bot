import sqlite3
import json
from typing import List, Dict, Union

DATABASE_FILE = "gptbot_db.sqlite"

SYSTEM_RULE = {
    "role": "system",
    "content": "you are a friendly bot that gives short answers",
}


def create_db():
    # Create a connection to the database
    with sqlite3.connect(DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id TEXT PRIMARY KEY,
                history TEXT
            );
        """
        )
        conn.commit()


def add_new_user(user: str):
    new_user = {"telegram_id": user, "history": json.dumps([SYSTEM_RULE])}

    with sqlite3.connect(DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO users (telegram_id, history) VALUES (?, ?)",
            (new_user["telegram_id"], new_user["history"]),
        )
        conn.commit()


def retrieve_history(user: str) -> Dict:
    with sqlite3.connect(DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id = ?", (user,))
        row = c.fetchone()

    return row


def reset_history_user(user: str):
    with sqlite3.connect(DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE users SET history = ? WHERE telegram_id = ?",
            (json.dumps([SYSTEM_RULE]), user),
        )


def create_question_prompt(row: Dict, question: str) -> Dict:
    history = json.loads(row[1])
    rule = {"role": "user", "content": question}
    history.append(rule)
    return history


def update_history_user(user: str, question: str, answer: str):
    with sqlite3.connect(DATABASE_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id = ?", (user,))
        row = c.fetchone()
        if row:
            user = {"telegram_id": row[0], "history": json.loads(row[1])}
            question_rule = {"role": "user", "content": question}
            answer_rule = {"role": "assistant", "content": answer}
            user["history"].append(question_rule)
            user["history"].append(answer_rule)
            updated_history = json.dumps(user["history"])
            c.execute(
                "UPDATE users SET history = ? WHERE telegram_id = ?",
                (updated_history, user["telegram_id"]),
            )


if __name__ == "__main__":
    user = "323232"
    add_new_user(user)

    question = "What's the meaning of life?"
    answer = "42"

    update_history_user(user=user, question=question, answer=answer)

    row = retrieve_history(user)
    print("after update: ", row)

    reset_history_user(user)
    print("\n" * 4)

    row = retrieve_history(user)
    print("After reset: ", row)