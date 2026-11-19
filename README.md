# TaskFlow

TaskFlow is a Django-based project and task management application. It provides a personal workspace where authenticated users can organize projects and track tasks by status, priority, and due date.

## Features

- User registration, login, and logout
- Create, view, update, and delete projects
- Create, view, update, and delete tasks
- Task status and priority tracking
- Task search and status filtering
- Paginated task list
- Dashboard with project and task summaries
- Per-user project and task access control
- Automated Django tests

## Tech stack

- Python 3.13
- Django 5.2
- SQLite for local development
- HTML and CSS

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/immsepehr/TaskFlow.git
cd TaskFlow
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

TaskFlow reads configuration from environment variables and does not automatically load a `.env` file. Set a unique local development secret before running Django.

Windows PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = "replace-with-a-long-random-local-secret"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1,[::1]"
```

macOS/Linux:

```bash
export DJANGO_SECRET_KEY="replace-with-a-long-random-local-secret"
export DJANGO_DEBUG="True"
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,[::1]"
```

For production, set a strong, unique `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=False`, and configure `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` through your hosting platform. Never commit real secrets to the repository.

### 5. Apply migrations and run the development server

```bash
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Running tests

```bash
python manage.py test accounts tasks -v 2
```

## Production checklist

Before deployment:

1. Set a strong, unique `DJANGO_SECRET_KEY`.
2. Set `DJANGO_DEBUG=False`.
3. Set `DJANGO_ALLOWED_HOSTS` to the deployed hostname(s), comma-separated.
4. Set `DJANGO_CSRF_TRUSTED_ORIGINS` to the full HTTPS origin(s), comma-separated (for example, `https://example.com`).
5. Configure a persistent production database. SQLite is intended for local development in this project.
6. Run `python manage.py check --deploy` and resolve all deployment warnings.
7. Run `python manage.py collectstatic --noinput` and configure the hosting platform to serve `staticfiles/`.

## Project structure

```text
TaskFlow/
|-- accounts/       # Registration and authentication
|-- config/         # Django project settings and URL configuration
|-- tasks/          # Projects, tasks, views, templates, and static assets
|-- manage.py
|-- requirements.txt
`-- README.md
```

## Project status

TaskFlow is an educational portfolio project. Core project and task management workflows, authentication, user-level data access restrictions, and automated tests are implemented. Production deployment and additional features are ongoing.
