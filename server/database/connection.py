import sqlite3
from pathlib import Path

def get_connection():
    #db_path = Path(__file__).parent / "pysync_chat.db"
    #connection = sqlite3.connect(db_path)
    #print("done")
    #print(db_path)
    connection = sqlite3.connect("pysync_chat.db")
    return connection


if __name__ == "__main__":
    start = get_connection()
    