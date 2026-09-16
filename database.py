import sqlite3
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'habits.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Habits Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'General',
            description TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Habit Logs Table (tracks daily completions)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_date TEXT NOT NULL,
            status INTEGER DEFAULT 1,
            FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
            UNIQUE(habit_id, completed_date)
        )
    ''')

    conn.commit()
    conn.close()

def calculate_streak(cursor, habit_id, today_str):
    today = datetime.strptime(today_str, "%Y-%m-%d").date()
    
    # Fetch all completed dates for this habit sorted descending
    cursor.execute('''
        SELECT completed_date FROM habit_logs
        WHERE habit_id = ? AND status = 1
        ORDER BY completed_date DESC
    ''', (habit_id,))
    
    rows = cursor.fetchall()
    completed_dates = {row['completed_date'] for row in rows}
    
    if not completed_dates:
        return 0
    
    streak = 0
    # Check if completed today; if not, start checking from yesterday
    check_date = today
    if today_str not in completed_dates:
        check_date = today - timedelta(days=1)
        if check_date.strftime("%Y-%m-%d") not in completed_dates:
            return 0

    while check_date.strftime("%Y-%m-%d") in completed_dates:
        streak += 1
        check_date -= timedelta(days=1)
        
    return streak

def get_all_habits_with_status(target_date=None):
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT h.id, h.name, h.category, h.description, h.created_at,
               COALESCE(hl.status, 0) as completed_today
        FROM habits h
        LEFT JOIN habit_logs hl ON h.id = hl.habit_id AND hl.completed_date = ?
        ORDER BY h.id DESC
    ''', (target_date,))
    
    raw_habits = cursor.fetchall()
    habits = []
    
    for row in raw_habits:
        habit_dict = dict(row)
        habit_dict['completed_today'] = bool(habit_dict['completed_today'])
        habit_dict['streak'] = calculate_streak(cursor, habit_dict['id'], target_date)
        habits.append(habit_dict)
        
    conn.close()
    return habits

def add_habit(name, category='General', description=''):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO habits (name, category, description)
        VALUES (?, ?, ?)
    ''', (name.strip(), category.strip(), description.strip()))
    conn.commit()
    habit_id = cursor.lastrowid
    conn.close()
    return habit_id

def toggle_habit_completion(habit_id, target_date=None):
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if habit exists first
    cursor.execute('SELECT id FROM habits WHERE id = ?', (habit_id,))
    if not cursor.fetchone():
        conn.close()
        return None
    
    # Check current status for target date
    cursor.execute('''
        SELECT status FROM habit_logs
        WHERE habit_id = ? AND completed_date = ?
    ''', (habit_id, target_date))
    
    row = cursor.fetchone()
    
    if row:
        new_status = 0 if row['status'] == 1 else 1
        cursor.execute('''
            UPDATE habit_logs SET status = ?
            WHERE habit_id = ? AND completed_date = ?
        ''', (new_status, habit_id, target_date))
    else:
        new_status = 1
        cursor.execute('''
            INSERT INTO habit_logs (habit_id, completed_date, status)
            VALUES (?, ?, 1)
        ''', (habit_id, target_date))
        
    conn.commit()
    conn.close()
    return bool(new_status)

def delete_habit(habit_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_stats(target_date=None):
    if not target_date:
        target_date = datetime.now().strftime("%Y-%m-%d")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM habits')
    total = cursor.fetchone()['total']
    
    cursor.execute('''
        SELECT COUNT(*) as completed FROM habit_logs hl
        JOIN habits h ON hl.habit_id = h.id
        WHERE hl.completed_date = ? AND hl.status = 1
    ''', (target_date,))
    completed = cursor.fetchone()['completed']
    
    conn.close()
    
    pending = total - completed if total >= completed else 0
    percentage = round((completed / total) * 100, 1) if total > 0 else 0
    
    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'percentage': percentage,
        'date': target_date
    }
