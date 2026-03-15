from flask import Blueprint, render_template, session, redirect, url_for, current_app
from app.models.user import User

dashboard_bp = Blueprint("dashboard", __name__)


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


@dashboard_bp.route("/")
def index():
    user = get_current_user()
    if user:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("index.html")


@dashboard_bp.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        return redirect(url_for("dashboard.index"))

    stats = user.stats
    syncing = stats is None or user.last_synced is None

    return render_template(
        "dashboard.html",
        user=user,
        stats=stats,
        syncing=syncing,
    )
