# 🗄️ MoodAtlas Database Design

## 📊 Schema Overview

MoodAtlas uses PostgreSQL to store global mood data aggregated from music trends (Last.fm) and news sentiment.

### Architecture:
```
┌─────────────────────────────────────────────────┐
│          Application Layer (FastAPI)            │
├─────────────────────────────────────────────────┤
│     SQLAlchemy ORM (Async with asyncpg)        │
├─────────────────────────────────────────────────┤
│          PostgreSQL 16 Database                 │
└─────────────────────────────────────────────────┘
```

---

## 📋 Tables

### 1. `country_mood` - Daily Country Mood Snapshots

Stores aggregated mood data per country per day.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | SERIAL | NOT NULL | Primary key |
| `country_code` | VARCHAR(3) | NOT NULL | ISO country code (US, GB, etc.) |
| `country_name` | VARCHAR(120) | NOT NULL | Full country name |
| `date` | TIMESTAMP | NOT NULL | Snapshot date/time |
| `mood_score` | FLOAT | NOT NULL | Mood value from -1.0 (negative) to 1.0 (positive) |
| `mood_label` | VARCHAR(20) | NOT NULL | Happy \| Calm \| Sad \| Angry \| Anxious |
| `color_code` | VARCHAR(7) | NOT NULL | Hex color code for visualization |
| `valence` | FLOAT | NULL | Musical positiveness (0-1) from Last.fm |
| `energy` | FLOAT | NULL | Musical intensity (0-1) from Last.fm |
| `danceability` | FLOAT | NULL | Danceability measure (0-1) |
| `acousticness` | FLOAT | NULL | Acoustic vs electronic (0-1) |
| `top_genre` | VARCHAR(60) | NULL | Most popular genre |
| `top_track` | VARCHAR(200) | NULL | Most popular track |
| `news_sentiment` | FLOAT | NULL | News sentiment score (-1 to 1) |
| `created_at` | TIMESTAMP | NULL | Record creation timestamp |

**Constraints:**
- Primary Key: `id`
- Unique: `(country_code, date)` - Ensures one record per country per day
- Index: `idx_country_mood_code` on `country_code`
- Index: `idx_country_mood_date` on `date`
- Index: `idx_country_mood_code_date` on `(country_code, date)` - Composite for fast lookups

**Example Row:**
```sql
id: 1
country_code: 'US'
country_name: 'United States'
date: 2026-02-07 12:00:00
mood_score: 0.65
mood_label: 'Happy'
color_code: '#22c55e'
valence: 0.72
energy: 0.68
danceability: 0.75
acousticness: 0.15
top_genre: 'pop'
top_track: 'Blinding Lights - The Weeknd'
news_sentiment: 0.12
created_at: 2026-02-07 12:05:00
```

---

### 2. `mood_spike` - Mood Change Detection

Tracks significant mood changes/anomalies per country.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | SERIAL | NOT NULL | Primary key |
| `country_code` | VARCHAR(3) | NOT NULL | ISO country code |
| `detected_at` | TIMESTAMP | NOT NULL | When spike was detected |
| `previous_label` | VARCHAR(20) | NOT NULL | Previous mood state |
| `new_label` | VARCHAR(20) | NOT NULL | New mood state |
| `delta` | FLOAT | NOT NULL | Magnitude of mood change |
| `reason` | TEXT | NULL | Detected cause of spike |

**Constraints:**
- Primary Key: `id`
- Index: `idx_mood_spike_code` on `country_code`
- Index: `idx_mood_spike_detected` on `detected_at`
- Index: `idx_mood_spike_code_detected` on `(country_code, detected_at)`

**Example Row:**
```sql
id: 1
country_code: 'BR'
detected_at: 2026-02-07 15:30:00
previous_label: 'Calm'
new_label: 'Happy'
delta: 0.45
reason: 'Major sports victory detected in news'
```

---

## 🔄 Data Flow

```
┌─────────────────┐
│   Last.fm API   │ ───► Fetch top tracks per country
└─────────────────┘      Extract mood features from tags
         │
         ▼
┌─────────────────┐
│   News API      │ ───► Fetch news sentiment per country
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Mood Engine    │ ───► Compute mood_score & mood_label
└─────────────────┘      Apply algorithm (valence, energy, etc.)
         │
         ▼
┌─────────────────┐
│ country_mood    │ ───► Store daily snapshot
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Spike Detector  │ ───► Compare with previous data
└─────────────────┘      Detect significant changes
         │
         ▼
┌─────────────────┐
│  mood_spike     │ ───► Log anomalies
└─────────────────┘
```

