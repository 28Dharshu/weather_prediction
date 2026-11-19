"""
Database Service Layer
Provides a unified interface whether using PostgreSQL (via SQLAlchemy)
or MongoDB (via PyMongo).
"""

from datetime import datetime
import os
from models_sql import db, User, Post, Like, Comment

# Optional MongoDB import:
try:
    from pymongo import MongoClient
    from bson import ObjectId
    PYMONGO_AVAILABLE = True
except ImportError:
    MongoClient = None
    ObjectId = None
    PYMONGO_AVAILABLE = False


class SQLService:
    """PostgreSQL and SQLite backend using SQLAlchemy."""

    @staticmethod
    def get_user_by_username(username):
        user = User.query.filter_by(username=username).first()
        return user

    @staticmethod
    def get_user_by_email(email):
        user = User.query.filter_by(email=email).first()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        try:
            return User.query.get(int(user_id))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def create_user(username, email, password_hash, location):
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            location=location
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_posts(user_id=None, current_user_id=None):
        query = Post.query
        if user_id is not None:
            query = query.filter_by(user_id=int(user_id))
        posts = query.order_by(Post.created_at.desc()).all()
        return [p.to_dict(current_user_id=current_user_id) for p in posts]

    @staticmethod
    def get_post_by_id(post_id):
        try:
            return Post.query.get(int(post_id))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def create_post(user_id, image_path, caption=""):
        post = Post(user_id=int(user_id), image_path=image_path, caption=caption)
        db.session.add(post)
        db.session.commit()
        return post.to_dict(current_user_id=user_id)

    @staticmethod
    def delete_post(post_id, user_id):
        post = Post.query.filter_by(id=int(post_id), user_id=int(user_id)).first()
        if not post:
            return False, "Post not found or unauthorized."
        image_path = post.image_path
        db.session.delete(post)
        db.session.commit()
        return True, image_path

    @staticmethod
    def toggle_like(user_id, post_id):
        existing_like = Like.query.filter_by(user_id=int(user_id), post_id=int(post_id)).first()
        if existing_like:
            db.session.delete(existing_like)
            db.session.commit()
            liked = False
        else:
            new_like = Like(user_id=int(user_id), post_id=int(post_id))
            db.session.add(new_like)
            db.session.commit()
            liked = True
        total_likes = Like.query.filter_by(post_id=int(post_id)).count()
        return {"liked": liked, "total_likes": total_likes}

    @staticmethod
    def get_comments(post_id):
        comments = Comment.query.filter_by(post_id=int(post_id)).order_by(Comment.created_at.desc()).all()
        return [c.to_dict() for c in comments]

    @staticmethod
    def add_comment(user_id, post_id, comment_text):
        comment = Comment(
            user_id=int(user_id),
            post_id=int(post_id),
            comment=comment_text.strip()
        )
        db.session.add(comment)
        db.session.commit()
        return comment.to_dict()

    @staticmethod
    def get_user_stats(user_id):
        post_count = Post.query.filter_by(user_id=int(user_id)).count()
        return {
            "posts_count": post_count,
            "followers_count": 0,
            "following_count": 0
        }


