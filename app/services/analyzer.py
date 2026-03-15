from datetime import datetime, timedelta
from collections import defaultdict


def analyze_user_data(repos, all_commits, language_data):
    """
    Given repos list, flat list of commit objects, and language_data dict,
    return a clean stats dictionary ready for storage and frontend use.
    """
    stats = {}

    # --- Basic counts ---
    stats["total_repos"] = len(repos)
    stats["total_stars"] = sum(r.get("stargazers_count", 0) for r in repos)
    stats["total_commits"] = len(all_commits)

    # --- Language breakdown ---
    lang_bytes = defaultdict(int)
    for lang, data in language_data.items():
        if isinstance(data, dict):
            for l, b in data.items():
                lang_bytes[l] += b
        else:
            lang_bytes[lang] += data

    total_bytes = sum(lang_bytes.values()) or 1
    language_stats = {
        lang: round((b / total_bytes) * 100, 1)
        for lang, b in sorted(lang_bytes.items(), key=lambda x: -x[1])
    }
    stats["language_stats"] = language_stats
    stats["top_language"] = list(language_stats.keys())[0] if language_stats else "Unknown"

    # --- Most active repo ---
    repo_commit_counts = defaultdict(int)
    for c in all_commits:
        repo_name = c.get("_repo", "unknown")
        repo_commit_counts[repo_name] += 1
    if repo_commit_counts:
        stats["most_active_repo"] = max(repo_commit_counts, key=repo_commit_counts.get)
    else:
        stats["most_active_repo"] = "N/A"

    # --- Top repos by commit count ---
    top_repos = sorted(
        [{"name": k, "commits": v} for k, v in repo_commit_counts.items()],
        key=lambda x: -x["commits"],
    )[:5]
    stats["top_repos"] = top_repos

    # --- Commit heatmap (date → count for last 365 days) ---
    today = datetime.utcnow().date()
    start_date = today - timedelta(days=364)
    heatmap = defaultdict(int)

    hourly = defaultdict(int)
    weekly = defaultdict(int)
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for c in all_commits:
        try:
            raw = (
                c.get("commit", {})
                .get("author", {})
                .get("date", "")
            )
            if not raw:
                continue
            dt = datetime.strptime(raw[:19], "%Y-%m-%dT%H:%M:%S")
            d = dt.date()
            if d >= start_date:
                heatmap[str(d)] += 1
            hourly[dt.hour] += 1
            weekly[days_of_week[dt.weekday()]] += 1
        except Exception:
            continue

    stats["commit_heatmap"] = dict(heatmap)
    stats["hourly_activity"] = {str(h): hourly[h] for h in range(24)}
    stats["weekly_activity"] = {day: weekly[day] for day in days_of_week}

    # --- Peak hour and day ---
    if hourly:
        stats["peak_coding_hour"] = max(hourly, key=hourly.get)
    else:
        stats["peak_coding_hour"] = 0

    if weekly:
        stats["peak_coding_day"] = max(weekly, key=weekly.get)
    else:
        stats["peak_coding_day"] = "Monday"

    # --- Repo growth (repos created per month) ---
    repo_growth = defaultdict(int)
    for r in repos:
        created = r.get("created_at", "")
        if created:
            try:
                month = created[:7]  # "YYYY-MM"
                repo_growth[month] += 1
            except Exception:
                pass
    stats["repo_growth"] = dict(sorted(repo_growth.items()))

    # --- Streak calculation ---
    sorted_dates = sorted(heatmap.keys())
    longest_streak = 0
    current_streak = 0
    prev_date = None

    for date_str in sorted_dates:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        if prev_date and (d - prev_date).days == 1:
            current_streak += 1
        else:
            current_streak = 1
        longest_streak = max(longest_streak, current_streak)
        prev_date = d

    # current streak (from today backwards)
    current = 0
    check = today
    while str(check) in heatmap:
        current += 1
        check -= timedelta(days=1)

    stats["longest_streak"] = longest_streak
    stats["current_streak"] = current

    return stats
