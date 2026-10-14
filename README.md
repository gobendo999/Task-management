# TaskFlow — Modern Production-Ready Django Task Management System

TaskFlow is a production-grade, secure, and beautifully designed Task Management web application built with **Django 5**, **Django REST Framework**, **Tailwind CSS**, and **PostgreSQL / MySQL / SQLite**.

---

## ✨ Production & Security Features

- **Disciplined Design System:** Clean **Indigo + Slate** theme with persistent Dark/Light mode toggle (`localStorage` & system preference support).
- **Strict User Isolation:** Complete multi-tenant privacy. Tasks and profiles are strictly scoped to the authenticated user.
- **Enhanced Authentication & Security:**
  - Password show/hide visibility toggles on both Login and Registration forms.
  - Strict valid email requirement (valid RFC format + active domain + unique constraint).
  - Open Redirect vulnerability protection on all authentication flows.
  - Secure CSRF-protected POST logout.
  - "Remember Me" session management (2-week persistent sessions vs browser session).
  - State-modifying endpoints protected with `@require_POST`.
  - Production security headers: XSS protection, MIME sniffing protection, Clickjacking frame-options.
- **Full Password Reset Flow:**
  - Complete email-based self-service password recovery workflow (request, token generation, confirmation, and complete views).
  - Pre-configured console backend for local development, easily switchable to SMTP/SendGrid/SES in production.
- **Scalable Performance:**
  - Database composite indexes on `('user', '-created_at')` and `('user', 'completed')` for fast querying.
  - Server-side pagination (8 tasks per page on web, 10 tasks per page on API) with query-preserving navigation controls.
  - Connection pooling with `conn_max_age=600` via `dj-database-url`.
- **RESTful API & Swagger / OpenAPI 3.0 Documentation:**
  - Interactive Swagger testing interface at `/swagger/` and `/api/docs/`.
  - Multi-method authentication support: Token Authentication, Session Authentication, and Basic Authentication.
  - Built-in API rate limiting & throttling (120 req/day for anonymous, 1000 req/day for authenticated users).
  - Token endpoint `/api/auth/token/` for mobile (Flutter/React Native/iOS/Android) and SPA integration.
- **12-Factor Cloud Deployment:**
  - Zero hardcoded secrets; fully configurable via environment variables (`.env`).
  - Production-ready WhiteNoise static file caching and compression (`CompressedStaticFilesStorage`).
  - `Procfile` included for instant deployment on Render, Railway, Fly.io, or Heroku.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, Django 5.2, Django REST Framework, drf-spectacular
- **Database:** PostgreSQL (Supabase / Neon / AWS RDS), MySQL, or SQLite
- **Static Asset Serving:** WhiteNoise 6.12
- **WSGI Server:** Gunicorn
- **Frontend:** Tailwind CSS (Indigo + Slate), FontAwesome 6, Vanilla JS

---

## 🚀 Local Setup Guide

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Environment Configuration
Copy `.env.example` to create your `.env` file:
```bash
cp .env.example .env
```
Configure your environment variables inside `.env`:
```env
SECRET_KEY=your-secure-random-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,0.0.0.0

# Database Option 1: SQLite (Instant testing)
DB_ENGINE=django.db.backends.sqlite3

# Database Option 2: Cloud PostgreSQL / Supabase
# DATABASE_URL=postgresql://user:password@host:5432/dbname

# Database Option 3: Local MySQL
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=todo_app
# DB_USER=root
# DB_PASSWORD=your_password
# DB_HOST=localhost
# DB_PORT=3306
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Database Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (Optional, for Django Admin)
```bash
python manage.py createsuperuser
```

### 6. Collect Static Assets
```bash
python manage.py collectstatic --noinput
```

### 7. Run Test Suite
```bash
python manage.py test
```

### 8. Start Development Server
```bash
python manage.py runserver
```
Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 📖 API Documentation & Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register new user & obtain token | No |
| `POST` | `/api/auth/login/` | Sign in & receive session + token | No |
| `POST` | `/api/auth/token/` | Obtain auth token by credentials | No |
| `POST` | `/api/auth/logout/` | Invalidate session & revoke token | Yes |
| `GET` | `/api/auth/user/` | Current user profile & task metrics | Yes |
| `GET` | `/api/tasks/` | List user tasks (supports `?q=` and `?status=`) | Yes |
| `POST` | `/api/tasks/` | Create new task | Yes |
| `GET` | `/api/tasks/{id}/` | Get task details | Yes |
| `PUT` / `PATCH` | `/api/tasks/{id}/` | Update task | Yes |
| `DELETE` | `/api/tasks/{id}/` | Delete task | Yes |
| `POST` | `/api/tasks/{id}/toggle/` | Toggle task completed status | Yes |

### Interactive Swagger Docs:
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`
- OpenAPI Schema: `http://127.0.0.1:8000/api/schema/`

---

## 🌐 Cloud Deployment (Render / Railway / VPS)

### Render / Railway Quick Setup:
1. Push your repository to GitHub.
2. In Render or Railway, create a **Web Service** connected to your repository.
3. Set the **Build Command**:
   ```bash
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```
4. Set the **Start Command**:
   ```bash
   gunicorn todo_project.wsgi:application
   ```
5. Add the following **Environment Variables**:
   - `SECRET_KEY`: *Generate a strong 50-character random string*
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `your-app-name.onrender.com,your-app-name.up.railway.app`
   - `CSRF_TRUSTED_ORIGINS`: `https://your-app-name.onrender.com,https://your-app-name.up.railway.app`
   - `DATABASE_URL`: `postgresql://user:password@host:port/dbname` *(from Supabase, Neon, or Render PostgreSQL)*
