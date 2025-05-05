from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

DB_NAME = 'puzzles.db'

# Initialize the database
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS puzzles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                grid TEXT,
                clues TEXT,
                clue_numbers TEXT,
                created_at TEXT,
                assigned_date TEXT
            )
        ''')
        conn.commit()

@app.route('/api/puzzles', methods=['POST'])
def save_puzzle():
    data = request.json
    title = data.get("title", "Untitled Puzzle")
    grid = json.dumps(data.get("grid", {}))
    clues = json.dumps(data.get("clues", {"across": [], "down": []}))
    clue_numbers = json.dumps(data.get("clue_numbers", {}))
    created_at = datetime.now().isoformat()
    assigned_date = data.get("assigned_date") or created_at[:10]

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO puzzles (title, grid, clues, clue_numbers, created_at, assigned_date) VALUES (?, ?, ?, ?, ?, ?)",
            (title, grid, clues, clue_numbers, created_at, assigned_date)
        )
        conn.commit()
        puzzle_id = cursor.lastrowid

    return jsonify({"status": "success", "id": puzzle_id}), 201

@app.route('/api/puzzles', methods=['GET'])
def list_puzzles():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, created_at, assigned_date FROM puzzles ORDER BY created_at DESC")
        rows = cursor.fetchall()
        puzzles = [{"id": row[0], "title": row[1], "created_at": row[2], "assigned_date": row[3]} for row in rows]

    return jsonify(puzzles)

@app.route('/api/puzzles/<int:puzzle_id>', methods=['GET'])
def get_puzzle(puzzle_id):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, grid, clues, clue_numbers, created_at, assigned_date FROM puzzles WHERE id = ?", (puzzle_id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": "Puzzle not found"}), 404

        puzzle = {
            "id": row[0],
            "title": row[1],
            "grid": json.loads(row[2]),
            "clues": json.loads(row[3]),
            "clue_numbers": json.loads(row[4]) if row[4] else {},
            "created_at": row[5],
            "assigned_date": row[6]
        }

    return jsonify(puzzle)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)