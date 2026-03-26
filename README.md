# jbl-chat

## Background

Welcome to JBL Chat! This is the first version of our messaging platform, built by a previous developer. The following user stories have been implemented:

1. As a user, I want to see all other users on the platform.
2. As a user, I want to view my conversation with another user.
3. As a user, I want to be able to send messages to another user on the platform.

The application is built with Django and uses HTMX for interactive front-end experiences.

## Your Task

We'd like you to **review and refactor** this codebase. The application works — all three user stories are functional — but the code quality needs significant improvement.

Please review the code, identify the issues, and refactor it into something you would be proud to ship. Focus on software design principles, security, performance, and Django best practices.

We'd like to see your thought process, so please document the issues you find and explain your reasoning for the changes you make.

## Getting Started

### Using Docker

```bash
docker compose up --build
```

### Using a virtual environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd jbl_chat
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

### Seed Data

Run the seed command to create test users (alice, bob, charlie, diana) with sample messages:

```bash
python manage.py seed_data
```

You can log in as any user from the login page dropdown — no password is required.

## Project Structure

```
jbl_chat/
├── manage.py
├── jbl_chat/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── chat/              # Chat application
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── templates/
    │   └── chat/
    │       ├── base.html
    │       ├── login.html
    │       ├── user_list.html
    │       └── conversation.html
    └── management/
        └── commands/
            └── seed_data.py
```