class MongoService:
    """MongoDB backend using PyMongo."""
    client = None
    db = None

    @classmethod
    def init_app(cls, app):
        if not PYMONGO_AVAILABLE:
            raise RuntimeError("pymongo is not installed. Run `pip install pymongo` to use MongoDB backend.")
        cls.client = MongoClient(app.config["MONGO_URI"])
        cls.db = cls.client[app.config["MONGO_DB_NAME"]]
        # Create indexes
        cls.db.users.create_index("username", unique=True)
        cls.db.users.create_index("email", unique=True)
        cls.db.posts.create_index([("created_at", -1)])
        cls.db.likes.create_index([("user_id", 1), ("post_id", 1)], unique=True)
        cls.db.comments.create_index([("post_id", 1), ("created_at", -1)])

    @classmethod
    def _user_doc(cls, doc):
        if not doc:
            return None
        doc["id"] = str(doc["_id"])
        return doc

    @classmethod
    def get_user_by_username(cls, username):
        user = cls.db.users.find_one({"username": username})
        return cls._user_doc(user)

    @classmethod
    def get_user_by_email(cls, email):
        user = cls.db.users.find_one({"email": email})
        return cls._user_doc(user)

    @classmethod
    def get_user_by_id(cls, user_id):
        try:
            user = cls.db.users.find_one({"_id": ObjectId(str(user_id))})
            return cls._user_doc(user)
        except Exception:
            return None

    @classmethod
    def create_user(cls, username, email, password_hash, location):
        doc = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "location": location,
            "profile_picture": None,
            "created_at": datetime.utcnow()
        }
        res = cls.db.users.insert_one(doc)
        doc["id"] = str(res.inserted_id)
        return doc

    @classmethod
    def get_posts(cls, user_id=None, current_user_id=None):
        query = {}
        if user_id:
            query["user_id"] = str(user_id)
        cursor = cls.db.posts.find(query).sort("created_at", -1)
        posts = []
        for doc in cursor:
            post_id = str(doc["_id"])
            user = cls.get_user_by_id(doc.get("user_id"))
            username = user["username"] if user else "Unknown"
            like_count = cls.db.likes.count_documents({"post_id": post_id})
            comment_count = cls.db.comments.count_documents({"post_id": post_id})
            liked_by_user = False
            if current_user_id:
                liked_by_user = cls.db.likes.count_documents({
                    "post_id": post_id,
                    "user_id": str(current_user_id)
                }) > 0
            
            created_at = doc.get("created_at")
            posts.append({
                "id": post_id,
                "user_id": doc.get("user_id"),
                "username": username,
                "image_path": doc.get("image_path"),
                "caption": doc.get("caption", ""),
                "like_count": like_count,
                "comment_count": comment_count,
                "liked_by_user": liked_by_user,
                "created_at": created_at.strftime("%B %d, %Y, %I:%M %p") if isinstance(created_at, datetime) else ""
            })
        return posts

    @classmethod
    def get_post_by_id(cls, post_id):
        try:
            return cls.db.posts.find_one({"_id": ObjectId(str(post_id))})
        except Exception:
            return None

    @classmethod
    def create_post(cls, user_id, image_path, caption=""):
        doc = {
            "user_id": str(user_id),
            "image_path": image_path,
            "caption": caption,
            "created_at": datetime.utcnow()
        }
        res = cls.db.posts.insert_one(doc)
        doc["id"] = str(res.inserted_id)
        return doc

    @classmethod
    def delete_post(cls, post_id, user_id):
        try:
            oid = ObjectId(str(post_id))
            post = cls.db.posts.find_one({"_id": oid, "user_id": str(user_id)})
            if not post:
                return False, "Post not found or unauthorized."
            image_path = post.get("image_path")
            cls.db.posts.delete_one({"_id": oid})
            cls.db.likes.delete_many({"post_id": str(post_id)})
            cls.db.comments.delete_many({"post_id": str(post_id)})
            return True, image_path
        except Exception as e:
            return False, str(e)

    @classmethod
    def toggle_like(cls, user_id, post_id):
        uid = str(user_id)
        pid = str(post_id)
        existing = cls.db.likes.find_one({"user_id": uid, "post_id": pid})
        if existing:
            cls.db.likes.delete_one({"_id": existing["_id"]})
            liked = False
        else:
            cls.db.likes.insert_one({
                "user_id": uid,
                "post_id": pid,
                "created_at": datetime.utcnow()
            })
            liked = True
        total_likes = cls.db.likes.count_documents({"post_id": pid})
        return {"liked": liked, "total_likes": total_likes}

    @classmethod
    def get_comments(cls, post_id):
        cursor = cls.db.comments.find({"post_id": str(post_id)}).sort("created_at", -1)
        comments = []
        for doc in cursor:
            user = cls.get_user_by_id(doc.get("user_id"))
            username = user["username"] if user else "Unknown"
            created_at = doc.get("created_at")
            comments.append({
                "id": str(doc["_id"]),
                "user_id": doc.get("user_id"),
                "post_id": str(post_id),
                "username": username,
                "comment": doc.get("comment", ""),
                "created_at": created_at.strftime("%B %d, %Y, %I:%M %p") if isinstance(created_at, datetime) else ""
            })
        return comments

    @classmethod
    def add_comment(cls, user_id, post_id, comment_text):
        doc = {
            "user_id": str(user_id),
            "post_id": str(post_id),
            "comment": comment_text.strip(),
            "created_at": datetime.utcnow()
        }
        res = cls.db.comments.insert_one(doc)
        user = cls.get_user_by_id(user_id)
        username = user["username"] if user else "Unknown"
        return {
            "id": str(res.inserted_id),
            "user_id": str(user_id),
            "post_id": str(post_id),
            "username": username,
            "comment": comment_text.strip(),
            "created_at": datetime.utcnow().strftime("%B %d, %Y, %I:%M %p")
        }

    @classmethod
    def get_user_stats(cls, user_id):
        post_count = cls.db.posts.count_documents({"user_id": str(user_id)})
        return {
            "posts_count": post_count,
            "followers_count": 0,
            "following_count": 0
        }


def get_db_service(app):
    """Factory function returning the active database service (SQL or MongoDB)."""
    db_type = app.config.get("DB_TYPE", "postgres")
    if db_type == "mongodb":
        MongoService.init_app(app)
        return MongoService
    return SQLService
