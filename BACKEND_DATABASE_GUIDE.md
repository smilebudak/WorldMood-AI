# 🔧 Backend Developer Guide - Database Connection

## 📝 Özet

PostgreSQL database'i hazırlandı. Backend developer'ın yapması gerekenler:

### ✅ Yapılması Gerekenler:

1. **PostgreSQL'i çalıştır ve init script'i uygula**
2. **`.env` dosyasını oluştur ve DATABASE_URL'i güncelle**
3. **Tabloları oluştur** (otomatik script ile)
4. **Backend'i başlat ve test et**

---

## 🚀 Hızlı Başlangıç

### Seçenek 1: Docker ile (Önerilen - En Kolay)

```bash
# 1. .env dosyası oluştur
cp .env.example .env

# 2. Tüm servisleri başlat (PostgreSQL + Redis + Backend + Frontend)
docker-compose up -d

# 3. Backend loglarını izle
docker-compose logs -f backend

# 4. Tabloları oluştur (ilk çalıştırmada)
docker-compose exec backend python scripts/create_tables.py

# 5. Database durumunu kontrol et
docker-compose exec backend python scripts/check_db.py
```

✅ **Docker ile hiçbir şey değiştirmeye gerek yok!** DATABASE_URL zaten doğru yapılandırılmış.

---

### Seçenek 2: Manuel PostgreSQL Sunucusu ile

#### 1️⃣ PostgreSQL'i Kur ve Başlat

```bash
# macOS
brew install postgresql@16
brew services start postgresql@16

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql-16
sudo systemctl start postgresql

# Uzak sunucu
ssh user@sunucu_ip
sudo systemctl start postgresql
```

#### 2️⃣ Database'i Oluştur

```bash
# init_db.sql script'ini çalıştır
psql -U postgres -f backend/init_db.sql

# Veya PostgreSQL içinden:
psql -U postgres
\i backend/init_db.sql
```

Script şunları yapar:
- ✅ `moodatlas` kullanıcısı oluşturur (şifre: `moodatlas`)
- ✅ `moodatlas` database'i oluşturur
- ✅ `country_mood` ve `mood_spike` tablolarını oluşturur
- ✅ İndeksleri ve izinleri ayarlar

#### 3️⃣ .env Dosyasını Yapılandır

```bash
# .env.example'ı kopyala
cp .env.example .env

# .env dosyasını düzenle
nano .env  # veya vim, vscode, vb.
```

**`.env` içindeki DATABASE_URL'i güncelle:**

```env
# Yerel PostgreSQL
DATABASE_URL=postgresql+asyncpg://moodatlas:moodatlas@localhost:5432/moodatlas

# Uzak sunucu (örnek)
DATABASE_URL=postgresql+asyncpg://moodatlas:moodatlas@192.168.1.100:5432/moodatlas

# Domain ile
DATABASE_URL=postgresql+asyncpg://moodatlas:moodatlas@db.example.com:5432/moodatlas
```

**Format:**
```
postgresql+asyncpg://[kullanıcı]:[şifre]@[host]:[port]/[database_adı]
```

#### 4️⃣ Tabloları Oluştur (İlk Sefer)

```bash
cd backend

# Python environment'ı aktifleştir (varsa)
# source venv/bin/activate

# Tabloları oluştur
python scripts/create_tables.py
```

Çıktı şöyle olmalı:
```
🗄️  MoodAtlas Database Initialization
============================================================
📍 Database URL: localhost:5432/moodatlas
============================================================

🔌 Database bağlantısı test ediliyor...
✅ Bağlantı başarılı!
📦 PostgreSQL version: PostgreSQL 16.x

🔍 Mevcut tabloları kontrol ediliyor...
✅ Tablolar başarıyla oluşturuldu!

📋 Oluşturulan tablolar:
   • country_mood
   • mood_spike

📊 Toplam tablo sayısı: 2

✨ Kurulum tamamlandı!
```

#### 5️⃣ Database Durumunu Kontrol Et

```bash
# Database durumunu kontrol et
python scripts/check_db.py
```

#### 6️⃣ Backend'i Başlat

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🔍 Sorun Giderme

### ❌ "could not connect to server"

