
# 📱 Django Phone & OTP Authentication API

A simple and secure authentication system built with Django REST Framework using **phone numbers**, **OTP verification**, and **JWT tokens**.

---

## 🚀 Features

- Phone number-based login and registration
- OTP (One-Time Password) verification with rate limiting
- Registration token system to complete user profile after OTP verification
- User registration with password and personal details
- JWT-based authentication for secure token handling
- Blocking mechanism after multiple failed attempts (login or OTP)

---

## 📦 Installation

1. **Clone the repository:**

```bash
git clone https://github.com/your_username/your_project.git
cd your_project
```

2. **Create a virtual environment and install requirements:**

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Apply database migrations:**

```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Run the server:**

```bash
python manage.py runserver
```

---

## 🔐 API Endpoints

| Method | Endpoint               | Description                                 |
|--------|------------------------|---------------------------------------------|
| POST   | `/auth/check-phone/`   | Check if phone exists, send OTP if not      |
| POST   | `/auth/verify/`        | Verify OTP and receive a registration token |
| POST   | `/auth/register/`      | Complete registration using the token       |
| POST   | `/auth/login/`         | Login with phone and password               |

---

## 📮 Usage Examples

### 1. Check Phone & Send OTP

```http
POST /auth/check-phone/
```

```json
{
  "phone": "09101234567"
}
```

---

### 2. Verify OTP and Receive Registration Token

```http
POST /auth/verify/
```

```json
{
  "phone": "09101234567",
  "code": "1234"
}
```

✅ Response:

```json
{
  "message": "Phone verified.",
  "registration_token": "fef8702768384d1d88a2e1454e6c749c"
}
```

---

### 3. Complete Registration

```http
POST /auth/register/
```

```json
{
  "reg_token": "fef8702768384d1d88a2e1454e6c749c",
  "password": "123456789",
  "first_name": "Majed",
  "last_name": "Shabani",
  "email": "majedwp12@gmail.com"
}
```

---

### 4. Login with Phone and Password

```http
POST /auth/login/
```

```json
{
  "phone": "09101234567",
  "password": "123456789"
}
```

---

## 🧠 Tech Stack

- Python 3.11+
- Django 4.x
- Django REST Framework
- Redis (for caching OTPs and tokens)
- JWT (for authentication tokens)

---

## ⚠ Notes

- Don't forget to configure your `CACHES` settings for production (e.g., Redis).
- All APIs expect a `/` at the end of the URL (e.g., `/auth/register/`). Make sure `APPEND_SLASH=True` is set.
- OTP and login attempt limits are IP-based and expire after a short time.
- OTPs and registration tokens are time-limited (default: 10 minutes).

---

## 📧 Contact

Feel free to reach out if you have any questions. Contributions and suggestions are welcome!

---
