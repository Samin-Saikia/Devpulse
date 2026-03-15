import requests
from flask import current_app
from datetime import datetime


class GitHubService:
    BASE = "https://api.github.com"

    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _get(self, url, params=None):
        try:
            r = requests.get(url, headers=self.headers, params=params, timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            current_app.logger.error(f"GitHub API error {url}: {e}")
            return None

    def _get_paginated(self, url, max_pages=10):
        results = []
        page = 1
        while page <= max_pages:
            data = self._get(url, params={"per_page": 100, "page": page})
            if not data:
                break
            results.extend(data)
            if len(data) < 100:
                break
            page += 1
        return results

    def get_user(self, username):
        return self._get(f"{self.BASE}/users/{username}")

    def get_repos(self, username):
        repos = self._get_paginated(f"{self.BASE}/users/{username}/repos")
        return [r for r in repos if not r.get("fork", False)]

    def get_commits(self, owner, repo, author=None):
        url = f"{self.BASE}/repos/{owner}/{repo}/commits"
        params = {"per_page": 100}
        if author:
            params["author"] = author

        results = []
        page = 1
        while page <= 15:  # cap at 1500 commits per repo
            try:
                r = requests.get(
                    url,
                    headers=self.headers,
                    params={**params, "page": page},
                    timeout=15,
                )
                if r.status_code == 409:  # empty repo
                    break
                r.raise_for_status()
                data = r.json()
                if not data:
                    break
                results.extend(data)
                if len(data) < 100:
                    break
                page += 1
            except Exception as e:
                current_app.logger.error(f"Commits error {repo}: {e}")
                break
        return results

    def get_languages(self, owner, repo):
        data = self._get(f"{self.BASE}/repos/{owner}/{repo}/languages")
        return data or {}

    def exchange_code_for_token(self, code):
        cfg = current_app.config
        r = requests.post(
            "https://github.com/login/oauth/access_token",
            json={
                "client_id": cfg["GITHUB_CLIENT_ID"],
                "client_secret": cfg["GITHUB_CLIENT_SECRET"],
                "code": code,
            },
            headers={"Accept": "application/json"},
            timeout=15,
        )
        data = r.json()
        return data.get("access_token")

    def get_authenticated_user(self):
        return self._get(f"{self.BASE}/user")
