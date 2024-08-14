import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables from .env file, if it exists
load_dotenv()

app = Flask(__name__)
CORS(app)

# Determine the database URI
database_uri = os.getenv('DATABASE_URL')
if not database_uri:
    # Use Vercel's POSTGRES_URL if DATABASE_URL isn't set
    database_uri = os.getenv('POSTGRES_URL')

if not database_uri:
    raise RuntimeError("DATABASE_URL or POSTGRES_URL must be set.")

app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/api/todos', methods=['GET', 'POST', 'DELETE'])
def manage_todos():
    if request.method == 'POST':
        data = request.get_json()
        new_todo = data.get('todo', '')
        if new_todo:
            todo = Todo(task=new_todo)
            db.session.add(todo)
            db.session.commit()
            return jsonify({"message": "To-Do added successfully!", "todo": {"id": todo.id, "task": todo.task}})
        else:
            return jsonify({"error": "No To-Do provided"}), 400
    
    elif request.method == 'GET':
        todos = Todo.query.all()
        todos_list = [{"id": todo.id, "task": todo.task} for todo in todos]
        return jsonify({"todos": todos_list})
    
    elif request.method == 'DELETE':
        data = request.get_json()
        todo_id = data.get('id', None)
        if todo_id is not None:
            todo = Todo.query.get(todo_id)
            if todo:
                db.session.delete(todo)
                db.session.commit()
                return jsonify({"message": f"Deleted To-Do: {todo.task}"})
            else:
                return jsonify({"error": "To-Do not found"}), 404
        else:
            return jsonify({"error": "Invalid ID"}), 400

if __name__ == '__main__':
    app.run(debug=True)