```bash
# PostgreSQL çalışıyor mu?
# macOS:
brew services list | grep postgresql

# Linux:
sudo systemctl status postgresql

# Başlat:
# macOS:
brew services start postgresql@16

# Linux:
sudo systemctl start postgresql
```

### ❌ "database 'moodatlas' does not exist"

```bash
# init_db.sql'i tekrar çalıştır
psql -U postgres -f backend/init_db.sql
```

### ❌ "password authentication failed"

`.env` dosyasındaki şifreyi kontrol et. Varsayılan: `moodatlas`

```bash
# Şifreyi PostgreSQL'de değiştir
psql -U postgres
ALTER USER moodatlas WITH PASSWORD 'yeni_şifre';
```

### ❌ "relation 'country_mood' does not exist"

```bash
# Tabloları oluştur
python scripts/create_tables.py
```

### 🔒 Firewall/Port Problemi

```bash
# PostgreSQL portuna erişim var mı?
telnet localhost 5432
# veya
nc -zv localhost 5432

# Firewall'da 5432 portunu aç (uzak sunucu için)
sudo ufw allow 5432/tcp

# PostgreSQL'in dışarıdan bağlantı kabul ettiğinden emin ol
# postgresql.conf:
# listen_addresses = '*'

# pg_hba.conf: (GÜVENLİK UYARISI - production'da IP kısıtla!)
# host    all    all    0.0.0.0/0    md5
```

---

## 📊 Faydalı Komutlar

### Python Scripts

```bash
# Database durumu
python scripts/check_db.py

# Tabloları oluştur
python scripts/create_tables.py

# Günlük veri toplama (cron job için)
python scripts/daily_ingest.py
```

### SQL Komutları

```bash
# PostgreSQL'e bağlan
psql -U moodatlas -d moodatlas

# Tabloları listele
\dt

# Tablo yapısı
\d country_mood
\d mood_spike

# Son kayıtlar
SELECT * FROM country_mood ORDER BY created_at DESC LIMIT 5;
SELECT * FROM mood_spike ORDER BY detected_at DESC LIMIT 5;

# İstatistikler
SELECT 
    country_code, 
    COUNT(*) as total_records,
    MAX(created_at) as latest_record
FROM country_mood 
GROUP BY country_code 
ORDER BY total_records DESC;

# Database boyutu
SELECT pg_size_pretty(pg_database_size('moodatlas'));
```

---

## 🔐 Güvenlik Notları

### Production İçin MUTLAKA Değiştir:

1. **Şifreleri güçlendir:**
```sql
ALTER USER moodatlas WITH PASSWORD 'çok_güçlü_şifre_123!@#$';
```

2. **`.env` dosyasını güncelle:**
```env
DATABASE_URL=postgresql+asyncpg://moodatlas:çok_güçlü_şifre_123!@#$@host:5432/moodatlas
```

3. **Firewall konfigürasyonu:**
```bash
# Sadece belirli IP'lerden erişime izin ver
# pg_hba.conf:
host    moodatlas    moodatlas    10.0.1.0/24    md5  # Sadece bu subnet
```

4. **SSL kullan:**
```env
DATABASE_URL=postgresql+asyncpg://moodatlas:password@host:5432/moodatlas?ssl=require
```

---

## 📞 İletişim

Database kurulumunda sorun yaşarsanız:

1. **Logları kontrol et:**
   - Backend logs: `docker-compose logs backend`
   - PostgreSQL logs: `/var/log/postgresql/`

2. **Debug mode aç:**
   ```env
   # .env dosyasında
   DEBUG=True
   ```

3. **Bağlantıyı test et:**
   ```bash
   python scripts/check_db.py
   ```

---

## 📚 Ek Kaynaklar

- [DATABASE_SETUP.md](DATABASE_SETUP.md) - Detaylı kurulum rehberi
- [backend/init_db.sql](backend/init_db.sql) - SQL initialization script
- [backend/app/db/models.py](backend/app/db/models.py) - SQLAlchemy modelleri
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**✨ Başarılı kurulum sonrası API endpoints test edilebilir:**

```bash
# Health check
curl http://localhost:8000/health

# Country moods
curl http://localhost:8000/api/country/US/mood

# Mood spikes
curl http://localhost:8000/api/spikes
```
