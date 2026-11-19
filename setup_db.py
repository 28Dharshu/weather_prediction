"""
Database setup and seeder script.
Supports both PostgreSQL / SQLite (via SQLAlchemy) and MongoDB (via PyMongo).
Run: python setup_db.py
"""

import os
from werkzeug.security import generate_password_hash
from app import app, db_service
from models_sql import db, User, Post, Comment, Like

def seed():
    print(f"Initializing database using backend: '{app.config['DB_TYPE']}'...")

    if app.config["DB_TYPE"] != "mongodb":
        with app.app_context():
            db.create_all()
            print("SQL tables verified/created successfully.")

            # Check if demo user already exists
            demo_user = User.query.filter_by(username="demo").first()
            if not demo_user:
                print("Seeding demo user...")
                demo_user = User(
                    username="demo",
                    email="demo@example.com",
                    password_hash=generate_password_hash("demo123"),
                    location="New York"
                )
                db.session.add(demo_user)
                db.session.commit()
                print("Demo user created: username='demo', password='demo123'")

            # Check if sample post exists
            if Post.query.count() == 0 and os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], "cat.jpeg")):
                print("Seeding sample post...")
                post = Post(
                    user_id=demo_user.id,
                    image_path="uploads/cat.jpeg",
                    caption="Welcome to the new Python application! 🐱"
                )
                db.session.add(post)
                db.session.commit()

                comment = Comment(
                    user_id=demo_user.id,
                    post_id=post.id,
                    comment="Hello world! The migration to Python backend is complete!"
                )
                db.session.add(comment)
                db.session.commit()
                print("Sample post and comment created.")

    else:
        # MongoDB Seeding
        from db_service import MongoService
        print("Ensuring MongoDB collections and indexes...")
        demo_user = MongoService.get_user_by_username("demo")
        if not demo_user:
            demo_user = MongoService.create_user(
                username="demo",
                email="demo@example.com",
                password_hash=generate_password_hash("demo123"),
                location="New York"
            )
            print("Demo user created in MongoDB: username='demo', password='demo123'")

        posts = MongoService.get_posts()
        if len(posts) == 0 and os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], "cat.jpeg")):
            p = MongoService.create_post(
                user_id=demo_user["id"],
                image_path="uploads/cat.jpeg",
                caption="Welcome to the new Python application with MongoDB! 🐱"
            )
            MongoService.add_comment(
                user_id=demo_user["id"],
                post_id=p["id"],
                comment_text="Hello world! Running on MongoDB!"
            )
            print("Sample post and comment created in MongoDB.")

    print("\nDatabase setup complete! You can start the server with: python app.py")

if __name__ == "__main__":
    seed()
