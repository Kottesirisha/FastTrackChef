# FastTrackChef 🍽️

A full-stack Flask food ordering web application with customer and admin portals, database-backed shopping cart, order management, and REST API.

## 🚀 Live Demo

**Application:** https://fasttrackchef-1.onrender.com

**GitHub Repository:** https://github.com/naren2023/FastTrackChef

--

## ✨ Features

### 👤 Customer

- Register, Login & Logout with BCrypt password hashing
- Browse menu with search, category filter, and sorting
- View food details
- Add, update and remove items from cart
- Database-backed shopping cart
- Checkout and place orders
- View order history
- Track order status
- Manage profile
- Change password

### 👨‍💼 Admin

- Secure role-based admin dashboard
- Food management (CRUD)
- Image upload support
- Category management
- Customer management
- Order management
- Update order status (Pending, Preparing, Delivered)

---

## 🌐 REST API

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/foods` | List foods |
| POST | `/api/foods` | Add food (Admin) |
| GET | `/api/foods/<id>` | Get food details |
| PUT | `/api/foods/<id>` | Update food |
| DELETE | `/api/foods/<id>` | Delete food |
| GET | `/api/categories` | List categories |
| GET | `/api/orders` | List orders |

---

## 🛠 Tech Stack

### Backend
- Python 3
- Flask
- SQLAlchemy
- Flask-Login
- Flask-WTF
- Flask-Bcrypt
- Flask-Migrate
- Flask-RESTful

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Database
- SQLite (Render Deployment)
- MySQL (Local Development)

---

## 📦 Installation

```bash
git clone https://github.com/naren2023/FastTrackChef.git
cd FastTrackChef

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

---

## ▶️ Run Locally

```bash
python run.py
```

Open:

```
http://127.0.0.1:5000
```

---

## 👤 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@fasttrackchef.com | Admin@123 |
| Customer | customer@demo.com | Customer@123 |

---

## 📁 Project Structure

```
FastTrackChef/
│
├── app/
├── migrations/
├── tests/
├── requirements.txt
├── run.py
├── wsgi.py
├── seed_data.py
└── database.sql
```

---

## 🔒 Security

- BCrypt Password Hashing
- CSRF Protection
- SQLAlchemy ORM
- Role-Based Access Control
- Secure Session Management
- File Upload Validation
- Input Validation

---

## 🧪 API Testing

```
GET /api/foods

GET /api/foods?q=pizza

GET /api/categories
```

---

## 📄 License

MIT License

---

## 👨‍💻 Author

**Narendra**

GitHub:
https://github.com/naren2023

Project:
https://github.com/naren2023/FastTrackChef

Live Demo:
https://fasttrackchef-1.onrender.com
