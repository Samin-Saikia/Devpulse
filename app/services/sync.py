from app import db
from app.models.user import User
from app.models.stats import UserStats
from app.services.github import GitHubService
from app.services.analyzer import analyze_user_data
from datetime import datetime
from flask import current_app


def sync_user(user_id: int):
    """
    Full sync: fetch GitHub data, run analyzer, save to DB.
    Safe to call from background scheduler or route handler.
    """
    user = User.query.get(user_id)
    if not user:
        return False

    current_app.logger.info(f"Syncing user: {user.username}")

    gh = GitHubService(user.access_token)

    # Fetch repos (excluding forks)
    repos = gh.get_repos(user.username)
    if repos is None:
        repos = []

    # Fetch commits and languages for each repo
    all_commits = []
    all_languages = {}

    for repo in repos:
        repo_name = repo.get("name")
        owner = repo.get("owner", {}).get("login", user.username)

        commits = gh.get_commits(owner, repo_name, author=user.username)
        for c in commits:
            c["_repo"] = repo_name
        all_commits.extend(commits)

        langs = gh.get_languages(owner, repo_name)
        if langs:
            all_languages[repo_name] = langs

    # Run analytics
    stats_dict = analyze_user_data(repos, all_commits, all_languages)

    # Upsert UserStats
    stats = user.stats
    if not stats:
        stats = UserStats(user_id=user.id)
        db.session.add(stats)

    stats.total_commits = stats_dict["total_commits"]
    stats.total_repos = stats_dict["total_repos"]
    stats.total_stars = stats_dict["total_stars"]
    stats.top_language = stats_dict["top_language"]
    stats.most_active_repo = stats_dict["most_active_repo"]
    stats.peak_coding_hour = stats_dict["peak_coding_hour"]
    stats.peak_coding_day = stats_dict["peak_coding_day"]
    stats.longest_streak = stats_dict["longest_streak"]
    stats.current_streak = stats_dict["current_streak"]
    stats.language_stats = stats_dict["language_stats"]
    stats.commit_heatmap = stats_dict["commit_heatmap"]
    stats.hourly_activity = stats_dict["hourly_activity"]
    stats.weekly_activity = stats_dict["weekly_activity"]
    stats.repo_growth = stats_dict["repo_growth"]
    stats.top_repos = stats_dict["top_repos"]
    stats.updated_at = datetime.utcnow()

    user.last_synced = datetime.utcnow()

    db.session.commit()
    current_app.logger.info(f"Sync complete for {user.username}: {len(all_commits)} commits, {len(repos)} repos")
    return True
