from flask import Flask, render_template, request, jsonify
from datetime import datetime
import database

app = Flask(__name__)

# Initialize database tables on server startup
with app.app_context():
    database.init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/habits', methods=['GET'])
def get_habits():
    target_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    habits = database.get_all_habits_with_status(target_date)
    return jsonify(habits)

@app.route('/api/habits', methods=['POST'])
def create_habit():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    category = data.get('category', 'General')
    description = data.get('description', '')

    if not name or not name.strip():
        return jsonify({'error': 'Habit name is required'}), 400

    habit_id = database.add_habit(name, category, description)
    return jsonify({
        'message': 'Habit created successfully',
        'id': habit_id
    }), 201

@app.route('/api/habits/<int:habit_id>/toggle', methods=['POST'])
def toggle_habit(habit_id):
    data = request.get_json(silent=True) or {}
    target_date = data.get('date', datetime.now().strftime("%Y-%m-%d"))
    is_completed = database.toggle_habit_completion(habit_id, target_date)
    
    if is_completed is None:
        return jsonify({'error': 'Habit not found'}), 404

    return jsonify({
        'message': 'Habit status updated',
        'habit_id': habit_id,
        'completed': is_completed
    })

@app.route('/api/habits/<int:habit_id>', methods=['DELETE'])
def delete_habit(habit_id):
    deleted = database.delete_habit(habit_id)
    if not deleted:
        return jsonify({'error': 'Habit not found'}), 404
        
    return jsonify({
        'message': 'Habit deleted successfully',
        'habit_id': habit_id
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    target_date = request.args.get('date', datetime.now().strftime("%Y-%m-%d"))
    stats = database.get_stats(target_date)
    return jsonify(stats)

if __name__ == '__main__':
    # Local dev server runs on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
