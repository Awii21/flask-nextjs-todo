import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from psycopg2 import pool

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize a connection pool
database_uri = os.getenv('POSTGRES_URL')
if not database_uri:
    raise RuntimeError("POSTGRES_URL must be set in the .env file.")

try:
    conn_pool = psycopg2.pool.SimpleConnectionPool(1, 20, database_uri)
    if conn_pool:
        print("Connection pool created successfully")
except Exception as e:
    print(f"Error creating connection pool: {e}")
    raise e

@app.route('/api/todos', methods=['GET', 'POST', 'DELETE'])
def manage_todos():
    conn = None
    cursor = None
    try:
        # Get a connection from the pool
        conn = conn_pool.getconn()
        cursor = conn.cursor()

        if request.method == 'POST':
            data = request.get_json()
            new_todo = data.get('todo', '')
            if new_todo:
                cursor.execute("INSERT INTO todo (task) VALUES (%s) RETURNING id, task;", (new_todo,))
                conn.commit()
                todo = cursor.fetchone()
                return jsonify({"message": "To-Do added successfully!", "todo": {"id": todo[0], "task": todo[1]}})
            else:
                return jsonify({"error": "No To-Do provided"}), 400

        elif request.method == 'GET':
            cursor.execute("SELECT id, task FROM todo;")
            todos = cursor.fetchall()
            todos_list = [{"id": todo[0], "task": todo[1]} for todo in todos]
            return jsonify({"todos": todos_list})

        elif request.method == 'DELETE':
            data = request.get_json()
            todo_id = data.get('id', None)
            if todo_id is not None:
                cursor.execute("DELETE FROM todo WHERE id = %s RETURNING task;", (todo_id,))
                conn.commit()
                todo = cursor.fetchone()
                if todo:
                    return jsonify({"message": f"Deleted To-Do: {todo[0]}"})
                else:
                    return jsonify({"error": "To-Do not found"}), 404
            else:
                return jsonify({"error": "Invalid ID"}), 400

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure the cursor and connection are properly closed
        if cursor:
            cursor.close()
        if conn:
            conn_pool.putconn(conn)

if __name__ == '__main__':
    app.run(debug=True)

# The teardown function should remain here but without closing the connection pool
@app.teardown_appcontext
def close_db_connection(exception):
    pass  # Don't close the pool here; it should remain open for the app's lifecycle