---

## 🎨 Mood Classification

### Mood Labels & Score Ranges:

| Label | Score Range | Color | Emoji | Description |
|-------|-------------|-------|-------|-------------|
| **Happy** | 0.5 to 1.0 | `#22c55e` (Green) | 😊 | Positive, upbeat mood |
| **Calm** | 0.15 to 0.5 | `#38bdf8` (Blue) | 😌 | Peaceful, relaxed state |
| **Anxious** | -0.5 to 0.15 | `#f97316` (Orange) | 😰 | Tense, worried state |
| **Sad** | -0.5 to -0.15 | `#8b5cf6` (Purple) | 😢 | Melancholic, down mood |
| **Angry** | -1.0 to -0.5 | `#ef4444` (Red) | 😠 | Aggressive, intense negativity |

### Mood Score Calculation:

```
base = 0.40 × (valence × 2 - 1)        # Musical positiveness
     + 0.20 × (energy × 2 - 1)         # Intensity
     + 0.15 × (danceability × 2 - 1)   # Danceability
     - 0.10 × (acousticness × 2 - 1)   # Electronic vs acoustic

If news_sentiment provided:
    mood_score = base × 0.85 + news_sentiment × 0.15

Clipped to [-1.0, 1.0]
```

---

## 🔍 Query Patterns

### Get Latest Mood for All Countries:
```sql
SELECT DISTINCT ON (country_code)
    country_code, country_name, mood_score, mood_label, color_code, date
FROM country_mood
ORDER BY country_code, date DESC;
```

### Get Country Trend (Last 7 Days):
```sql
SELECT date, mood_score, mood_label
FROM country_mood
WHERE country_code = 'US'
  AND date >= NOW() - INTERVAL '7 days'
ORDER BY date ASC;
```

### Get Recent Mood Spikes:
```sql
SELECT country_code, detected_at, previous_label, new_label, delta, reason
FROM mood_spike
WHERE detected_at >= NOW() - INTERVAL '24 hours'
ORDER BY detected_at DESC;
```

### Country with Biggest Mood Change:
```sql
WITH latest AS (
    SELECT DISTINCT ON (country_code)
        country_code,
        mood_score as current_score
    FROM country_mood
    ORDER BY country_code, date DESC
),
previous AS (
    SELECT DISTINCT ON (country_code)
        country_code,
        mood_score as previous_score
    FROM country_mood
    WHERE date < (SELECT MAX(date) FROM country_mood)
    ORDER BY country_code, date DESC
)
SELECT 
    l.country_code,
    l.current_score,
    p.previous_score,
    (l.current_score - p.previous_score) as delta
FROM latest l
JOIN previous p ON l.country_code = p.country_code
ORDER BY ABS(l.current_score - p.previous_score) DESC
LIMIT 10;
```

---

## 🎯 Supported Countries

Currently tracking **31 countries** via Last.fm:

| Region | Countries |
|--------|-----------|
| **Americas** | US, CA, BR, MX, AR, CL, CO |
| **Europe** | GB, DE, FR, ES, IT, NL, PL, SE, NO, FI, TR, RU |
| **Asia** | JP, IN, KR, PH, ID, TH, VN |
| **Oceania** | AU |
| **Africa** | ZA, NG, EG |

---

## 📈 Data Volume Estimates

### Storage Requirements:

| Metric | Value |
|--------|-------|
| Countries tracked | 31 |
| Records per day | 31 (1 per country) |
| Records per year | ~11,315 |
| Average row size | ~500 bytes |
| Annual storage (country_mood) | ~5.5 MB |
| Spikes per month | ~50-100 |
| 5-year projection | ~30 MB |

**Conclusion:** Lightweight schema, suitable for any PostgreSQL instance.

---

## 🔧 Performance Optimization

### Indexes:

1. **Single Column Indexes:**
   - `country_code` - Fast country lookups
   - `date` - Time-based queries

2. **Composite Indexes:**
   - `(country_code, date)` - Optimal for trend queries

