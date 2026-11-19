# Deployment Guide: Modern Auth & Community Platform

This guide covers step-by-step instructions for deploying this application to production.

---

## Option 1: Free Cloud Deployment on Render.com (Recommended)

Render offers free hosting for Python web services and managed PostgreSQL databases connected directly to your GitHub repository.

### Step 1: Push Project to GitHub
1. Create a new repository on GitHub (e.g. `modern-auth-system`).
2. In your terminal inside `python_app`:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of full-stack Python PostgreSQL app"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

### Step 2: Create a PostgreSQL Database on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **PostgreSQL**.
2. Fill in:
   - **Name**: `auth-database`
   - **Database**: `my_auth_db`
   - **User**: `postgres`
   - **Region**: Choose the closest region to you.
   - **Plan**: Free
3. Click **Create Database**.
4. After creation, copy the **Internal Database URL** (e.g., `postgresql://postgres:...@.../my_auth_db`).

### Step 3: Deploy the Python Web Service
1. In the Render Dashboard, click **New +** -> **Web Service**.
2. Select your GitHub repository.
3. Configure the service:
   - **Name**: `modern-auth-app`
   - **Environment**: `Python 3`
   - **Region**: Same region as your database.
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
4. Under **Environment Variables**, add:
   - `DB_TYPE` = `postgres`
   - `DATABASE_URL` = *(Paste the Internal Database URL from Step 2)*
   - `SECRET_KEY` = *(Enter any long random string)*
   - `OPENWEATHER_API_KEY` = `your_openweather_api_key_here`
   - `GNEWS_API_KEY` = `your_gnews_api_key_here`
5. Click **Deploy Web Service**.

Render will automatically install dependencies, initialize PostgreSQL tables, and provide you with a live HTTPS URL (e.g., `https://modern-auth-app.onrender.com`).

---

## Option 2: Deploy with Docker Compose (Local or any VPS)

If you have Docker installed on your machine or an Ubuntu/Debian cloud server (AWS, DigitalOcean, Linode):

### 1. Start Database and Web Application
Run one command:
```bash
docker compose up --build -d
```

### 2. View Status and Logs
```bash
docker compose ps
docker compose logs -f web
```

### 3. Access Application
Open your browser at:
👉 **http://localhost:5000**

To stop the containers:
```bash
docker compose down
```

---

## Option 3: Deploy on Railway.app

1. Go to [Railway.app](https://railway.app/) and sign in with GitHub.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select this repository.
4. Add a **PostgreSQL database** service in Railway by clicking **New** -> **Database** -> **Add PostgreSQL**.
5. In your web service settings, add the variable:
   - `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
   - `DB_TYPE` = `postgres`
   - `SECRET_KEY` = `some-random-secret`
6. Railway will automatically build the `Dockerfile` or `Procfile` and deploy your app.
