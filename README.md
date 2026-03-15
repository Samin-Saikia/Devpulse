# ⚡ DevPulse

> Your GitHub analytics dashboard — commit heatmaps, language breakdowns, activity patterns, and streaks, all from your real data.

Live at: **[devpulse.onrender.com](https://devpulse-5y2i.onrender.com)**

---

## 📸 Screenshots


### Landing Page
![Landing Page](screenshots\Screenshot_25.png)

### Dashboard
![Dashboard](screenshots\Screenshot_26.png)

### Charts
![Charts](screenshots\Screenshot_27.png)

---

## ✨ Features

- **GitHub OAuth Login** — Secure login, no passwords stored
- **Commit Heatmap** — GitHub-style 365-day activity calendar
- **Language Distribution** — Doughnut chart of every language you've written
- **Hourly Activity** — Bar chart showing what time of day you code
- **Weekly Patterns** — Which days you're most productive
- **Top Repos** — Most active repositories by commit count
- **Streaks** — Longest and current commit streak tracking
- **Auto-sync** — Background job refreshes your data every 24 hours

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11 + Flask |
| Database | SQLite + SQLAlchemy |
| Auth | GitHub OAuth2 |
| Data Source | GitHub REST API v3 |
| Scheduler | APScheduler |
| Charts | Chart.js |
| Frontend | HTML + CSS + Vanilla JS |
| Deployment | Render + Gunicorn |

---

## 🚀 Deploy to Render

### Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/devpulse.git
git push -u origin main
```

### Step 2 — Create a GitHub OAuth App

1. Go to [github.com/settings/developers](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in:
   - **Application name**: `DevPulse`
   - **Homepage URL**: `https://devpulse-5y2i.onrender.com`
   - **Authorization callback URL**: `https://devpulse-5y2i.onrender.com/callback`
4. Click **Register application**
5. Copy the **Client ID**
6. Click **Generate a new client secret** — copy it immediately

### Step 3 — Create a Web Service on Render

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `devpulse` ← this gives you `devpulse.onrender.com`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app --workers 2 --bind 0.0.0.0:$PORT --timeout 120`
   - **Python Version**: `3.11`

### Step 4 — Set Environment Variables on Render

In your Render dashboard → **Environment**, add these:

| Key | Value |
|-----|-------|
| `GITHUB_CLIENT_ID` | from your GitHub OAuth app |
| `GITHUB_CLIENT_SECRET` | from your GitHub OAuth app |
| `SECRET_KEY` | a random hex string (see below) |
| `APP_URL` | `https://devpulse-5y2i.onrender.com` |

Generate a SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 5 — Deploy

Hit **Deploy**. Render will build and deploy automatically. First login and sync takes 30–90 seconds depending on how many repos you have.

> **Note:** The `.env` file in this repo is for reference only — never commit real secrets to git. Always set them via Render's Environment tab.

---

## 💻 Run Locally (optional)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Update `.env`:
```env
APP_URL=http://localhost:5000
```

Update your GitHub OAuth app callback URL to `http://localhost:5000/callback`, then:

```bash
python run.py
```

Open [http://localhost:5000](http://localhost:5000).

---

## 📁 Project Structure

```
devpulse/
├── app/
│   ├── __init__.py          # App factory
│   ├── scheduler.py         # 24hr background sync
│   ├── routes/
│   │   ├── auth.py          # GitHub OAuth flow
│   │   ├── dashboard.py     # Page rendering
│   │   └── api.py           # JSON endpoints
│   ├── models/
│   │   ├── user.py          # User model
│   │   └── stats.py         # Analytics model
│   ├── services/
│   │   ├── github.py        # GitHub API client
│   │   ├── analyzer.py      # Analytics engine
│   │   └── sync.py          # Data sync orchestrator
│   ├── templates/
│   │   ├── index.html
│   │   └── dashboard.html
│   └── static/
│       ├── css/style.css
│       └── js/dashboard.js
├── config.py
├── run.py
├── Procfile
├── requirements.txt
├── .env
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔒 Privacy

- DevPulse only requests **read-only** GitHub access (`read:user`, `repo`)
- No data is shared with third parties
- Revoke access anytime at [github.com/settings/applications](https://github.com/settings/applications)

---

## 📄 License

MIT — see [LICENSE](./LICENSE)
