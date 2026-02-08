# WorldMood-AI

**Real-time global mood visualization powered by music trends, AI sentiment analysis, and interactive 3D globe.**

Experience the world's emotional pulse through data-driven insights, combining music analytics from Last.fm, news sentiment via Google Gemini AI, and stunning visual storytelling.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](http://localhost:3001)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=next.js)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://www.postgresql.org/)

---

## Features

### Interactive 3D Visualization
- **3D Globe with Starfield** - Mapbox GL powered rotating globe with atmospheric effects
- **Real-time Mood Colors** - Countries dynamically colored based on current mood (Happy 🟢, Calm 🔵, Sad 🟣, Angry 🔴, Anxious 🟠)
- **Smooth Interactions** - Click and drag to explore, zoom to regions, hover for instant insights

### AI-Powered Insights
- **Gemini AI Summaries** - Context-aware mood explanations for each country
- **Smart Analysis** - Combines news headlines with music trends for accurate sentiment
- **Automated Updates** - Daily data refresh with intelligent caching

### Rich Data Visualizations
- **Country Detail Panel** - Deep-dive into any country's mood with:
  - 7-day mood trend charts
  - Audio feature breakdowns (valence, energy, danceability, acousticness)
  - Top music tracks from that region
  - Recent news headlines with sentiment analysis
- **Global Statistics** - Dashboard showing:
  - Total countries tracked
  - Dominant global mood
  - Mood distribution percentages
  - Average emotional metrics
- **Spike Alerts** - Real-time notifications for significant mood shifts

### Multi-Source Data Integration
- **Last.fm API** - Top music tracks and audio features from 60+ countries
- **Google News RSS** - Country-specific news headlines
- **Gemini AI** - Advanced natural language processing for sentiment analysis

---

