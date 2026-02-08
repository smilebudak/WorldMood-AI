# 🔧 Backend Developer Guide - Database Connection

## 📝 Summary

PostgreSQL database is ready. Backend developer needs to:

### ✅ Tasks to Complete:

1. **Run PostgreSQL and apply the init script**
2. **Create the `.env` file and update the DATABASE_URL**
3. **Create tables** (with automatic script)
4. **Start and test the backend**

---

## 🚀 Quick Start

### Option 1: With Docker (Recommended - Easiest)

```bash
# 1. Create .env file
cp .env.example .env

# 2. Start all services (PostgreSQL + Redis + Backend + Frontend)
docker-compose up -d

# 3. Monitor backend logs
docker-compose logs -f backend

# 4. Create tables (on first run)
docker-compose exec backend python scripts/create_tables.py

# 5. Check database status
docker-compose exec backend python scripts/check_db.py
```

✅ **No changes needed with Docker!** DATABASE_URL is already properly configured.

---

### Option 2: With Manual PostgreSQL Server

#### 1️⃣ Install and Start PostgreSQL

```bash
# macOS
brew install postgresql@16
brew services start postgresql@16

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql-16
sudo systemctl start postgresql

# Remote server
ssh user@server_ip
sudo systemctl start postgresql
```

#### 2️⃣ Create the Database

```bash
# Run the init_db.sql script
psql -U postgres -f backend/init_db.sql

# Or from within PostgreSQL:
psql -U postgres
\i backend/init_db.sql
```

The script does:
- ✅ Creates the `worldmood` user (password: `worldmood`)
- ✅ Creates the `worldmood` database
- ✅ Creates the `country_mood` and `mood_spike` tables
- ✅ Sets up indexes and permissions

#### 3️⃣ Configure the .env File

```bash
# Copy .env.example
cp .env.example .env

# Edit the .env file
nano .env  # or vim, vscode, etc.
```

**Update DATABASE_URL in `.env`:**

```env
# Local PostgreSQL
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@localhost:5432/worldmood

# Remote server (example)
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@192.168.1.100:5432/worldmood

# With domain
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@db.example.com:5432/worldmood
```

**Format:**
```
postgresql+asyncpg://[username]:[password]@[host]:[port]/[database_name]
```

#### 4️⃣ Create Tables (First Time)

```bash
cd backend

# Activate Python environment (if available)
# source venv/bin/activate

# Create tables
python scripts/create_tables.py
```

Output should look like:
```
🗄️  WorldMood-AI Database Initialization
============================================================
📍 Database URL: localhost:5432/worldmood
============================================================

🔌 Testing database connection...
✅ Connection successful!
📦 PostgreSQL version: PostgreSQL 16.x

🔍 Checking existing tables...
✅ Tables created successfully!

📋 Created tables:
   • country_mood
   • mood_spike

📊 Total table count: 2

✨ Setup complete!
```

#### 5️⃣ Check Database Status

```bash
# Check database status
python scripts/check_db.py
```

#### 6️⃣ Start the Backend

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🔍 Troubleshooting

### ❌ "could not connect to server"

```bash
# Is PostgreSQL running?
# macOS:
brew services list | grep postgresql

# Linux:
sudo systemctl status postgresql

# Start it:
# macOS:
brew services start postgresql@16

# Linux:
sudo systemctl start postgresql
```

### ❌ "database 'worldmood' does not exist"

```bash
# Run init_db.sql again
psql -U postgres -f backend/init_db.sql
```

### ❌ "password authentication failed"

Check the password in the `.env` file. Default: `worldmood`

```bash
# Change password in PostgreSQL
psql -U postgres
ALTER USER worldmood WITH PASSWORD 'new_password';
```

### ❌ "relation 'country_mood' does not exist"

```bash
# Create tables
python scripts/create_tables.py
```

### 🔒 Firewall/Port Issues

```bash
# Can you access PostgreSQL port?
telnet localhost 5432
# or
nc -zv localhost 5432

# Open port 5432 in firewall (for remote server)
sudo ufw allow 5432/tcp

# Make sure PostgreSQL accepts external connections
# postgresql.conf:
# listen_addresses = '*'

# pg_hba.conf: (SECURITY WARNING - restrict IP in production!)
# host    all    all    0.0.0.0/0    md5
```

---

## 📊 Useful Commands

### Python Scripts

```bash
# Database status
python scripts/check_db.py

# Create tables
python scripts/create_tables.py

# Daily data collection (for cron job)
python scripts/daily_ingest.py
```

### SQL Commands

```bash
# Connect to PostgreSQL
psql -U worldmood -d worldmood

# List tables
\dt

# Table structure
\d country_mood
\d mood_spike

# Latest records
SELECT * FROM country_mood ORDER BY created_at DESC LIMIT 5;
SELECT * FROM mood_spike ORDER BY detected_at DESC LIMIT 5;

# Statistics
SELECT
    country_code,
    COUNT(*) as total_records,
    MAX(created_at) as latest_record
FROM country_mood
GROUP BY country_code
ORDER BY total_records DESC;

# Database size
SELECT pg_size_pretty(pg_database_size('worldmood'));
```

---

## 🔐 Security Notes

### MUST Change for Production:

1. **Strengthen passwords:**
```sql
ALTER USER worldmood WITH PASSWORD 'very_strong_password_123!@#$';
```

2. **Update the `.env` file:**
```env
DATABASE_URL=postgresql+asyncpg://worldmood:very_strong_password_123!@#$@host:5432/worldmood
```

3. **Firewall configuration:**
```bash
# Allow access only from specific IPs
# pg_hba.conf:
host    worldmood    worldmood    10.0.1.0/24    md5  # Only this subnet
```

4. **Use SSL:**
```env
DATABASE_URL=postgresql+asyncpg://worldmood:password@host:5432/worldmood?ssl=require
```

---

## 📞 Contact

If you experience issues with database setup:

1. **Check logs:**
   - Backend logs: `docker-compose logs backend`
   - PostgreSQL logs: `/var/log/postgresql/`

2. **Enable debug mode:**
   ```env
   # In .env file
   DEBUG=True
   ```

3. **Test connection:**
   ```bash
   python scripts/check_db.py
   ```

---

## 📚 Additional Resources

- [DATABASE_SETUP.md](DATABASE_SETUP.md) - Detailed setup guide
- [backend/init_db.sql](backend/init_db.sql) - SQL initialization script
- [backend/app/db/models.py](backend/app/db/models.py) - SQLAlchemy models
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**✨ After successful setup, API endpoints can be tested:**

```bash
# Health check
curl http://localhost:8000/health

# Country moods
curl http://localhost:8000/api/country/US/mood

# Mood spikes
curl http://localhost:8000/api/spikes
```
