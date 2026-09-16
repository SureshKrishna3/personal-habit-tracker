# Personal Habit Tracker

A clean, modern, responsive Personal Habit Tracker web application built with Python, Flask, HTML5, CSS3, JavaScript (Fetch API), and SQLite.

This project is structured as a foundational web application designed to be containerized with Docker and deployed to Kubernetes in future DevOps learning milestones.

---

## 🚀 Features

- **Add New Habit**: Easily create habits with custom categories (Health, Fitness, Productivity, Learning, Mindset, General) and optional descriptions.
- **Track Progress**: Mark habits as completed or incomplete for today with a single click.
- **Active Streaks**: Automatically calculates daily completion streaks for each habit.
- **Real-Time Dashboard Stats**: Live metrics showing:
  - Total habits
  - Completed habits today
  - Pending habits today
  - Completion progress percentage bar & circular ring indicator
- **Category & Status Filtering**: Filter habits by status (*All*, *Pending*, *Completed*) or category.
- **Delete Habit**: Remove habits cleanly along with associated historical log records.
- **Responsive & Modern UI**: Built with a sleek glassmorphic dark theme, CSS variables, and fluid mobile/desktop layouts.

---

## 📁 Project Structure & File Purpose

```
personal-habit-tracker/
├── app.py              # Main Flask web application defining REST API endpoints and routes
├── database.py         # SQLite helper functions for CRUD operations, streak calculations, & database schema initialization
├── test_app.py         # Automated unit tests for API endpoints & business logic
├── requirements.txt    # Python package dependencies (Flask)
├── README.md           # Project documentation and local execution instructions
├── static/
│   ├── css/
│   │   └── style.css   # Custom responsive CSS design system (dark glassmorphism theme, animations)
│   └── js/
│       └── app.js      # Frontend JavaScript logic handling Fetch API requests, UI updates, and modals
└── templates/
    └── index.html      # Main responsive HTML dashboard page
```

### File Explanations:

1. **`app.py`**: The entry point for the Python Flask web application. Defines routes (`/`, `/api/habits`, `/api/stats`, `/api/habits/<id>/toggle`, `/api/habits/<id>`) for rendering the dashboard and handling JSON API requests.
2. **`database.py`**: Encapsulates SQLite database operations (`habits.db`). Manages table creation (`habits` and `habit_logs`), toggling daily statuses, deleting records, calculating consecutive daily streaks, and computing statistical metrics.
3. **`templates/index.html`**: The single-page app layout containing the dashboard header, stat cards, progress indicators, filter controls, habit grid container, habit creation modal, and notification toast element.
4. **`static/css/style.css`**: Contains custom styling, glassmorphism card design, category badges, progress ring gradients, animations, and responsive breakpoints for mobile and desktop screens.
5. **`static/js/app.js`**: Client-side JavaScript logic. Interacts with Flask REST endpoints asynchronously using `fetch()`, updates stats without full page reloads, manages filter tabs, and handles modal form submissions.
6. **`requirements.txt`**: Lists external Python library dependencies required to run the web application (`Flask`).
7. **`test_app.py`**: Unit tests verifying API behavior (creating, retrieving, toggling completion, stats calculation, and deleting habits).

---

## 🛠️ How to Run Locally

### 1. Prerequisites
- Python 3.8+ installed on your machine.

### 2. Install Dependencies
Open your terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### 3. Start the Web Application
Run the Flask server:
```bash
python app.py
```

### 4. Access the Dashboard
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Running Automated Tests

To execute the unit tests and verify API correctness:
```bash
python test_app.py
```