## Quick Start

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- API Keys (see [Getting API Keys](#-getting-api-keys))

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/WorldMood-AI.git
cd WorldMood-AI

# 2. Set up environment file
cp backend/.env.example backend/.env
# Edit backend/.env and add your API keys

# 3. Start all services
docker-compose up -d

# 4. Wait for services to be healthy (30-60 seconds)
docker-compose ps

# 5. Initialize database
docker-compose exec backend python scripts/create_tables.py

# 6. Load initial mood data (takes 2-3 minutes)
docker-compose exec backend python scripts/daily_ingest.py

# 7. Open the application
# Frontend: http://localhost:3001
# Backend API: http://localhost:8001
# API Docs: http://localhost:8001/docs
```

### Quick Commands

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart backend frontend

# Stop everything
docker-compose down

# Refresh mood data
docker-compose exec backend python scripts/daily_ingest.py
```

---

## Getting API Keys

### Required APIs

| Service | Purpose | Get Key | Free Tier |
|---------|---------|---------|-----------|
| **Google Gemini AI** | AI mood summaries | [Google AI Studio](https://makersuite.google.com/app/apikey) | ✅ Generous |
| **Last.fm** | Music trends & audio features | [Last.fm API](https://www.last.fm/api/account/create) | ✅ Yes |
| **Mapbox** | 3D globe visualization | [Mapbox Account](https://account.mapbox.com/) | ✅ 50k loads/mo |

### Optional APIs

| Service | Purpose | Get Key |
|---------|---------|---------|
| **NewsAPI** | Additional news sources | [NewsAPI.org](https://newsapi.org/register) |

### Environment Configuration

Edit `backend/.env`:

```env
# Database (auto-configured by Docker)
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@postgres:5432/worldmood
REDIS_URL=redis://redis:6379/0

# Required APIs
GEMINI_API_KEY=your_gemini_key_here
LASTFM_API_KEY=your_lastfm_key_here
MAPBOX_TOKEN=your_mapbox_token_here

# Optional
NEWS_API_KEY=your_news_api_key_here  # Can be left empty

# App Settings
DEBUG=true
MUSIC_PROVIDER=lastfm
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token_here
NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

## Architecture

### Tech Stack

#### Backend
- **FastAPI** - Modern async Python web framework
- **PostgreSQL 16** - Primary database with async support
- **Redis 7** - Caching and session management
- **SQLAlchemy 2.0** - ORM with async/await
- **Google Gemini AI** - Advanced language model for summaries
- **Last.fm API** - Music data and audio features
- **Alembic** - Database migrations

#### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Mapbox GL JS** - 3D globe and geospatial visualization
- **Framer Motion** - Smooth animations
- **Recharts** - Data visualization
- **Radix UI** - Accessible component primitives

#### Infrastructure
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Reverse proxy (optional)

### Project Structure

```
WorldMood-AI/
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── api/                 # REST API endpoints
│   │   │   ├── routes/
│   │   │   │   ├── mood.py      # Global & country mood
│   │   │   │   ├── country.py   # Country details
│   │   │   │   └── spikes.py    # Mood spike alerts
│   │   │   └── deps.py          # Shared dependencies
│   │   ├── core/                # Business logic
│   │   │   ├── mood_engine.py   # Mood calculation algorithm
│   │   │   └── spike_detector.py # Anomaly detection
│   │   ├── db/                  # Database layer
│   │   │   ├── models.py        # SQLAlchemy models
│   │   │   └── session.py       # Async DB sessions
│   │   ├── services/            # External integrations
│   │   │   ├── lastfm_service.py    # Last.fm API
│   │   │   ├── news_service.py      # Google News RSS
│   │   │   ├── gemini_service.py    # Gemini AI
│   │   │   └── trends_service.py    # DB operations
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic models
│   │   ├── config.py            # App configuration
│   │   └── main.py              # FastAPI app entry
│   ├── scripts/                 # Utility scripts
│   │   ├── create_tables.py     # Initialize DB
│   │   ├── check_db.py          # DB diagnostics
│   │   ├── daily_ingest.py      # Data refresh job
│   │   ├── create_migration.py  # Migration helper
│   │   └── run_migrations.py    # Apply migrations
│   ├── alembic/                 # Database migrations
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
│
├── frontend/                     # Next.js Frontend
│   ├── app/
│   │   ├── components/          # React components
│   │   │   ├── WorldMap.tsx          # 3D globe
│   │   │   ├── CountryPanel.tsx      # Detail sidebar
│   │   │   ├── CountryTooltip.tsx    # Hover info
│   │   │   ├── GlobalStats.tsx       # Statistics widget
│   │   │   ├── SpikeAlert.tsx        # Mood alerts
│   │   │   └── MoodLegend.tsx        # Color legend
│   │   ├── lib/                 # Utilities
│   │   │   ├── api.ts                # Backend client
│   │   │   ├── moodColors.ts         # Color system
│   │   │   └── mockData.ts           # Dev fallback
│   │   ├── page.tsx             # Home page
│   │   └── layout.tsx           # Root layout
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   ├── tailwind.config.ts
│   └── .env.local
│
├── docker-compose.yml           # Service orchestration
├── .env.example                 # Environment template
├── .gitignore
└── README.md                    # This file
```

---

## How It Works

### Mood Calculation Algorithm

The mood engine combines multiple data sources:

1. **Music Analysis** (60% weight)
   - Valence (happiness level): 40%
   - Energy (intensity): 20%
   - Danceability (positive energy): 15%
   - Acousticness (calmness): -10%

2. **News Sentiment** (40% weight)
   - Analyzed via Gemini AI
   - Weighted by recency
   - Blended 50/50 with music score

3. **Mood Classification**
   - Score > 0.3: **Happy** 🟢 (#22c55e)
   - Score 0 to 0.3: **Calm** 🔵 (#38bdf8)
   - Score -0.3 to 0: **Anxious** 🟠 (#f97316)
   - Score -0.6 to -0.3: **Sad** 🟣 (#8b5cf6)
   - Score < -0.6: **Angry** 🔴 (#ef4444)

### Spike Detection

Identifies significant mood shifts using:
- **Z-score analysis** - Statistical anomaly detection
- **7-day rolling window** - Trend comparison
- **Threshold**: 2.0 standard deviations
- **Triggers**: Label changes or score deltas > 0.3

---

## Database Schema

### `country_mood` Table
Stores daily mood snapshots for each country.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `country_code` | VARCHAR(3) | ISO 3166-1 alpha-2 code |
| `country_name` | VARCHAR(100) | Full country name |
| `date` | TIMESTAMP | Snapshot timestamp |
| `mood_score` | FLOAT | Computed score (-1 to 1) |
| `mood_label` | VARCHAR(20) | Happy, Calm, Anxious, Sad, Angry |
| `color_code` | VARCHAR(7) | Hex color for UI |
| `valence` | FLOAT | Music happiness (0-1) |
| `energy` | FLOAT | Music intensity (0-1) |
| `danceability` | FLOAT | Music danceability (0-1) |
| `acousticness` | FLOAT | Music acousticness (0-1) |
| `top_genre` | VARCHAR(100) | Most popular genre |
| `top_track` | VARCHAR(200) | Most popular song |
| `news_sentiment` | FLOAT | News sentiment (-1 to 1) |
| `news_headlines` | TEXT | JSON array of headlines |
| `news_summary` | TEXT | Gemini AI generated summary |
| `created_at` | TIMESTAMP | Record creation time |

**Indexes:**
- `unique(country_code, date)` - One mood per country per day
- `idx_country_date` - Fast country+date lookups

### `mood_spike` Table
Tracks significant mood changes.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `country_code` | VARCHAR(3) | ISO country code |
| `detected_at` | TIMESTAMP | When spike was detected |
| `previous_label` | VARCHAR(20) | Mood before change |
| `new_label` | VARCHAR(20) | Mood after change |
| `delta` | FLOAT | Change magnitude |
| `reason` | TEXT | Detected trigger/cause |

---

## API Documentation

### REST Endpoints

#### Health Check
```http
GET /health
```
Returns service status.

#### Global Mood Map
```http
GET /mood/global
```
Returns mood data for all countries with caching.

**Response:**
```json
{
  "updated_at": "2025-01-15T10:30:00Z",
  "countries": [
    {
      "country_code": "US",
      "country_name": "United States",
      "mood_score": 0.45,
      "mood_label": "Happy",
      "color_code": "#22c55e",
      "valence": 0.72,
      "energy": 0.68,
      "top_genre": "Pop",
      "top_track": "Good Feeling - Flo Rida",
      "news_sentiment": 0.3,
      "date": "2025-01-15T10:30:00Z"
    }
  ]
}
```

#### Country Details
```http
GET /mood/country/{country_code}
```
Returns detailed mood info + 7-day trend + AI summary.

**Response:**
```json
{
  "country_code": "US",
  "mood_score": 0.45,
  "mood_label": "Happy",
  "trend": [
    {"date": "2025-01-09", "mood_score": 0.42, "mood_label": "Happy"},
    {"date": "2025-01-10", "mood_score": 0.38, "mood_label": "Happy"}
  ],
  "news_headlines": [
    "Economy shows strong growth",
    "New infrastructure projects announced"
  ],
  "news_summary": "United States feels happy as recent headlines...",
  "spike_active": false
}
```

#### Mood Spikes
```http
GET /spikes
```
Returns recent significant mood changes (last 20).

**Full API Docs:** [http://localhost:8001/docs](http://localhost:8001/docs) (interactive Swagger UI)

---

## UI Components

### WorldMap Component
3D interactive globe with:
- Mapbox GL globe projection
- Starfield background (1000 stars with parallax)
- Country click handlers
- Hover tooltips
- Smooth camera transitions

### CountryPanel Component
Slide-in detail panel featuring:
- Mood score gauge
- Audio feature bars
- 7-day trend chart (Recharts)
- News headlines list
- Gemini AI insight card
- Spike indicators

### GlobalStats Component
Collapsible statistics widget:
- Total countries tracked
- Dominant mood calculation
- Mood distribution pie chart
- Average valence & energy

### SpikeAlert Component
Real-time alert widget:
- Badge with spike count
- Expandable list (top 5)
- Mood transition arrows
- Delta values
- Timestamps

---

## Configuration

### Docker Services

| Service | Internal Port | External Port | Description |
|---------|---------------|---------------|-------------|
| `postgres` | 5432 | 5433 | PostgreSQL 16 database |
| `redis` | 6379 | 6380 | Redis 7 cache |
| `backend` | 8000 | 8001 | FastAPI application |
| `frontend` | 3000 | 3001 | Next.js application |

### Environment Variables Reference

**Backend** (`backend/.env`):
```env
# Database
DATABASE_URL=postgresql+asyncpg://worldmood:worldmood@postgres:5432/worldmood
REDIS_URL=redis://redis:6379/0

# APIs
GEMINI_API_KEY=<your-key>
LASTFM_API_KEY=<your-key>
NEWS_API_KEY=<optional>

# App
DEBUG=true
MUSIC_PROVIDER=lastfm
CORS_ORIGINS=["http://localhost:3001"]
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_MAPBOX_TOKEN=<your-token>
NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

## Data Pipeline

### Daily Ingestion (`daily_ingest.py`)

Automated workflow:

1. **Fetch Music Data** (Last.fm API)
   - Top 50 tracks per country
   - Extract audio features
   - Calculate aggregated metrics

2. **Fetch News Data** (Google News RSS)
   - Country-specific headlines (5 per country)
   - Sentiment analysis via Gemini AI

3. **Compute Mood**
   - Apply weighted formula
   - Assign label and color
   - Store in database

4. **Detect Spikes**
   - Compare with 7-day history
   - Z-score analysis
   - Save anomalies

5. **Generate AI Summaries**
   - Send headlines + mood to Gemini
   - Store 1-2 sentence explanation

**Schedule:** Run daily via cron:
```bash
# Add to crontab
0 0 * * * cd /path/to/backend && docker-compose exec backend python scripts/daily_ingest.py
```

---

## Development

### Running Locally (Without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start PostgreSQL & Redis locally
# Then:
uvicorn app.main:app --reload --port 8001
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
# Create new migration
docker-compose exec backend python scripts/create_migration.py "Add new field"

# Apply migrations
docker-compose exec backend python scripts/run_migrations.py

# Or use Alembic directly
docker-compose exec backend alembic upgrade head
```

### Debugging

```bash
# Check database status
docker-compose exec backend python scripts/check_db.py

# View backend logs
docker-compose logs -f backend

# Access database
docker-compose exec postgres psql -U worldmood -d worldmood

# Access Redis CLI
docker-compose exec redis redis-cli
```

---

## Troubleshooting

### Frontend shows no colors

**Solution:**
```bash
# 1. Check if data exists
docker-compose exec postgres psql -U worldmood -d worldmood -c "SELECT COUNT(*) FROM country_mood;"

# 2. If empty, run ingestion
docker-compose exec backend python scripts/daily_ingest.py

# 3. Hard refresh browser
# Press: Ctrl + Shift + R (Windows/Linux) or Cmd + Shift + R (Mac)
```

### Backend API not responding

**Solution:**
```bash
# Check backend status
docker-compose ps backend

# View logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Database connection errors

**Solution:**
```bash
# Check PostgreSQL status
docker-compose ps postgres

# Verify connection
docker-compose exec backend python -c "from app.db.session import engine; print('OK')"

# Check DATABASE_URL in .env
cat backend/.env | grep DATABASE_URL
```

### Gemini AI summaries not showing

**Solution:**
```bash
# 1. Verify API key is set
cat backend/.env | grep GEMINI_API_KEY

# 2. Check Gemini API quota at https://makersuite.google.com/

# 3. Re-run ingestion
docker-compose exec backend python scripts/daily_ingest.py
```

### Port conflicts

**Solution:**
```bash
# Check what's using ports
lsof -i :3001  # Frontend
lsof -i :8001  # Backend
lsof -i :5433  # PostgreSQL
lsof -i :6380  # Redis

# Kill process or change ports in docker-compose.yml
```

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Mapbox GL JS API](https://docs.mapbox.com/mapbox-gl-js/)
- [Last.fm API Documentation](https://www.last.fm/api)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## Security Best Practices

### Production Checklist

- [ ] Change database password in `docker-compose.yml`
- [ ] Set `DEBUG=false` in `backend/.env`
- [ ] Configure allowed CORS origins (remove `localhost`)
- [ ] Use environment secrets manager (AWS Secrets Manager, HashiCorp Vault)
- [ ] Enable SSL/TLS for database connections
- [ ] Set up rate limiting on API endpoints
- [ ] Configure firewall rules (allow only necessary ports)
- [ ] Use reverse proxy (Nginx) with SSL certificate
- [ ] Enable Docker secrets for sensitive data
- [ ] Implement API key rotation schedule
- [ ] Set up monitoring and alerting (Sentry, Datadog)
- [ ] Regular security audits (`npm audit`, `safety check`)

### Never Commit
- `backend/.env`
- `frontend/.env.local`
- API keys or tokens
- Database credentials

---

## Contributing

We welcome contributions! Here's how:

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m "Add amazing feature"
   ```
4. **Push** to the branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Contribution Guidelines
- Follow existing code style (PEP 8 for Python, Prettier for TypeScript)
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Last.fm](https://www.last.fm/) for music data API
- [Google](https://ai.google.dev/) for Gemini AI
- [Mapbox](https://www.mapbox.com/) for geospatial visualization
- [FastAPI](https://fastapi.tiangolo.com/) community for excellent documentation
- [Next.js](https://nextjs.org/) team for React framework

---

## Support

Need help? Try these resources:

1. **Check Documentation** - Review this README and API docs
2. **View Logs** - `docker-compose logs -f`
3. **Run Diagnostics** - `python scripts/check_db.py`
4. **Search Issues** - Check existing GitHub issues
5. **Open Issue** - Create new issue with:
   - Description of problem
   - Steps to reproduce
   - Environment details
   - Relevant logs

---

## Roadmap

- [ ] User authentication and personalized dashboards
- [ ] Historical mood playback (time machine)
- [ ] Export data to CSV/JSON
- [ ] Mobile app (React Native)
- [ ] Additional data sources (Twitter, Reddit)
- [ ] Machine learning predictions
- [ ] Multi-language support
- [ ] Real-time WebSocket updates
- [ ] Country comparison views
- [ ] Embeddable widgets
