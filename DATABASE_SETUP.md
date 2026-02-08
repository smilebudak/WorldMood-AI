# 🗄️ PostgreSQL Database Setup Guide

## 📋 Requirements
- PostgreSQL 12+ must be installed
- Access to `psql` command on the server

---

## 🚀 Setup Steps

### 1️⃣ Creating the Database

Connect to PostgreSQL and run the `init_db.sql` script:

```bash
# Connect to PostgreSQL as root/postgres user
psql -U postgres

# Execute the script file
\i /path/to/backend/init_db.sql

# Or directly:
psql -U postgres -f backend/init_db.sql
```

The script performs the following operations:
- ✅ Creates the `worldmood` user
- ✅ Creates the `worldmood` database
- ✅ Creates the `country_mood` and `mood_spike` tables
- ✅ Adds required indexes
- ✅ Sets up permissions

---

### 2️⃣ Environment Configuration

#### Using with Docker (Recommended)

If you're using Docker Compose, in the `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@postgres:5432/worldmood
```

Docker Compose automatically starts the PostgreSQL service.

#### Manual Server Setup

If you're using your own PostgreSQL server:

1. **Copy `.env.example`:**
```bash
cp .env.example .env
```

2. **Edit the `.env` file:**
```env
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@<SERVER_IP>:5432/worldmood
```

Replace `<SERVER_IP>` with:
- Local use: `localhost` or `127.0.0.1`
- Remote server: Server's IP address (e.g., `192.168.1.100`)
- Domain: Server domain (e.g., `db.example.com`)

---

### 3️⃣ Testing the Database Connection

From the backend folder:

```bash
cd backend

# Activate Python environment
# poetry shell  # if using poetry
# or
# source venv/bin/activate  # if using venv

# Test the database connection
python -c "
from app.db.session import engine
import asyncio

async def test():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('✅ Database connection successful!')

asyncio.run(test())
"
```

---

### 4️⃣ Migration with Alembic (Optional)

You can use Alembic for future schema changes:

```bash
# Create migration folder
cd backend
alembic init alembic

# Save existing models as a migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

---

## 🔒 Security Notes

### For Production Environment:

1. **Use strong passwords:**
```sql
ALTER USER worldmood WITH PASSWORD 'strong_and_complex_password_123!@#';
```

2. **Never commit the `.env` file:**
```bash
# Make sure it's in .gitignore
echo ".env" >> .gitignore
```

3. **PostgreSQL firewall settings:**
```bash
# Allow access only from specific IPs
# Configure postgresql.conf and pg_hba.conf files
```

4. **Use SSL/TLS:**
```env
DATABASE_URL=postgresql+asyncpg://worldmood:password@host:5432/worldmood?ssl=require
```

---

## 🐛 Troubleshooting

### Connection Error: "could not connect to server"
```bash
# Check PostgreSQL service
sudo systemctl status postgresql

# Start the service
sudo systemctl start postgresql
```

### Permission Error: "permission denied"
```sql
-- Re-grant permissions in PostgreSQL
GRANT ALL PRIVILEGES ON DATABASE worldmood TO worldmood;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO worldmood;
```

### Port 5432 is in use
```bash
# Check which process is using the port
lsof -i :5432
```

---

## 📊 Useful SQL Commands

```sql
-- List tables
\dt

-- Show table structure
\d country_mood
\d mood_spike

-- Check existing data
SELECT COUNT(*) FROM country_mood;
SELECT COUNT(*) FROM mood_spike;

-- Show latest records
SELECT * FROM country_mood ORDER BY created_at DESC LIMIT 5;
SELECT * FROM mood_spike ORDER BY detected_at DESC LIMIT 5;

-- Check database size
SELECT pg_size_pretty(pg_database_size('worldmood'));
```

---

## 🔄 Backup and Restore

### Creating a Backup:
```bash
pg_dump -U worldmood -h localhost worldmood > backup_$(date +%Y%m%d).sql
```

### Restore:
```bash
psql -U worldmood -h localhost worldmood < backup_20260207.sql
```

---

## 📞 Help

If you experience issues:
1. Check PostgreSQL logs: `/var/log/postgresql/`
2. Check backend logs
3. Set `DEBUG=True` in the `.env` file and review detailed logs