3. **Covering Index (Future):**
```sql
CREATE INDEX idx_country_mood_covering 
ON country_mood (country_code, date) 
INCLUDE (mood_score, mood_label, color_code);
```

### Partitioning (For Scale):

If data grows significantly, partition by date:
```sql
CREATE TABLE country_mood (
    -- columns...
) PARTITION BY RANGE (date);

CREATE TABLE country_mood_2026_q1 
PARTITION OF country_mood 
FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
```

---

## 🔄 Migration Strategy

### Version Control:

Migrations managed via **Alembic** in `backend/alembic/versions/`:

```
001_initial.py         - Initial schema
002_add_xyz.py         - Future changes
...
```

### Running Migrations:

```bash
# Apply all pending migrations
cd backend
python3 scripts/run_migrations.py

# Or manually:
python3 -m alembic upgrade head

# Create new migration
python3 scripts/create_migration.py "Add new feature"
```

---

## 🛡️ Data Integrity

### Constraints:

1. **Unique Constraint:** `(country_code, date)`
   - Prevents duplicate snapshots
   - Ensures data consistency

2. **NOT NULL:** Essential fields enforced
   - `mood_score`, `mood_label`, `color_code`

3. **Foreign Keys:** None currently
   - Countries are denormalized for performance
   - Future: Add `countries` lookup table if needed

### Data Validation:

Handled at application level (Pydantic schemas):
- `mood_score` ∈ [-1.0, 1.0]
- `country_code` matches ISO 3166-1 alpha-2/3
- `color_code` is valid hex

---

## 🚀 Future Enhancements

### Planned Tables:

1. **`user_preferences`**
```sql
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL UNIQUE,
    favorite_countries VARCHAR(3)[],
    alert_threshold FLOAT DEFAULT 0.3,
    created_at TIMESTAMP DEFAULT NOW()
);
```

2. **`mood_history_aggregates`**
```sql
CREATE TABLE mood_history_aggregates (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(3) NOT NULL,
    week_start DATE NOT NULL,
    avg_mood_score FLOAT,
    dominant_label VARCHAR(20),
    UNIQUE(country_code, week_start)
);
```

3. **`global_events`**
```sql
CREATE TABLE global_events (
    id SERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    event_type VARCHAR(50),
    description TEXT,
    affected_countries VARCHAR(3)[]
);
```

---

## 📊 ER Diagram

```
┌─────────────────────────────────┐
│       country_mood              │
├─────────────────────────────────┤
│ PK id                           │
│    country_code VARCHAR(3)      │
│    country_name VARCHAR(120)    │
│    date TIMESTAMP               │
│    mood_score FLOAT             │
│    mood_label VARCHAR(20)       │
│    color_code VARCHAR(7)        │
│    valence FLOAT                │
│    energy FLOAT                 │
│    danceability FLOAT           │
│    acousticness FLOAT           │
│    top_genre VARCHAR(60)        │
│    top_track VARCHAR(200)       │
│    news_sentiment FLOAT         │
│    created_at TIMESTAMP         │
└─────────────────────────────────┘
         │
         │ 1:N (logical)
         ▼
┌─────────────────────────────────┐
│        mood_spike               │
├─────────────────────────────────┤
│ PK id                           │
│    country_code VARCHAR(3)      │
│    detected_at TIMESTAMP        │
│    previous_label VARCHAR(20)   │
│    new_label VARCHAR(20)        │
│    delta FLOAT                  │
│    reason TEXT                  │
└─────────────────────────────────┘
```

---

## 🔐 Security Considerations

1. **Database User Permissions:**
```sql
-- Read-only user for analytics
CREATE USER moodatlas_readonly WITH PASSWORD 'xxx';
GRANT CONNECT ON DATABASE moodatlas TO moodatlas_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO moodatlas_readonly;
```

2. **SSL/TLS in Production:**
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
```

3. **Backup Strategy:**
```bash
# Daily backup
pg_dump -U moodatlas moodatlas > backup_$(date +%Y%m%d).sql

# Automated with cron
0 2 * * * pg_dump -U moodatlas moodatlas > /backups/moodatlas_$(date +\%Y\%m\%d).sql
```

---

**Database Version:** 1.0  
**PostgreSQL Version:** 16+  
**Last Updated:** 2026-02-07  
**Schema Revision:** 001_initial
