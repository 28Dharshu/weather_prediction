# Modern Auth & Community Platform

A full-stack web application featuring user authentication, photo sharing, interactive likes, live comments, user profiles, and weather/news integrations. Built with a **Python (Flask)** backend, modern **HTML5/CSS3/JavaScript** frontend, and flexible database support for **PostgreSQL** or **MongoDB**.

---

## ✨ Features

- **User Authentication**: Secure Sign-up, Sign-in, and Logout with salted password hashing.
- **Dashboard Feed**: Personalized feed with live local weather and top news headlines.
- **Photo Sharing**: Upload photos with captions, file validation, and live image previews.
- **Social Interactions**: Real-time like toggle and dynamic commenting without page reloads.
- **User Profile & Gallery**: Profile statistics, personal upload gallery, and community showcase.
- **Dual Database Support**: Easily switch between PostgreSQL and MongoDB (with zero-config SQLite fallback for instant local testing).

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask, SQLAlchemy / PyMongo, Werkzeug
- **Frontend**: HTML5, CSS3 (Custom Properties, Flexbox & Grid), Vanilla ES6 JavaScript (Fetch API)
- **Database**: PostgreSQL / MongoDB / SQLite

---

## 🚀 How to Run the Project

### 1. Clone and Navigate to the Directory
```bash
git clone <your-repository-url>
cd python_app
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Demo Data
Run the setup script to create database tables/collections and create a sample demo user:
```bash
python setup_db.py
```

### 4. Start the Application Server
```bash
python app.py
```

Open your browser and visit:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Demo Account

You can log in immediately using the pre-seeded demo credentials:
- **Username:** `demo`
- **Password:** `demo123`

*(Or register a new user directly from the Sign Up page).*

---

## 🗄️ Database Setup (Optional)

The project runs out-of-the-box on SQLite with zero setup required. To connect to PostgreSQL or MongoDB, set the variables in a `.env` file or in `config.py`:

### Option A: PostgreSQL
```env
DB_TYPE=postgres
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
```

### Option B: MongoDB
```env
DB_TYPE=mongodb
MONGO_URI=mongodb://localhost:27017/my_auth_db
MONGO_DB_NAME=my_auth_db
```

---

## 🧪 Running Tests

To verify that all APIs, routes, and database operations are working:
```bash
python test_app.py
```
