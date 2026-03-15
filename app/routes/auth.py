from flask import Blueprint, redirect, request, session, url_for, current_app
from app import db
from app.models.user import User
from app.services.github import GitHubService
import threading

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login")
def login():
    cfg = current_app.config
    callback_url = cfg["APP_URL"] + url_for("auth.callback")
    github_auth_url = (
        f"{cfg['GITHUB_AUTHORIZE_URL']}"
        f"?client_id={cfg['GITHUB_CLIENT_ID']}"
        f"&redirect_uri={callback_url}"
        f"&scope=read:user,repo"
    )
    return redirect(github_auth_url)


@auth_bp.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return redirect(url_for("dashboard.index"))

    gh_temp = GitHubService(token=None)
    token = gh_temp.exchange_code_for_token(code)
    if not token:
        return redirect(url_for("dashboard.index"))

    gh = GitHubService(token)
    gh_user = gh.get_authenticated_user()
    if not gh_user:
        return redirect(url_for("dashboard.index"))

    # Upsert user
    user = User.query.filter_by(github_id=gh_user["id"]).first()
    if not user:
        user = User(github_id=gh_user["id"])
        db.session.add(user)

    user.username = gh_user.get("login", "")
    user.display_name = gh_user.get("name") or gh_user.get("login", "")
    user.avatar_url = gh_user.get("avatar_url", "")
    user.access_token = token
    user.public_repos = gh_user.get("public_repos", 0)
    user.followers = gh_user.get("followers", 0)
    user.following = gh_user.get("following", 0)
    user.github_created_at = gh_user.get("created_at", "")
    db.session.commit()

    session["user_id"] = user.id

    # Trigger background sync
    from app.services.sync import sync_user
    app = current_app._get_current_object()
    t = threading.Thread(target=_bg_sync, args=(app, user.id))
    t.daemon = True
    t.start()

    return redirect(url_for("dashboard.dashboard"))


def _bg_sync(app, user_id):
    with app.app_context():
        from app.services.sync import sync_user
        try:
            sync_user(user_id)
        except Exception as e:
            app.logger.error(f"Background sync error: {e}")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("dashboard.index"))
