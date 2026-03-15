from flask import Blueprint, jsonify, session
from app.models.user import User
from app import db
from datetime import datetime

api_bp = Blueprint("api", __name__, url_prefix="/api")


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


@api_bp.route("/stats")
def get_stats():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    stats = user.stats
    if not stats:
        return jsonify({"syncing": True})

    return jsonify({
        "syncing": False,
        "total_commits": stats.total_commits,
        "total_repos": stats.total_repos,
        "total_stars": stats.total_stars,
        "top_language": stats.top_language,
        "most_active_repo": stats.most_active_repo,
        "peak_coding_hour": stats.peak_coding_hour,
        "peak_coding_day": stats.peak_coding_day,
        "longest_streak": stats.longest_streak,
        "current_streak": stats.current_streak,
        "language_stats": stats.language_stats,
        "commit_heatmap": stats.commit_heatmap,
        "hourly_activity": stats.hourly_activity,
        "weekly_activity": stats.weekly_activity,
        "repo_growth": stats.repo_growth,
        "top_repos": stats.top_repos,
        "last_synced": user.last_synced.isoformat() if user.last_synced else None,
    })


@api_bp.route("/sync", methods=["POST"])
def trigger_sync():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    import threading
    from flask import current_app
    from app.services.sync import sync_user

    app = current_app._get_current_object()

    def _sync():
        with app.app_context():
            sync_user(user.id)

    t = threading.Thread(target=_sync)
    t.daemon = True
    t.start()

    return jsonify({"message": "Sync started"})


@api_bp.route("/status")
def sync_status():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    stats = user.stats
    return jsonify({
        "synced": stats is not None and user.last_synced is not None,
        "last_synced": user.last_synced.isoformat() if user.last_synced else None,
    })
