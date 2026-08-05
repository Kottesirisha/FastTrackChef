# FastTrackChef

A full-stack Flask food ordering web application with customer and admin portals, database-backed shopping cart, order management, and REST API.

## Features

### Customer
- Register, login, logout with BCrypt password hashing
- Browse menu with search, category filter, and sort (price, popularity)
- View food details and add items to cart
- Database-persisted cart (add, update quantity, remove)
- Checkout and place orders
- View order history and track status
- Manage profile and change password

### Admin
- Secure role-based admin dashboard with statistics
- CRUD for food items with image upload
- Category management
- Customer management
- Order management with status updates (Pending, Preparing, Delivered)

### REST API
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/foods` | List foods (search, filter, sort) |
| POST | `/api/foods` | Add food (admin) |
| GET | `/api/foods/<id>` | Get food by ID |
| PUT | `/api/foods/<id>` | Update food (admin) |
| DELETE | `/api/foods/<id>` | Delete food (admin) |
| GET | `/api/categories` | List categories |
| GET | `/api/orders` | List orders (admin: all, customer: own) |

## Tech Stack

- **Backend:** Python 3.12+, Flask, SQLAlchemy, Flask-Login, Flask-WTF, Flask-Bcrypt, Flask-Migrate, Flask-RESTful
- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Database:** MySQL 8.0+

## Setup

### 1. Prerequisites
- Python 3.12+
- MySQL 8.0+
- Git

### 2. Clone & Install

```bash
cd FastTrackChef
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Configure Database

Create the MySQL database:

```bash
mysql -u root -p < database.sql
```

Update `.env` with your MySQL credentials:

```
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/fasttrackchef
SECRET_KEY=your-random-secret-key
```

**SQLite fallback (local testing only):**

```
DATABASE_URL=sqlite:///instance/fasttrackchef.db
```

### 4. Initialize & Seed

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
python seed_data.py
```

### 5. Run

```bash
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@fasttrackchef.com | Admin@123 |
| Customer | customer@demo.com | Customer@123 |

## Project Structure

```
FastTrackChef/
├── app/
│   ├── __init__.py      # App factory
│   ├── models.py        # Database models
│   ├── auth.py          # Authentication
│   ├── customer.py      # Customer routes
│   ├── admin.py         # Admin routes
│   ├── api.py           # REST API
│   ├── forms.py         # WTForms validation
│   ├── config.py        # Configuration
│   ├── utils.py         # Helpers
│   ├── templates/       # HTML templates
│   └── static/          # CSS, JS, uploads
├── migrations/
├── tests/
├── database.sql
├── seed_data.py
├── requirements.txt
└── run.py
```

## Security

- BCrypt password hashing
- CSRF protection (Flask-WTF)
- SQL injection prevention (SQLAlchemy ORM)
- Role-based access control
- Session timeout (2 hours)
- Input validation on all forms
- Secure file upload validation

## API Testing (Postman)

```
GET  http://127.0.0.1:5000/api/foods
GET  http://127.0.0.1:5000/api/foods?q=pizza&sort=price_asc
GET  http://127.0.0.1:5000/api/categories
```

For POST/PUT/DELETE, login as admin in the browser first (session cookie required).

## License

MIT — Built as a resume-worthy full-stack student project.
