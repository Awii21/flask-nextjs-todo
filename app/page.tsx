import { useState, useEffect } from 'react';

type Todo = {
    id: number;
    task: string;
};

export default function Home() {
    const [todos, setTodos] = useState<Todo[]>([]);
    const [newTodo, setNewTodo] = useState('');

    const apiUrl = process.env.NEXT_PUBLIC_API_URL;

    useEffect(() => {
        fetch(`${apiUrl}/todos`)
            .then((response) => response.json())
            .then((data) => setTodos(data.todos))
            .catch((error) => console.error('Error fetching todos:', error));
    }, [apiUrl]);

    const handleAddTodo = () => {
        if (newTodo.trim() === '') return;  // Prevent adding empty todos
        fetch(`${apiUrl}/todos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                todo: newTodo
            })
        })
        .then((response) => response.json())
        .then((data) => {
            setTodos([...todos, data.todo as Todo]);  // Add the new todo to the current state
            setNewTodo('');  // Clear the input field
        })
        .catch((error) => console.error('Error adding todo:', error));
    };

    const handleDeleteTodo = (id: number) => {
        fetch(`${apiUrl}/todos`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id
            })
        })
        .then((response) => response.json())
        .then(() => setTodos(todos.filter(todo => todo.id !== id)))
        .catch((error) => console.error('Error deleting todo:', error));
    };

    return (
        <div className="min-h-screen flex flex-col items-center justify-center bg-gray-950 py-10 text-black">
            <h1 className="text-4xl font-bold mb-6 text-gray-100">To-Do App</h1>
            <div className='text-lg mb-4 font-semibold text-gray-300'>FrontEnd - Next.js | Backend - Flask</div>
            <div className="bg-teal-800 p-10 hover:p-8 rounded-xl shadow-2xl w-80 hover:scale-110 hover:mt-5 transition-all duration-500">
                <div className="mb-4">
                    <input
                        type="text"
                        value={newTodo}
                        onChange={(e) => setNewTodo(e.target.value)}
                        onKeyPress={(event) => event.key === 'Enter' && handleAddTodo()}
                        placeholder="Enter a new To-Do"
                        className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <button
                    className="w-full bg-green-500 text-white px-3 py-2 rounded-lg hover:bg-green-600 transition-colors duration-300"
                    onClick={handleAddTodo}
                >
                    Add To-Do
                </button>
                <ul className="mt-4 text-gray-200">
                    {todos.map((todo) => (
                        <li key={todo.id} className="flex justify-between items-center mb-2">
                            <span>{todo.task}</span>
                            <button
                                className="bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600 transition-colors duration-300"
                                onClick={() => handleDeleteTodo(todo.id)}
                            >
                                Delete
                            </button>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
