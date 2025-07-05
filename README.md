# Expense Tracker API
## Developed by : Ankit Karki
---
## A Django a REST API for expense/income tracking with JWT User authentication.

---

## Table of Contents
- [Features](#-features)
- [Setup](#-setup)
- [Authentication](#-authentication)
- [API Endpoints](#-api-endpoints)
- [Examples](#-examples)
- [Admin Access](#-admin-access)
- [Notes](#-notes)

---

## Features
- JWT authentication (access/refresh tokens)
- Personal expense/income tracking
- Automatic tax calculation (flat amount or percentage)
- Paginated API responses
- User-specific data isolation
- Complete CRUD operations

---

## Setup

### Prerequisites
- Python 3.10+
- PostgreSQL (recommended) or SQLite

### Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/expense-tracker-api.git
   cd expense-tracker-api
   ```

2. Set up virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the server:
   ```bash
   python manage.py runserver
   ```
   Access at: `http://localhost:8000`

---

## Authentication

### Register
**POST** `/api/auth/register/`
```json
{
  "username": "username",
  "email": "user@gmail.com",
  "password": "YourPass123",
  "password2": "YourPass123"
}
```

### Login
**POST** `/api/auth/login/`
```json
{
  "username": "newuser",
  "password": "YourPass123"
}
```
Response:
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci..."
}
```

### Protected Requests
Include in headers:
```
Authorization: Bearer <access_token>
```

---

## API Endpoints

| Endpoint                | Method | Description                     |
|-------------------------|--------|---------------------------------|
| `/api/expenses/`        | GET    | List all records (paginated)    |
| `/api/expenses/`        | POST   | Create new record               |
| `/api/expenses/{id}/`   | GET    | Retrieve single record          |
| `/api/expenses/{id}/`   | PUT    | Update record                   |
| `/api/expenses/{id}/`   | DELETE | Delete record                   |

---

## Examples

### Create Expense
**POST** `/api/expenses/`
```json
{
  "title": "Office Supplies",
  "amount": 45.99,
  "transaction_type": "debit",
  "tax": 5.00,
  "tax_type": "percentage"
}
```

Response (201 Created):
```json
{
  "id": 4,
  "title": "Office Supplies",
  "total_amount": "48.29",
  "created_at": "2025-07-05T14:30:00Z"
}
```

### Paginated List
**GET** `/api/expenses/?page=2&page_size=5`
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/expenses/?page=2&page_size=3",
  "previous": "http://localhost:8000/api/expenses/?page_size=1",
  "results": [

  ]
}
```

---

## Admin Access
1. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```
2. Access admin panel at: `http://localhost:8000/admin`

**Admin privileges:**
- View/edit all users' records
- Manage system settings
- Access detailed analytics

---

## Notes
- **Timezones**: All timestamps in UTC
- **Pagination**: Default 4 items/page (`?page_size` to override)
- **Tax Types**: 
  - `flat`: Fixed amount (e.g., Rs10)
  - `percentage`: Rate (e.g., 10%)

---

## Built With
- Django REST Framework
- SimpleJWT
- PostgreSQL
- Python 3.10
