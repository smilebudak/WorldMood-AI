# 🗄️ PostgreSQL Database Kurulumu - Hızlı Başvuru

## 📁 Oluşturulan Dosyalar

```
WorldMood-AI/
├── setup_database.sh              # 🚀 Otomatik kurulum scripti
├── DATABASE_SETUP.md              # 📚 Detaylı kurulum dokümantasyonu  
├── BACKEND_DATABASE_GUIDE.md      # 🔧 Backend developer rehberi
├── .env.example                   # ⚙️  Environment template (güncellenmiş)
└── backend/
    ├── init_db.sql               # 💾 PostgreSQL initialization script
    └── scripts/
        ├── create_tables.py      # 📊 Tabloları otomatik oluştur
        └── check_db.py           # 🔍 Database durumunu kontrol et
```

---

## ⚡ Hızlı Kurulum

### Yöntem 1: Otomatik Script (En Hızlı)

```bash
./setup_database.sh
```

Bu script otomatik olarak:
- ✅ PostgreSQL'i kontrol eder ve başlatır
- ✅ Database ve kullanıcıyı oluşturur
- ✅ Tabloları ve indeksleri oluşturur
- ✅ `.env` dosyasını hazırlar
- ✅ Kurulumu doğrular

---

### Yöntem 2: Docker Compose (Önerilen)

```bash
# 1. .env dosyası oluştur
cp .env.example .env

# 2. Tüm servisleri başlat
docker-compose up -d

# 3. Tabloları oluştur
docker-compose exec backend python scripts/create_tables.py

# 4. Durumu kontrol et
docker-compose exec backend python scripts/check_db.py
```

---

### Yöntem 3: Manuel Kurulum

```bash
# 1. Database'i oluştur
psql -U postgres -f backend/init_db.sql

# 2. .env yapılandır
cp .env.example .env
nano .env  # DATABASE_URL'i güncelle

# 3. Tabloları oluştur
cd backend
python scripts/create_tables.py

# 4. Durumu kontrol et
python scripts/check_db.py
```

---

## 🔧 Database URL Formatı

### Docker ile:
```env
DATABASE_URL=postgresql+asyncpg://moodatlas:moodatlas@postgres:5432/moodatlas
```

### Yerel PostgreSQL:
```env
DATABASE_URL=postgresql+asyncpg://moodatlas:moodatlas@localhost:5432/moodatlas
```

### Uzak Sunucu:
```env
DATABASE_URL=postgresql+asyncpg://moodatlas:moodatlas@<SUNUCU_IP>:5432/moodatlas
```

**Not:** `<SUNUCU_IP>` yerine gerçek IP adresini yazın (örn: `192.168.1.100`)

---

## 📊 Database Şeması

### country_mood Tablosu
```sql
- id (SERIAL PRIMARY KEY)
- country_code (VARCHAR(3))      -- "US", "TR", vb.
- country_name (VARCHAR(120))
- date (TIMESTAMP)
- mood_score (FLOAT)             -- -1.0 to 1.0
- mood_label (VARCHAR(20))       -- "Happy", "Sad", vb.
- color_code (VARCHAR(7))        -- Hex color
- valence, energy, danceability, acousticness (FLOAT)
- top_genre, top_track (VARCHAR)
- news_sentiment (FLOAT)
- created_at (TIMESTAMP)
- UNIQUE(country_code, date)
```

### mood_spike Tablosu
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

## 🛠️ Faydalı Komutlar

### Python Scripts
```bash
# Tabloları oluştur
python backend/scripts/create_tables.py

# Database durumu
python backend/scripts/check_db.py

# Günlük veri toplama
python backend/scripts/daily_ingest.py
```

### SQL Komutları
```bash
# Database'e bağlan
psql -U moodatlas -d moodatlas

# Tabloları listele
\dt

# Veri kontrolü
SELECT COUNT(*) FROM country_mood;
SELECT COUNT(*) FROM mood_spike;

# Son kayıtlar
SELECT * FROM country_mood ORDER BY created_at DESC LIMIT 5;
```

### Docker Komutları
```bash
# Servisleri başlat
docker-compose up -d

# Backend logs
docker-compose logs -f backend

# PostgreSQL'e bağlan
docker-compose exec postgres psql -U moodatlas -d moodatlas

# Backend içinde komut çalıştır
docker-compose exec backend python scripts/check_db.py
```

---

## 🔍 Sorun Giderme

| Hata | Çözüm |
|------|-------|
| `could not connect to server` | `pg_isready` ile servisi kontrol et, gerekirse başlat |
| `database does not exist` | `psql -U postgres -f backend/init_db.sql` çalıştır |
| `password authentication failed` | `.env` dosyasındaki şifreyi kontrol et |
| `relation does not exist` | `python scripts/create_tables.py` çalıştır |
| Port 5432 kullanımda | `lsof -i :5432` ile kontrol et |

---

## 📚 Dokümantasyon

- **[BACKEND_DATABASE_GUIDE.md](BACKEND_DATABASE_GUIDE.md)** - Backend developer için detaylı rehber
- **[DATABASE_SETUP.md](DATABASE_SETUP.md)** - Kapsamlı kurulum ve yönetim dokümantasyonu
- **[backend/init_db.sql](backend/init_db.sql)** - SQL initialization script

---

## 🔐 Güvenlik Notları

**Production için MUTLAKA:**

1. **Şifreleri değiştir:**
```sql
ALTER USER moodatlas WITH PASSWORD 'güçlü_şifre_123!';
```

2. **`.env` dosyasını git'e ekleme:**
```bash
# .gitignore'da olduğundan emin ol
echo ".env" >> .gitignore
```

3. **Firewall yapılandır:**
```bash
# Sadece belirli IP'lerden erişime izin ver
sudo ufw allow from 10.0.0.0/24 to any port 5432
```

4. **SSL kullan:**
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
```

---

## ✅ Backend Developer Checklist

Backend geliştirici için yapılacaklar:

- [ ] PostgreSQL kurulu ve çalışıyor
- [ ] `init_db.sql` çalıştırıldı
- [ ] `.env` dosyası oluşturuldu
- [ ] `DATABASE_URL` doğru sunucu IP'si ile güncellendi
- [ ] `python scripts/create_tables.py` çalıştırıldı
- [ ] `python scripts/check_db.py` ile doğrulandı
- [ ] API anahtarları `.env`'e eklendi (SPOTIFY, NEWS_API, vb.)
- [ ] Backend başlatıldı ve test edildi
- [ ] Health check endpoint çalışıyor (`/health`)

---

## 🚀 Başlatma

```bash
# Backend'i başlat
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Veya Docker ile tüm stack'i başlat
docker-compose up
```

**API Test:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/country/US/mood
```

---

## 📞 Yardım

Sorun yaşarsanız:

1. Logları kontrol edin
2. `python scripts/check_db.py` çalıştırın
3. `.env` dosyasında `DEBUG=True` yapın
4. [DATABASE_SETUP.md](DATABASE_SETUP.md) sorun giderme bölümüne bakın

---

**Created: 2026-02-07**  
**Version: 1.0**  
**PostgreSQL: 16+**  
**SQLAlchemy: 2.0+**
