from flask import Flask, jsonify, request # type: ignore
from flask_cors import CORS # type: ignore
from flask_sqlalchemy import SQLAlchemy # type: ignore

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the ToDo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)

# Create the database and the tables
with app.app_context():
    db.create_all()

@app.route('/api/todos', methods=['GET', 'POST', 'DELETE'])
def manage_todos():
    if request.method == 'POST':
        # Add a new to-do item
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
        # Return all to-do items
        todos = Todo.query.all()
        todos_list = [{"id": todo.id, "task": todo.task} for todo in todos]
        return jsonify({"todos": todos_list})
    
    elif request.method == 'DELETE':
        # Delete a to-do item by its ID
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