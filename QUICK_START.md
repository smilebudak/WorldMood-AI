# 🚀 WorldMood-AI - Quick Start Guide

## Backend Developer - Quick Setup

This guide will help you set up the WorldMood-AI backend with Last.fm integration.

---

## ⚡ Get Started in 1 Minute

### 1️⃣ Create .env File

```bash
cd WorldMood-AI
cp .env.example .env
nano .env
```

**`.env` contents:**
```env
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@localhost:5432/worldmood
REDIS_URL=redis://localhost:6379/0
LASTFM_API_KEY=your_lastfm_api_key_here
```

---

### 2️⃣ Prepare PostgreSQL

```bash
# Start PostgreSQL (macOS)
brew services start postgresql@16

# Create database
psql -U postgres -f backend/init_db.sql
```

**Or use the automated script:**
```bash
./setup_database.sh
```

---

### 3️⃣ Install Dependencies

```bash
cd backend
pip3 install -r requirements.txt
```

**requirements.txt contents:**
```plaintext
fastapi>=0.110,<1
uvicorn[standard]>=0.29,<1
pydantic>=2.6,<3
pydantic-settings>=2.2,<3
sqlalchemy[asyncio]>=2.0,<3
asyncpg>=0.29,<1
alembic>=1.13,<2
psycopg2-binary>=2.9,<3
redis>=5.0,<6
httpx>=0.27,<1
numpy>=1.26,<2
pandas>=2.2,<3
scikit-learn>=1.4,<2
python-dotenv>=1.0,<2
```

---

### 4️⃣ Run Migrations

```bash
cd backend
python3 scripts/run_migrations.py
```

**Output:**
```
🔄 WorldMood-AI Database Migration
============================================================
📍 Current migration status:
...
⬆️  Applying migrations...
✅ Migrations applied successfully!
```

---

### 5️⃣ Start Backend

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database tables ensured.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### 6️⃣ Test It!

After the backend is running:

```bash
# Health check
curl http://localhost:8000/health

# Real data from Last.fm
curl http://localhost:8000/mood/global
```

**Expected response:**
```json
{
  "updated_at": "2026-02-07T12:00:00",
  "countries": [
    {
      "country_code": "US",
      "country_name": "United States",
      "mood_score": 0.65,
      "mood_label": "Happy",
      "color_code": "#22c55e",
      "valence": 0.72,
      "energy": 0.68,
      "top_genre": "pop",
      "top_track": "Blinding Lights - The Weeknd",
      "date": "2026-02-07T12:00:00"
    },
    ...
  ]
}
```

---

## 🐘 Check with pgAdmin

### 1. Open pgAdmin
```bash
brew install --cask pgadmin4
pgadmin4
```

### 2. Add Server

**General:**
- Name: `WorldMood-AI`

**Connection:**
- Host: `localhost`
- Port: `5432`
- Database: `worldmood`
- Username: `worldmood`
- Password: `worldmood`

### 3. View Tables

In the left panel:
```
Servers → WorldMood-AI → Databases → worldmood
  → Schemas → public → Tables
    ├── country_mood  ← Mood data
    └── mood_spike    ← Mood changes
```

---

## 🔄 Populate Data (Optional)

### Daily Data Collection:

```bash
cd backend
python3 scripts/daily_ingest.py
```

This script:
- Fetches data from Last.fm for all countries
- Calculates mood scores
- Saves to database
- Detects spikes

---

## 📊 Important Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/mood/global` | GET | Current mood for all countries (from Last.fm) |
| `/country/{code}/mood` | GET | Specific country mood details |
| `/country/{code}/trend` | GET | 7-day trend for a country |
| `/spikes` | GET | Recent mood spikes |

---

## 🔍 Troubleshooting

### PostgreSQL Connection Error

```bash
# Is the service running?
pg_isready

# Does the database exist?
psql -U postgres -l | grep worldmood

# If not, create it
psql -U postgres -f backend/init_db.sql
```

### Alembic Error

```bash
# Is Alembic installed?
python3 -m alembic --version

# If not, install it
pip3 install alembic psycopg2-binary

# Check migration status
cd backend
python3 -m alembic current
```

### Last.fm API Error

**Error:** `LASTFM_API_KEY not configured`

**Solution:** Check the API key in `.env` file:
```env
LASTFM_API_KEY=your_lastfm_api_key_here
```

### Port Already in Use

```bash
# Who is using port 8000?
lsof -i :8000

# Kill the old process if needed
kill -9 <PID>
```

---

## 📁 Project Structure

```
WorldMood-AI/
├── .env                    ← API keys here
├── backend/
│   ├── alembic/            ← Migration files
│   │   └── versions/
│   │       └── 001_initial.py
│   ├── app/
│   │   ├── api/routes/
│   │   │   └── mood.py     ← /mood/global endpoint
│   │   ├── services/
│   │   │   └── lastfm_service.py  ← Last.fm integration
│   │   ├── core/
│   │   │   └── mood_engine.py     ← Mood calculation
│   │   ├── db/
│   │   │   └── models.py          ← Database models
│   │   └── main.py                ← FastAPI app
│   └── scripts/
│       ├── run_migrations.py      ← Migration runner
│       └── check_db.py            ← Database check
└── frontend/
    └── ...
```

---

## 🎯 What's New?

Recent changes:

1. **Last.fm Integration**
   - ✅ Added `lastfm_service.py`
   - ✅ Tag-based mood feature extraction
   - ✅ Support for 31 countries

2. **Config Updates**
   - ✅ `MUSIC_PROVIDER=lastfm`
   - ✅ Added `LASTFM_API_KEY`

3. **Endpoint Changes**
   - ✅ `/mood/global` now returns real data from Last.fm
   - ✅ Redis caching mechanism
   - ✅ On-the-fly mood calculation

---

## 🚀 Deploying to Production

### 1. Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://worldmood:STRONG_PASSWORD@production-host:5432/worldmood
REDIS_URL=redis://production-redis:6379/0
LASTFM_API_KEY=YOUR_PRODUCTION_KEY
DEBUG=False
```

### 2. Run Migrations

```bash
cd backend
python3 scripts/run_migrations.py
```

### 3. Start with Gunicorn

```bash
pip3 install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. With Docker (Recommended)

```bash
docker-compose up -d
```

---

## 📚 Related Documentation

- **[DATABASE_DESIGN.md](DATABASE_DESIGN.md)** - Detailed database schema
- **[DATABASE_README.md](DATABASE_README.md)** - Database setup guide
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Manual database setup
- **[BACKEND_DATABASE_GUIDE.md](BACKEND_DATABASE_GUIDE.md)** - Backend developer guide

---

## ✅ Checklist

Before getting started, verify:

- [ ] PostgreSQL 16+ installed
- [ ] Python 3.11+ installed
- [ ] `.env` file created
- [ ] `LASTFM_API_KEY` entered
- [ ] PostgreSQL service running
- [ ] Database `worldmood` created
- [ ] Dependencies installed (`pip3 install -r requirements.txt`)
- [ ] Migrations applied
- [ ] Backend started
- [ ] `/mood/global` endpoint tested

---

**🎉 Congratulations! Your backend is ready and fetching real data from Last.fm!**
