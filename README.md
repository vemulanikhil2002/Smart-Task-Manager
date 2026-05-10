# Smart Task Management System (Django Edition)

A Python-based web application built with **Django**, **SQLite**, **Pandas & NumPy**, and **Django Channels (WebSockets)**.

---

## Tech Stack

| Technology        | Purpose                        |
|-------------------|-------------------------------|
| Python + Django   | Backend & REST API             |
| SQLite            | Database (built-in, no setup)  |
| Django Channels   | Real-time WebSocket updates    |
| Pandas & NumPy    | Analytics module               |
| HTML + CSS        | Frontend UI                    |

---

## Features

- ✅ User Registration, Login & Logout (Django Auth)
- ✅ Full CRUD REST API for Tasks (Add, Update, Delete, Get All)
- ✅ Task fields: Title, Description, Priority, Status, Created Date
- ✅ SQLite database with Django ORM
- ✅ Analytics using Pandas & NumPy (total, completed, pending, completion %)
- ✅ Real-time WebSocket notifications via Django Channels
- ✅ Clean, responsive HTML/CSS frontend

---

## Setup Instructions

### 1. Clone / Extract the Project

```bash
cd smart_task_manager_django
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations (creates db.sqlite3 automatically)

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000**

---

## REST API Endpoints

| Method | Endpoint                         | Description        |
|--------|----------------------------------|--------------------|
| GET    | `/api/tasks/`                    | Get all user tasks |
| POST   | `/api/tasks/add/`                | Create a new task  |
| PUT    | `/api/tasks/<id>/update/`        | Update a task      |
| DELETE | `/api/tasks/<id>/delete/`        | Delete a task      |
| GET    | `/api/analytics/`                | Get analytics data |

### Example POST `/api/tasks/add/`

```json
{
  "title": "Complete assignment",
  "description": "Finish the Django project",
  "priority": "high",
  "status": "pending"
}
```

---

## WebSocket

Connects at: `ws://localhost:8000/ws/tasks/`

Events emitted: `task_added`, `task_updated`, `task_deleted`

---

## Project Structure

```
smart_task_manager_django/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3               ← auto-created after migrate
├── smart_task_manager/      ← Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── tasks/                   ← Main Django app
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── consumers.py         ← WebSocket consumer
│   ├── routing.py
│   └── migrations/
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## Notes

- No PostgreSQL or Redis required — uses SQLite and in-memory channel layer
- Django admin available at `/admin/` (create superuser: `python manage.py createsuperuser`)
# Smart-Task-Manager
