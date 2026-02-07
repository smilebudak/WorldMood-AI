# ⚡ Hızlı Başlangıç - pgAdmin ve Migration

## 🎯 pgAdmin'de Tabloları Görme

### 1. pgAdmin'i Aç
```bash
# macOS
brew install --cask pgadmin4

# Uygulamayı başlat
pgadmin4
```

### 2. Server Bağlantısı Kur

**Servers → Sağ tık → Create → Server**

```
General:
  Name: MoodAtlas

Connection:
  Host: localhost
  Port: 5432
  Database: moodatlas
  Username: moodatlas
  Password: moodatlas
```

### 3. Tabloları Gör

Sol panelde genişlet:
```
Servers
└── MoodAtlas
    └── Databases
        └── moodatlas
            └── Schemas
                └── public
                    └── Tables  ← BURASI!
                        ├── country_mood
                        └── mood_spike
```

**Tabloya sağ tık → View/Edit Data → All Rows** → Verileri görmek için

---

## 🔄 Migration'ları Çalıştırma

### Hızlı Yol (Önerilen):

```bash
cd backend

# Migration'ları çalıştır
python scripts/run_migrations.py
```

### Manuel Yol:

```bash
cd backend

# Alembic'i başlat (sadece ilk kez)
alembic init alembic

# env.py'yi yapılandır (detaylar MIGRATION_REHBERI.md'de)
# ...

# İlk migration'ı oluştur
alembic revision --autogenerate -m "Initial schema"

# Migration'ı çalıştır
alembic upgrade head

# Durumu kontrol et
alembic current
```

### Docker ile:

```bash
# Migration'ı Docker container'da çalıştır
docker-compose exec backend alembic upgrade head
```

---

## 📊 Faydalı SQL Sorguları (pgAdmin'de)

pgAdmin'de **Query Tool** aç (`moodatlas`'a sağ tık → Query Tool):

```sql
-- Tüm tabloları listele
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- country_mood verilerini göster
SELECT * FROM country_mood 
ORDER BY created_at DESC 
LIMIT 10;

-- Ülke bazında istatistikler
SELECT 
    country_code,
    COUNT(*) as total,
    AVG(mood_score) as avg_mood
FROM country_mood
GROUP BY country_code;

-- Database boyutu
SELECT pg_size_pretty(pg_database_size('moodatlas'));
```

---

## 🚀 Yeni Tablo/Kolon Ekleme

### 1. models.py'yi Düzenle

```python
# backend/app/db/models.py
class CountryMood(Base):
    # ... mevcut kolonlar ...
    
    # YENİ KOLON EKLE
    spotify_playlist_url = Column(String(200), nullable=True)
```

### 2. Migration Oluştur

```bash
cd backend
python scripts/create_migration.py "Add spotify_playlist_url"
```

### 3. Migration'ı Çalıştır

```bash
python scripts/run_migrations.py
```

### 4. pgAdmin'de Göster

pgAdmin'de Tables → Sağ tık → **Refresh**

---

## 🔍 Sorun Giderme

### PostgreSQL Çalışmıyor

```bash
# Kontrol et
pg_isready

# Başlat
# macOS:
brew services start postgresql@16

# Docker:
docker-compose up -d postgres
```

### pgAdmin Bağlanamıyor

```bash
# Database durumunu kontrol et
python backend/scripts/check_db.py

# .env dosyasını kontrol et
cat .env | grep DATABASE_URL
```

### Migration Hatası

```bash
# Mevcut durumu işaretle
cd backend
alembic stamp head

# Tekrar dene
alembic upgrade head
```

---

## 📚 Detaylı Dokümantasyon

- **[PGADMIN_REHBERI.md](PGADMIN_REHBERI.md)** - pgAdmin detaylı kullanım
- **[MIGRATION_REHBERI.md](MIGRATION_REHBERI.md)** - Migration detayları
- **[DATABASE_README.md](DATABASE_README.md)** - Database genel bilgi

---

## ✅ Checklist

- [ ] pgAdmin kuruldu
- [ ] Server bağlantısı yapıldı
- [ ] Tablolar görüntülendi
- [ ] Alembic kuruldu ve yapılandırıldı
- [ ] İlk migration oluşturuldu
- [ ] Migration başarıyla çalıştırıldı

---

**Her şey hazır! pgAdmin'de tablolarını görebilir ve migration'larla yönetebilirsin! 🎉**
