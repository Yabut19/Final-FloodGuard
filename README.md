# FloodGuard (Full Stack)

This project consists of a Flask backend, a React Native Web Admin Dashboard, and a React Native Mobile App.

## Prerequisites
- **XAMPP** (or any MySQL server)
- **Python 3.x**
- **Node.js** & **npm**

---

## 1. Database Setup
1. Start **Apache** and **MySQL** in XAMPP.
2. Open **phpMyAdmin** (`http://localhost/phpmyadmin`).
3. Create a new database named `floodguard`.
4. Import the schema file located at: `backend_flask/db_schema.sql`.
   - This script creates necessary tables and default admin accounts.

**Default Credentials:**
- **Super Admin:** `admin@system.com` / `admin123`
- **LGU Moderator:** `moderator@lgu.gov` / `password123`

---

## 2. Backend (Flask)
The backend handles API requests and database interactions.

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend_flask
   ```
2. Install Python dependencies (optional, if not installed):
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Flask application:
   ```bash
   python app.py
   ```
   - The server will start at `http://localhost:5000` (or `0.0.0.0:5000`).

---

## 3. Web Admin Dashboard
The web dashboard is for administrators to monitor sensors and manage alerts.

1. Open a **new** terminal and navigate to the web-admin directory:
   ```bash
   cd frontend/admin/web-admin
   ```
2. Install dependencies (first time only):
   ```bash
   npm install
   ```
3. Run the web app:
   ```bash
   npm run web
   ```
   - This will open the dashboard in your default browser (usually `http://localhost:8081`).

---

## 4. Mobile App
The mobile app is for users to report incidents and receive alerts.

1. Open a **new** terminal and navigate to the mobile directory:
   ```bash
   cd frontend/mobile
   ```
2. Install dependencies (first time only):
   ```bash
   npm install
   ```
3. Run the mobile app:
   ```bash
   npm run start
   ```
   - Use the **Expo Go** app on your phone to scan the QR code, or press `a` to run on an Android emulator / `w` for web preview.

---

## Troubleshooting
- **Database Connection Error:** Check `backend_flask/config.py` and ensure `DB_USER` and `DB_PASSWORD` match your XAMPP settings (default is usually `root` and empty password).
- **CORS Issues:** The backend is configured to allow CORS, but ensure you are accessing the frontend via `localhost` or the correct network IP if testing on a physical device.
