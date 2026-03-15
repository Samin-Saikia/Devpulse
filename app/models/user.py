from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    github_id = db.Column(db.Integer, unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(200))
    avatar_url = db.Column(db.String(500))
    access_token = db.Column(db.String(500), nullable=False)
    public_repos = db.Column(db.Integer, default=0)
    followers = db.Column(db.Integer, default=0)
    following = db.Column(db.Integer, default=0)
    github_created_at = db.Column(db.String(50))
    last_synced = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    stats = db.relationship("UserStats", backref="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"
