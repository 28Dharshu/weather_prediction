import os
import time
import requests
from pathlib import Path
from flask import (
    Flask, render_template, request, jsonify, session,
    redirect, url_for, send_from_directory, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from models_sql import db
from db_service import get_db_service

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
os.makedirs(app.instance_path, exist_ok=True)

# Initialize Database
db_service = None
if app.config["DB_TYPE"] != "mongodb":
    db.init_app(app)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"[Warning] SQL create_all error: {e}")
    db_service = get_db_service(app)
else:
    try:
        db_service = get_db_service(app)
    except Exception as e:
        print(f"[Warning] MongoDB initialization error: {e}")
        # Fall back to SQL service if MongoDB is unavailable
        db.init_app(app)
        with app.app_context():
            db.create_all()
        from db_service import SQLService
        db_service = SQLService


def get_current_user():
    """Helper to get currently logged-in user dictionary."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    user = db_service.get_user_by_id(user_id)
    if not user:
        session.clear()
        return None
    if hasattr(user, "to_dict"):
        return user.to_dict()
    return user


def login_required(func):
    """Decorator to protect API routes."""
    from functools import wraps
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"success": False, "error": "Unauthorized. Please log in."}), 401
        return func(*args, **kwargs)
    return decorated_view


# -------------------------------------------------------------
# Frontend Page Routes (HTML)
# -------------------------------------------------------------

@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return redirect(url_for("dashboard_page"))

@app.route("/login")
def login_page():
    if session.get("user_id"):
        return redirect(url_for("dashboard_page"))
    return render_template("login.html")

@app.route("/register")
def register_page():
    if session.get("user_id"):
        return redirect(url_for("dashboard_page"))
    return render_template("register.html")

@app.route("/dashboard")
def dashboard_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")

@app.route("/profile")
def profile_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("profile.html")

@app.route("/gallery")
def gallery_page():
    if not session.get("user_id"):
        return redirect(url_for("login_page"))
    return render_template("gallery.html")

@app.route("/logout")
def logout_page():
    session.clear()
    return redirect(url_for("login_page"))


# -------------------------------------------------------------
# File Serving Route
# -------------------------------------------------------------

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# -------------------------------------------------------------
# RESTful API Endpoints (JSON / Multipart)
# -------------------------------------------------------------

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""
    location = (data.get("location") or "").strip()

    # Validations replicating PHP logic
    errors = {}
    if not username:
        errors["username"] = "Please enter a username."
    elif len(username) < 3:
        errors["username"] = "Username must have at least 3 characters."
    elif db_service.get_user_by_username(username):
        errors["username"] = "This username is already taken."

    if not email:
        errors["email"] = "Please enter an email."
    elif "@" not in email:
        errors["email"] = "Please enter a valid email address."
    elif db_service.get_user_by_email(email):
        errors["email"] = "This email is already registered."

    if not password:
        errors["password"] = "Please enter a password."
    elif len(password) < 6:
        errors["password"] = "Password must have at least 6 characters."

    if not confirm_password:
        errors["confirm_password"] = "Please confirm password."
    elif password != confirm_password:
        errors["confirm_password"] = "Passwords did not match."

    if not location:
        errors["location"] = "Please enter your location."

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    hashed_pw = generate_password_hash(password)
    user = db_service.create_user(
        username=username,
        email=email,
        password_hash=hashed_pw,
        location=location
    )

    return jsonify({
        "success": True,
        "message": "Account created successfully! Please log in."
    }), 201


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or request.form
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    errors = {}
    if not username:
        errors["username"] = "Please enter your username."
    if not password:
        errors["password"] = "Please enter your password."

    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    user = db_service.get_user_by_username(username)
    if not user:
        return jsonify({"success": False, "errors": {"username": "No account found with that username."}}), 400

    pw_hash = user.password_hash if hasattr(user, "password_hash") else user.get("password_hash")
    if not check_password_hash(pw_hash, password):
        return jsonify({"success": False, "errors": {"password": "Invalid password."}}), 400

    user_id = user.id if hasattr(user, "id") else user.get("id")
    username_val = user.username if hasattr(user, "username") else user.get("username")
    
    # Set Flask session
    session.clear()
    session["user_id"] = str(user_id)
    session["username"] = username_val

    return jsonify({
        "success": True,
        "message": "Login successful!",
        "user": {
            "id": str(user_id),
            "username": username_val
        }
    })


@app.route("/api/auth/logout", methods=["POST", "GET"])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully."})


@app.route("/api/auth/me", methods=["GET"])
def api_me():
    user = get_current_user()
    if not user:
        return jsonify({"logged_in": False, "user": None}), 401
    return jsonify({"logged_in": True, "user": user})


@app.route("/api/profile", methods=["GET"])
@login_required
def api_profile():
    user = get_current_user()
    stats = db_service.get_user_stats(session["user_id"])
    posts = db_service.get_posts(user_id=session["user_id"], current_user_id=session["user_id"])
    return jsonify({
        "success": True,
        "user": user,
        "stats": stats,
        "posts": posts
    })


# -------------------------------------------------------------
# Posts, Likes, Comments APIs
# -------------------------------------------------------------

@app.route("/api/posts", methods=["GET"])
@login_required
def api_get_posts():
    user_id_param = request.args.get("user_id")
    current_uid = session.get("user_id")
    posts = db_service.get_posts(user_id=user_id_param, current_user_id=current_uid)
    return jsonify({"success": True, "posts": posts})


@app.route("/api/posts", methods=["POST"])
@login_required
def api_create_post():
    if "post_image" not in request.files:
        return jsonify({"success": False, "error": "No image file provided."}), 400

    file = request.files["post_image"]
    if file.filename == "":
        return jsonify({"success": False, "error": "No selected file."}), 400

    caption = request.form.get("caption", "").strip()

    # Validate extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in app.config["ALLOWED_EXTENSIONS"]:
        return jsonify({"success": False, "error": "Invalid file type. Only JPG, JPEG, PNG & GIF are allowed."}), 400

    # Generate secure unique filename
    orig_name = secure_filename(file.filename)
    filename = f"{int(time.time())}_{orig_name}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    # Relative web path (uploads/filename)
    rel_path = f"uploads/{filename}"

    post = db_service.create_post(
        user_id=session["user_id"],
        image_path=rel_path,
        caption=caption
    )

    return jsonify({"success": True, "message": "Post created successfully!", "post": post}), 201


@app.route("/api/posts/<post_id>", methods=["DELETE"])
@login_required
def api_delete_post(post_id):
    success, result = db_service.delete_post(post_id=post_id, user_id=session["user_id"])
    if not success:
        return jsonify({"success": False, "error": result}), 400

    # Delete local image file if exists
    try:
        image_filename = os.path.basename(result)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"[Warning] Failed to delete image file: {e}")

    return jsonify({"success": True, "message": "Post deleted successfully."})


@app.route("/api/posts/<post_id>/like", methods=["POST"])
@login_required
def api_like_post(post_id):
    res = db_service.toggle_like(user_id=session["user_id"], post_id=post_id)
    return jsonify({"success": True, **res})


@app.route("/api/posts/<post_id>/comments", methods=["GET"])
@login_required
def api_get_comments(post_id):
    comments = db_service.get_comments(post_id)
    return jsonify({"success": True, "comments": comments})


@app.route("/api/posts/<post_id>/comments", methods=["POST"])
@login_required
def api_add_comment(post_id):
    data = request.get_json(silent=True) or request.form
    comment_text = (data.get("comment_text") or "").strip()

    if not comment_text:
        return jsonify({"success": False, "error": "Comment cannot be empty."}), 400

    comment = db_service.add_comment(
        user_id=session["user_id"],
        post_id=post_id,
        comment_text=comment_text
    )
    return jsonify({"success": True, "comment": comment}), 201


# -------------------------------------------------------------
# Weather and News APIs (Replicating welcome.php)
# -------------------------------------------------------------

@app.route("/api/weather", methods=["GET"])
@login_required
def api_weather():
    user = get_current_user()
    location = user.get("location") if user else None
    if not location:
        return jsonify({"success": False, "error": "User location not set."}), 400

    api_key = app.config["OPENWEATHER_API_KEY"]
    try:
        # Current weather
        curr_url = f"https://api.openweathermap.org/data/2.5/weather?q={requests.utils.quote(location)}&appid={api_key}&units=metric"
        curr_res = requests.get(curr_url, timeout=5)
        current_data = curr_res.json() if curr_res.status_code == 200 else None

        # Forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={requests.utils.quote(location)}&appid={api_key}&units=metric"
        forecast_res = requests.get(forecast_url, timeout=5)
        forecast_list = []
        if forecast_res.status_code == 200:
            forecast_data = forecast_res.json()
            forecast_list = forecast_data.get("list", [])[:2]

        return jsonify({
            "success": True,
            "current": current_data,
            "forecast": forecast_list,
            "location": location
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Weather API error: {str(e)}"}), 502


@app.route("/api/news", methods=["GET"])
@login_required
def api_news():
    api_key = app.config["GNEWS_API_KEY"]
    try:
        url = f"https://gnews.io/api/v4/top-headlines?token={api_key}&lang=en"
        res = requests.get(url, timeout=5)
        articles = []
        if res.status_code == 200:
            articles = res.json().get("articles", [])[:5]
        return jsonify({"success": True, "articles": articles})
    except Exception as e:
        return jsonify({"success": False, "error": f"News API error: {str(e)}"}), 502


if __name__ == "__main__":
    port = int(os.environ.get("APP_PORT", 5000))
    print(f"Starting Python Server at http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
