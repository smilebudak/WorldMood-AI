# 🗄️ PostgreSQL Database Kurulum Rehberi

## 📋 Gereksinimler
- PostgreSQL 12+ kurulu olmalı
- Sunucu üzerinde `psql` komutuna erişim

---

## 🚀 Kurulum Adımları

### 1️⃣ Database Oluşturma

PostgreSQL'e bağlanın ve `init_db.sql` scriptini çalıştırın:

```bash
# PostgreSQL'e root/postgres kullanıcısı ile bağlanın
psql -U postgres

# Script dosyasını çalıştırın
\i /path/to/backend/init_db.sql

# Veya doğrudan:
psql -U postgres -f backend/init_db.sql
```

Script aşağıdaki işlemleri yapar:
- ✅ `moodatlas` kullanıcısı oluşturur
- ✅ `moodatlas` database'i oluşturur
- ✅ `country_mood` ve `mood_spike` tablolarını oluşturur
- ✅ Gerekli indeksleri ekler
- ✅ İzinleri ayarlar

---

### 2️⃣ Environment Konfigürasyonu

#### Docker ile Kullanım (Önerilen)

Docker Compose kullanıyorsanız, `.env` dosyasında:

```env
DATABASE_URL=postgresql+asyncpg://moodatlas:moodatlas@postgres:5432/moodatlas
```

Docker Compose PostgreSQL servisini otomatik olarak başlatır.

#### Manuel Sunucu Kurulumu

Kendi PostgreSQL sunucunuzu kullanıyorsanız:

1. **`.env.example`'ı kopyalayın:**
```bash
cp .env.example .env
```

2. **`.env` dosyasını düzenleyin:**
```env
DATABASE_URL=postgresql+asyncpg://moodatlas:moodatlas@<SUNUCU_IP>:5432/moodatlas
```

`<SUNUCU_IP>` yerine:
- Yerel kullanım: `localhost` veya `127.0.0.1`
- Uzak sunucu: Sunucunun IP adresi (örn: `192.168.1.100`)
- Domain: Sunucu domain'i (örn: `db.example.com`)

---

### 3️⃣ Database Bağlantısını Test Etme

Backend klasöründen:

```bash
cd backend

# Python environment'ını aktifleştirin
# poetry shell  # eğer poetry kullanıyorsanız
# veya
# source venv/bin/activate  # eğer venv kullanıyorsanız

# Database bağlantısını test edin
python -c "
from app.db.session import engine
import asyncio

async def test():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('✅ Database bağlantısı başarılı!')

asyncio.run(test())
"
```

---

### 4️⃣ Alembic ile Migration (Opsiyonel)

Gelecekte schema değişiklikleri için Alembic kullanabilirsiniz:

```bash
# Migration klasörü oluştur
cd backend
alembic init alembic

# Mevcut modelleri migration olarak kaydet
alembic revision --autogenerate -m "Initial schema"

# Migration'ları uygula
alembic upgrade head
```

---

## 🔒 Güvenlik Notları

### Prodüksiyon Ortamı İçin:

1. **Güçlü şifreler kullanın:**
```sql
ALTER USER moodatlas WITH PASSWORD 'güçlü_ve_karmaşık_şifre_123!@#';
```

2. **`.env` dosyasını asla commit etmeyin:**
```bash
# .gitignore içinde olduğundan emin olun
echo ".env" >> .gitignore
```

3. **PostgreSQL firewall ayarları:**
```bash
# Sadece belirli IP'lerden erişime izin verin
# postgresql.conf ve pg_hba.conf dosyalarını yapılandırın
```

4. **SSL/TLS kullanın:**
```env
DATABASE_URL=postgresql+asyncpg://moodatlas:password@host:5432/moodatlas?ssl=require
```

---

## 🐛 Sorun Giderme

### Bağlantı Hatası: "could not connect to server"
```bash
# PostgreSQL servisini kontrol edin
sudo systemctl status postgresql

# Servisi başlatın
sudo systemctl start postgresql
```

### İzin Hatası: "permission denied"
```sql
-- PostgreSQL'de izinleri yeniden verin
GRANT ALL PRIVILEGES ON DATABASE moodatlas TO moodatlas;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO moodatlas;
```

### Port 5432 kullanımda
```bash
# Hangi processin portu kullandığını kontrol edin
lsof -i :5432
```

---

## 📊 Faydalı SQL Komutları

```sql
-- Tabloları listele
\dt

-- Tablo yapısını göster
\d country_mood
\d mood_spike

-- Mevcut verileri kontrol et
SELECT COUNT(*) FROM country_mood;
SELECT COUNT(*) FROM mood_spike;

-- En son kayıtları göster
SELECT * FROM country_mood ORDER BY created_at DESC LIMIT 5;
SELECT * FROM mood_spike ORDER BY detected_at DESC LIMIT 5;

-- Database boyutunu kontrol et
SELECT pg_size_pretty(pg_database_size('moodatlas'));
```

---

## 🔄 Backup ve Restore

### Backup Oluşturma:
```bash
pg_dump -U moodatlas -h localhost moodatlas > backup_$(date +%Y%m%d).sql
```

### Restore:
```bash
psql -U moodatlas -h localhost moodatlas < backup_20260207.sql
```

---

## 📞 Yardım

Sorun yaşarsanız:
1. PostgreSQL loglarını kontrol edin: `/var/log/postgresql/`
2. Backend loglarını kontrol edin
3. `.env` dosyasındaki `DEBUG=True` yapın ve detaylı logları inceleyin
