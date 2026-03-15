from app import db
from datetime import datetime
import json

class UserStats(db.Model):
    __tablename__ = "user_stats"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    total_commits = db.Column(db.Integer, default=0)
    total_repos = db.Column(db.Integer, default=0)
    total_stars = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)

    _language_stats = db.Column("language_stats", db.Text, default="{}")
    _commit_heatmap = db.Column("commit_heatmap", db.Text, default="{}")
    _hourly_activity = db.Column("hourly_activity", db.Text, default="{}")
    _weekly_activity = db.Column("weekly_activity", db.Text, default="{}")
    _repo_growth = db.Column("repo_growth", db.Text, default="{}")
    _top_repos = db.Column("top_repos", db.Text, default="[]")

    top_language = db.Column(db.String(100))
    most_active_repo = db.Column(db.String(200))
    peak_coding_hour = db.Column(db.Integer)
    peak_coding_day = db.Column(db.String(20))

    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def language_stats(self):
        return json.loads(self._language_stats or "{}")

    @language_stats.setter
    def language_stats(self, value):
        self._language_stats = json.dumps(value)

    @property
    def commit_heatmap(self):
        return json.loads(self._commit_heatmap or "{}")

    @commit_heatmap.setter
    def commit_heatmap(self, value):
        self._commit_heatmap = json.dumps(value)

    @property
    def hourly_activity(self):
        return json.loads(self._hourly_activity or "{}")

    @hourly_activity.setter
    def hourly_activity(self, value):
        self._hourly_activity = json.dumps(value)

    @property
    def weekly_activity(self):
        return json.loads(self._weekly_activity or "{}")

    @weekly_activity.setter
    def weekly_activity(self, value):
        self._weekly_activity = json.dumps(value)

    @property
    def repo_growth(self):
        return json.loads(self._repo_growth or "{}")

    @repo_growth.setter
    def repo_growth(self, value):
        self._repo_growth = json.dumps(value)

    @property
    def top_repos(self):
        return json.loads(self._top_repos or "[]")

    @top_repos.setter
    def top_repos(self, value):
        self._top_repos = json.dumps(value)

    def __repr__(self):
        return f"<UserStats user_id={self.user_id}>"
