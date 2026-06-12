# Student Management System

A lightweight Flask application for managing student records, academic profiles, and exam marks.

## Overview

This app provides a simple student management system with role-based access control. Admin users can add and manage student accounts, update scores across predefined subjects, and view all students and users. Student users can log in to view their own profile, marks, total score, percentage, and rank.

## Key features

- User registration and login using `flask_login`
- Admin and student roles
- Secure password hashing with `werkzeug.security`
- SQLite database with `flask_sqlalchemy`
- Student profile management
- Marks entry and edit support for multiple subjects
- Automated score summary, percentage calculation, and rank generation

## Technologies

- Python
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLite
- Jinja2 templates

## Getting started

1. Create and activate a virtual environment

```bash
python -m venv venv
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# Windows (cmd)
venv\Scripts\activate
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app

```bash
python app.py
```

4. Open the app in your browser

```bash
http://127.0.0.1:5000
```

## Usage

- Register a new user as an admin (allowed only once)
- Admins can add new student accounts and manage profiles
- Students can log in and view their own marks and profile details

## Notes

- Change `app.config['SECRET_KEY']` before deploying to production
- The default database file is `students.db`
- This project is ideal for learning Flask and CRUD-based web apps

## GitHub Profile

Find the project and other work on GitHub:

`https://github.com/yeshwanthreddyk15-ui`
