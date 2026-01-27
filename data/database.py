# Взаимодействие с SQLite
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'game_statistics.db')


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            result TEXT,
            game_time TEXT,
            score INTEGER,
            enemies_killed INTEGER,
            levels_completed INTEGER
        )
    ''')

    conn.commit()
    conn.close()


def save_game_stats(result: str, game_time: str, score: int, enemies_killed: int, levels_completed: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO game_stats (result, game_time, score, enemies_killed, levels_completed)
        VALUES (?, ?, ?, ?, ?)
    ''', (result, game_time, score, enemies_killed, levels_completed))

    conn.commit()
    conn.close()


def get_last_game_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM game_stats 
        WHERE id = (SELECT MAX(id) FROM game_stats)
    ''')
    result = cursor.fetchone()

    conn.close()
    return result


def get_average_score():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT AVG(score) FROM game_stats')
    result = cursor.fetchone()[0]

    conn.close()
    return int(result) if result else 0


def get_all_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM game_stats ORDER BY id DESC')
    results = cursor.fetchall()

    conn.close()
    return results

