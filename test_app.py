import unittest
import json
import os
import database

# Override database path for testing
database.DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_habits.db')

from app import app

class HabitTrackerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        database.init_db()

    def tearDown(self):
        if os.path.exists(database.DB_PATH):
            os.remove(database.DB_PATH)

    def test_create_and_get_habit(self):
        # Test habit creation
        res = self.app.post('/api/habits', data=json.dumps({
            'name': 'Drink 2L Water',
            'category': 'Health',
            'description': 'Stay hydrated all day'
        }), content_type='application/json')
        
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertIn('id', data)
        habit_id = data['id']

        # Test habit listing
        res = self.app.get('/api/habits')
        self.assertEqual(res.status_code, 200)
        habits = json.loads(res.data)
        self.assertEqual(len(habits), 1)
        self.assertEqual(habits[0]['name'], 'Drink 2L Water')
        self.assertFalse(habits[0]['completed_today'])

        # Test habit toggle
        res = self.app.post(f'/api/habits/{habit_id}/toggle', data=json.dumps({}), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        toggle_data = json.loads(res.data)
        self.assertTrue(toggle_data['completed'])

        # Test stats update
        res = self.app.get('/api/stats')
        self.assertEqual(res.status_code, 200)
        stats = json.loads(res.data)
        self.assertEqual(stats['total'], 1)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['percentage'], 100.0)

        # Test delete habit
        res = self.app.delete(f'/api/habits/{habit_id}')
        self.assertEqual(res.status_code, 200)
        
        res = self.app.get('/api/habits')
        habits = json.loads(res.data)
        self.assertEqual(len(habits), 0)

if __name__ == '__main__':
    unittest.main()
