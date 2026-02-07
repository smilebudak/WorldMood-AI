# 🚀 MoodAtlas - Quick Start Guide

## Backend Developer - Hızlı Başlangıç

Arkadaşın Last.fm entegrasyonunu ekledi. İşte kurulum adımları:

---

## ⚡ 1 Dakikada Başla

### 1️⃣ .env Dosyasını Oluştur

```bash
cd /Users/ismailbudak/Desktop/WorldMood-AI
cp .env.example .env
nano .env
```

**`.env` içeriği:**
```env
DATABASE_URL=postgresql+asyncpg://moodatlas:moodatlas@localhost:5432/moodatlas
REDIS_URL=redis://localhost:6379/0
LASTFM_API_KEY=your_lastfm_api_key_here
```

---

### 2️⃣ PostgreSQL'i Hazırla

```bash
# PostgreSQL başlat (macOS)
brew services start postgresql@16

# Database oluştur
psql -U postgres -f backend/init_db.sql
```

**Veya otomatik script:**
```bash
./setup_database.sh
```

---

### 3️⃣ Dependencies'leri Yükle

```bash
cd backend
pip3 install -r requirements.txt
```

**requirements.txt içeriği:**
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

### 4️⃣ Migration'ları Çalıştır

```bash
cd backend
python3 scripts/run_migrations.py
```

**Çıktı:**
```
🔄 MoodAtlas Database Migration
============================================================
📍 Mevcut migration durumu:
...
⬆️  Migration'lar uygulanıyor...
✅ Migration'lar başarıyla uygulandı!
```

---

### 5️⃣ Backend'i Başlat

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Beklenen çıktı:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database tables ensured.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### 6️⃣ Test Et!

Backend ayağa kalktıktan sonra:

```bash
# Health check
curl http://localhost:8000/health

# Last.fm'den gerçek veri
curl http://localhost:8000/mood/global
```

**Beklenen response:**
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

## 🐘 pgAdmin'de Kontrol Et

### 1. pgAdmin'i Aç
```bash
brew install --cask pgadmin4
pgadmin4
```

### 2. Server Ekle

**General:**
- Name: `MoodAtlas`

**Connection:**
- Host: `localhost`
- Port: `5432`
- Database: `moodatlas`
- Username: `moodatlas`
- Password: `moodatlas`

### 3. Tabloları Gör

Sol panelde:
```
Servers → MoodAtlas → Databases → moodatlas 
  → Schemas → public → Tables
    ├── country_mood  ← Mood verileri
    └── mood_spike    ← Mood değişimleri
```

---

## 🔄 Verileri Doldur (Opsiyonel)

### Günlük Veri Toplama:

```bash
cd backend
python3 scripts/daily_ingest.py
```

Bu script:
- Last.fm'den tüm ülkeler için veri çeker
- Mood hesaplar
- Database'e kayeder
- Spike'ları tespit eder

---

## 📊 Önemli Endpointler

| Endpoint | Metod | Açıklama |
|----------|-------|----------|
| `/health` | GET | Sağlık kontrolü |
| `/mood/global` | GET | Tüm ülkelerin anlık mood'u (Last.fm'den) |
| `/country/{code}/mood` | GET | Belirli ülkenin mood detayı |
| `/country/{code}/trend` | GET | Ülkenin 7 günlük trend'i |
| `/spikes` | GET | Son mood spike'ları |

---

## 🔍 Sorun Giderme

### PostgreSQL Bağlantı Hatası

```bash
# Servis çalışıyor mu?
pg_isready

# Database var mı?
psql -U postgres -l | grep moodatlas

# Yoksa oluştur
psql -U postgres -f backend/init_db.sql
```

### Alembic Hatası

```bash
# Alembic kurulu mu?
python3 -m alembic --version

# Yoksa yükle
pip3 install alembic psycopg2-binary

# Migration durumu
cd backend
python3 -m alembic current
```

### Last.fm API Hatası

**Hata:** `LASTFM_API_KEY not configured`

**Çözüm:** `.env` dosyasında API key'i kontrol et:
```env
LASTFM_API_KEY=your_lastfm_api_key_here
```

### Port Zaten Kullanımda

```bash
# 8000 portunu kim kullanıyor?
lsof -i :8000

# Eğer eski process varsa öldür
kill -9 <PID>
```

---

## 📁 Proje Yapısı

```
WorldMood-AI/
├── .env                    ← API keys burada
├── backend/
│   ├── alembic/            ← Migration dosyaları
│   │   └── versions/
│   │       └── 001_initial.py
│   ├── app/
│   │   ├── api/routes/
│   │   │   └── mood.py     ← /mood/global endpoint
│   │   ├── services/
│   │   │   └── lastfm_service.py  ← Last.fm entegrasyonu
│   │   ├── core/
│   │   │   └── mood_engine.py     ← Mood hesaplama
│   │   ├── db/
│   │   │   └── models.py          ← Database modelleri
│   │   └── main.py                ← FastAPI app
│   └── scripts/
│       ├── run_migrations.py      ← Migration runner
│       └── check_db.py            ← Database kontrolü
└── frontend/
    └── ...
```

---

## 🎯 Ne Değişti?

Arkadaşın yaptığı değişikler:

1. **Last.fm Entegrasyonu**
   - ✅ `lastfm_service.py` eklendi
   - ✅ Tag-based mood feature extraction
   - ✅ 31 ülke desteği

2. **Config Güncellemesi**
   - ✅ `MUSIC_PROVIDER=lastfm`
   - ✅ `LASTFM_API_KEY` eklendi

3. **Endpoint Değişikliği**
   - ✅ `/mood/global` artık Last.fm'den gerçek veri döndürüyor
   - ✅ Cache mekanizması (Redis)
   - ✅ On-the-fly mood hesaplama

---

## 🚀 Production'a Alma

### 1. Environment Değişkenleri

```env
DATABASE_URL=postgresql+asyncpg://moodatlas:GÜÇLÜ_ŞİFRE@production-host:5432/moodatlas
REDIS_URL=redis://production-redis:6379/0
LASTFM_API_KEY=YOUR_PRODUCTION_KEY
DEBUG=False
```

### 2. Migration

```bash
cd backend
python3 scripts/run_migrations.py
```

### 3. Gunicorn ile Başlat

```bash
pip3 install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. Docker ile (Önerilen)

```bash
docker-compose up -d
```

---

## 📚 İlgili Dokümantasyon

- **[DATABASE_DESIGN.md](DATABASE_DESIGN.md)** - Detaylı database schema
- **[PGADMIN_REHBERI.md](PGADMIN_REHBERI.md)** - pgAdmin kullanımı
- **[MIGRATION_REHBERI.md](MIGRATION_REHBERI.md)** - Migration detayları
- **[HIZLI_BASLANGIC.md](HIZLI_BASLANGIC.md)** - pgAdmin hızlı başlangıç

---

## ✅ Checklist

Başlamadan önce kontrol et:

- [ ] PostgreSQL 16+ kurulu
- [ ] Python 3.11+ kurulu
- [ ] `.env` dosyası oluşturuldu
- [ ] `LASTFM_API_KEY` girildi
- [ ] PostgreSQL servisi çalışıyor
- [ ] Database `moodatlas` oluşturuldu
- [ ] Dependencies yüklendi (`pip3 install -r requirements.txt`)
- [ ] Migration'lar uygulandı
- [ ] Backend başlatıldı
- [ ] `/mood/global` endpoint'i test edildi

---

**🎉 Tebrikler! Backend hazır. Last.fm'den gerçek veri çekmeye başladı!**
