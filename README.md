# 🌍 MoodAtlas AI

Real-time global mood visualization powered by music trends, news sentiment, and social data.

---

## 🚀 Quick Start

### With Docker (Recommended)

```bash
# 1. Clone repository
git clone <repo-url>
cd WorldMood-AI

# 2. Create environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Initialize database tables
docker-compose exec backend python scripts/create_tables.py

# 5. Open application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

See [DATABASE_README.md](DATABASE_README.md) for detailed setup instructions.

---

## 📁 Project Structure

```
WorldMood-AI/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # REST API endpoints
│   │   ├── core/        # Business logic (mood engine, spike detector)
│   │   ├── db/          # Database models and sessions
│   │   ├── models/      # Pydantic schemas
│   │   └── services/    # External integrations (Spotify, News, Trends)
│   ├── scripts/         # Utility scripts
│   │   ├── create_tables.py    # Initialize database
│   │   ├── check_db.py         # Verify database status
│   │   └── daily_ingest.py     # Daily data collection cron job
│   └── init_db.sql      # PostgreSQL schema
│
├── frontend/            # Next.js frontend
│   ├── app/
│   │   ├── components/  # React components
│   │   │   ├── WorldMap.tsx
│   │   │   ├── CountryPanel.tsx
│   │   │   └── SpikeAlert.tsx
│   │   └── lib/         # Utilities and API client
│   └── styles/
│
├── docker-compose.yml   # Multi-container setup
├── .env.example         # Environment template
│
└── Documentation/
    ├── DATABASE_README.md             # Quick reference
    ├── BACKEND_DATABASE_GUIDE.md      # Backend developer guide
    ├── DATABASE_SETUP.md              # Comprehensive setup docs
    └── DATABASE_KURULUM_OZET.txt      # Turkish summary
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL 16** - Primary database
- **SQLAlchemy 2.0** - ORM with async support
- **Redis** - Caching layer
- **asyncpg** - Async PostgreSQL driver

### Frontend
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Mapbox GL** - Interactive maps

### Data Sources
- **Spotify API** - Music trends and audio features
- **News API** - Sentiment analysis
- **Google Trends** - Search trends (optional)

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Database (required)
DATABASE_URL=postgresql+asyncpg://moodatlas:moodatlas@localhost:5432/moodatlas

# Redis (required)
REDIS_URL=redis://localhost:6379/0

# Spotify (required for music data)
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret

# News API (required for sentiment)
NEWS_API_KEY=your_api_key

# Mapbox (required for frontend maps)
MAPBOX_TOKEN=your_mapbox_token
NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token

# API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Getting API Keys

1. **Spotify**: [Developer Dashboard](https://developer.spotify.com/dashboard)
2. **News API**: [NewsAPI.org](https://newsapi.org/register)
3. **Mapbox**: [Mapbox Account](https://account.mapbox.com/)

---

## 🗄️ Database Setup

### Automated Setup

```bash
./setup_database.sh
```

### Manual Setup

```bash
# 1. Create database
psql -U postgres -f backend/init_db.sql

# 2. Create tables
cd backend
python scripts/create_tables.py

# 3. Verify
python scripts/check_db.py
```

**Detailed instructions:** [DATABASE_README.md](DATABASE_README.md)

---

## 📊 Database Schema

### `country_mood` Table
Stores daily mood snapshots per country.

| Column | Type | Description |
|--------|------|-------------|
| `country_code` | VARCHAR(3) | ISO country code |
| `mood_score` | FLOAT | Mood value (-1 to 1) |
| `mood_label` | VARCHAR(20) | Happy, Sad, Calm, Anxious, Angry |
| `color_code` | VARCHAR(7) | Hex color for visualization |
| `valence`, `energy` | FLOAT | Spotify audio features |
| `news_sentiment` | FLOAT | News sentiment score |

### `mood_spike` Table
Tracks significant mood changes.

| Column | Type | Description |
|--------|------|-------------|
| `country_code` | VARCHAR(3) | ISO country code |
| `previous_label` | VARCHAR(20) | Previous mood |
| `new_label` | VARCHAR(20) | New mood |
| `delta` | FLOAT | Change magnitude |
| `reason` | TEXT | Detected cause |

---

## 🚀 Running the Application

### Development Mode

```bash
# Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend
npm run dev
```

### Production Mode

```bash
# Using Docker Compose
docker-compose up -d

# Or build separately
cd backend && docker build -t moodatlas-backend .
cd frontend && docker build -t moodatlas-frontend .
```

---

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Country Mood
```bash
GET /api/country/{country_code}/mood
```

### Mood Spikes
```bash
GET /api/spikes
```

### Full API Documentation
Visit `http://localhost:8000/docs` after starting the backend.

---

## 🔄 Data Ingestion

### Manual Run
```bash
cd backend
python scripts/daily_ingest.py
```

### Automated (Cron Job)
```bash
# Add to crontab
0 0 * * * cd /path/to/backend && python scripts/daily_ingest.py
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🐳 Docker Services

| Service | Port | Description |
|---------|------|-------------|
| `postgres` | 5432 | PostgreSQL database |
| `redis` | 6379 | Cache layer |
| `backend` | 8000 | FastAPI application |
| `frontend` | 3000 | Next.js application |

### Docker Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart service
docker-compose restart backend

# Stop all
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 🔒 Security Notes

### Production Checklist

- [ ] Change default database password
- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure CORS origins properly
- [ ] Use SSL/TLS for database connections
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Secure API keys (use secrets manager)
- [ ] Never commit `.env` to version control

---

## 📚 Documentation

- **[HIZLI_BASLANGIC.md](HIZLI_BASLANGIC.md)** - 🎯 pgAdmin ve Migration hızlı başlangıç
- **[PGADMIN_REHBERI.md](PGADMIN_REHBERI.md)** - 🐘 pgAdmin detaylı kullanım rehberi
- **[MIGRATION_REHBERI.md](MIGRATION_REHBERI.md)** - 🔄 Alembic migration dokümantasyonu
- **[DATABASE_README.md](DATABASE_README.md)** - Database quick reference
- **[BACKEND_DATABASE_GUIDE.md](BACKEND_DATABASE_GUIDE.md)** - Backend developer guide
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Comprehensive database docs
- **[DATABASE_KURULUM_OZET.txt](DATABASE_KURULUM_OZET.txt)** - Turkish setup summary

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL status
pg_isready

# Check connection from Python
python -c "from app.db.session import engine; print('OK')"

# View database status
python backend/scripts/check_db.py
```

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend
lsof -i :5432  # PostgreSQL
```

### Docker Issues

```bash
# Reset everything
docker-compose down -v
docker-compose up -d --build

# View container logs
docker-compose logs backend
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

[Add your license here]

---

## 👥 Team

- Backend Developer: Database integration, API endpoints
- Frontend Developer: UI/UX, map visualization
- Data Engineer: Ingestion pipelines, cron jobs

---

## 📞 Support

For issues or questions:
1. Check [DATABASE_SETUP.md](DATABASE_SETUP.md) troubleshooting section
2. Review logs: `docker-compose logs -f`
3. Run diagnostics: `python scripts/check_db.py`
4. Open an issue on GitHub

---

**Built with ❤️ using FastAPI, Next.js, and PostgreSQL**
