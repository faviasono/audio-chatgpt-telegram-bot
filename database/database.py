import json
import os
from typing import Dict

import psycopg2
from dotenv import load_dotenv

load_dotenv("app/.env")

db_host = os.environ.get("PGHOST")
db_user = os.environ.get("PGUSER")
db_password = os.environ.get("PGPASSWORD")
db_name = os.environ.get("PGDATABASE")




SYSTEM_RULE = {
    "role": "system",
    "content": "you are friendly bot and gives answers up to 50 words.",
}


def create_db():
    # Create a connection to the database
    with psycopg2.connect(
        host=db_host, user=db_user, password=db_password, database=db_name
    ) as conn:
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

    with psycopg2.connect(
        host=db_host, user=db_user, password=db_password, database=db_name
    ) as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (telegram_id, history) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
            (new_user["telegram_id"], new_user["history"]),
        )
        conn.commit()


def retrieve_history(user: str) -> Dict:
    with psycopg2.connect(
        host=db_host, user=db_user, password=db_password, database=db_name
    ) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id = %s", (user,))
        row = c.fetchone()

    return row


def reset_history_user(user: str):
    with psycopg2.connect(
        host=db_host, user=db_user, password=db_password, database=db_name
    ) as conn:
        c = conn.cursor()
        c.execute(
            "UPDATE users SET history = %sWHERE telegram_id = %s",
            (json.dumps([SYSTEM_RULE]), user),
        )


def create_question_prompt(row: Dict, question: str) -> Dict:
    history = json.loads(row[1])
    rule = {"role": "user", "content": question}
    history.append(rule)
    return history


def update_history_user(user: str, question: str, answer: str):
    with psycopg2.connect(
        host=db_host, user=db_user, password=db_password, database=db_name
    ) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE telegram_id = %s", (user,))
        row = c.fetchone()
        if row:
            user = {"telegram_id": row[0], "history": json.loads(row[1])}
            question_rule = {"role": "user", "content": question}
            answer_rule = {"role": "assistant", "content": answer}
            user["history"].append(question_rule)
            user["history"].append(answer_rule)
            updated_history = json.dumps(user["history"])
            c.execute(
                "UPDATE users SET history = %sWHERE telegram_id = %s",
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
