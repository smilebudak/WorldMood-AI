# 🗄️ PostgreSQL Database Setup - Quick Reference

## 📁 Created Files

```
WorldMood-AI/
├── setup_database.sh              # 🚀 Automated setup script
├── DATABASE_SETUP.md              # 📚 Detailed setup documentation
├── BACKEND_DATABASE_GUIDE.md      # 🔧 Backend developer guide
├── .env.example                   # ⚙️  Environment template (updated)
└── backend/
    ├── init_db.sql               # 💾 PostgreSQL initialization script
    └── scripts/
        ├── create_tables.py      # 📊 Auto-create tables
        └── check_db.py           # 🔍 Check database status
```

---

## ⚡ Quick Setup

### Method 1: Automated Script (Fastest)

```bash
./setup_database.sh
```

This script automatically:
- ✅ Checks and starts PostgreSQL
- ✅ Creates database and user
- ✅ Creates tables and indexes
- ✅ Prepares `.env` file
- ✅ Validates installation

---

### Method 2: Docker Compose (Recommended)

```bash
# 1. Create .env file
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Create tables
docker-compose exec backend python scripts/create_tables.py

# 4. Check status
docker-compose exec backend python scripts/check_db.py
```

---

### Method 3: Manual Setup

```bash
# 1. Create database
psql -U postgres -f backend/init_db.sql

# 2. Configure .env
cp .env.example .env
nano .env  # Update DATABASE_URL

# 3. Create tables
cd backend
python scripts/create_tables.py

# 4. Check status
python scripts/check_db.py
```

---

## 🔧 Database URL Format

### With Docker:
```env
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@postgres:5432/worldmood
```

### Local PostgreSQL:
```env
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@localhost:5432/worldmood
```

### Remote Server:
```env
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@<SERVER_IP>:5432/worldmood
```

**Note:** Replace `<SERVER_IP>` with the actual IP address (e.g., `192.168.1.100`)

---

## 📊 Database Schema

### country_mood Table
```sql
- id (SERIAL PRIMARY KEY)
- country_code (VARCHAR(3))      -- "US", "GB", etc.
- country_name (VARCHAR(120))
- date (TIMESTAMP)
- mood_score (FLOAT)             -- -1.0 to 1.0
- mood_label (VARCHAR(20))       -- "Happy", "Sad", etc.
- color_code (VARCHAR(7))        -- Hex color
- valence, energy, danceability, acousticness (FLOAT)
- top_genre, top_track (VARCHAR)
- news_sentiment (FLOAT)
- created_at (TIMESTAMP)
- UNIQUE(country_code, date)
```

### mood_spike Table
```sql
- id (SERIAL PRIMARY KEY)
- country_code (VARCHAR(3))
- detected_at (TIMESTAMP)
- previous_label (VARCHAR(20))
- new_label (VARCHAR(20))
- delta (FLOAT)
- reason (TEXT)
```

---

## 🛠️ Useful Commands

### Python Scripts
```bash
# Create tables
python backend/scripts/create_tables.py

# Database status
python backend/scripts/check_db.py

# Daily data collection
python backend/scripts/daily_ingest.py
```

### SQL Commands
```bash
# Connect to database
psql -U worldmood -d worldmood

# List tables
\dt

# Check data
SELECT COUNT(*) FROM country_mood;
SELECT COUNT(*) FROM mood_spike;

# Recent records
SELECT * FROM country_mood ORDER BY created_at DESC LIMIT 5;
```

### Docker Commands
```bash
# Start services
docker-compose up -d

# Backend logs
docker-compose logs -f backend

# Connect to PostgreSQL
docker-compose exec postgres psql -U worldmood -d worldmood

# Run commands in backend
docker-compose exec backend python scripts/check_db.py
```

---

## 🔍 Troubleshooting

| Error | Solution |
|-------|----------|
| `could not connect to server` | Check service with `pg_isready`, start if needed |
| `database does not exist` | Run `psql -U postgres -f backend/init_db.sql` |
| `password authentication failed` | Check password in `.env` file |
| `relation does not exist` | Run `python scripts/create_tables.py` |
| Port 5432 in use | Check with `lsof -i :5432` |

---

## 📚 Documentation

- **[BACKEND_DATABASE_GUIDE.md](BACKEND_DATABASE_GUIDE.md)** - Detailed guide for backend developers
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Comprehensive setup and management documentation
- **[backend/init_db.sql](backend/init_db.sql)** - SQL initialization script

---

## 🔐 Security Notes

**IMPORTANT for Production:**

1. **Change passwords:**
```sql
ALTER USER worldmood WITH PASSWORD 'strong_password_123!';
```

2. **Don't commit `.env` to git:**
```bash
# Ensure it's in .gitignore
echo ".env" >> .gitignore
```

3. **Configure firewall:**
```bash
# Allow access only from specific IPs
sudo ufw allow from 10.0.0.0/24 to any port 5432
```

4. **Use SSL:**
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
```

---

## ✅ Backend Developer Checklist

For backend developers:

- [ ] PostgreSQL installed and running
- [ ] `init_db.sql` executed
- [ ] `.env` file created
- [ ] `DATABASE_URL` updated with correct server IP
- [ ] `python scripts/create_tables.py` executed
- [ ] Verified with `python scripts/check_db.py`
- [ ] API keys added to `.env` (LASTFM, GEMINI, etc.)
- [ ] Backend started and tested
- [ ] Health check endpoint working (`/health`)

---

## 🚀 Starting the Application

```bash
# Start backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or start entire stack with Docker
docker-compose up
```

**API Test:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/country/US/mood
```

---

## 📞 Help

If you encounter issues:

1. Check logs
2. Run `python scripts/check_db.py`
3. Set `DEBUG=True` in `.env`
4. Refer to [DATABASE_SETUP.md](DATABASE_SETUP.md) troubleshooting section

---

**Created: 2026-02-07**
**Version: 1.0**
**PostgreSQL: 16+**
**SQLAlchemy: 2.0+**
