# 🐘 pgAdmin Kullanım Rehberi

## 📥 pgAdmin Kurulumu

### macOS
```bash
# Homebrew ile
brew install --cask pgadmin4

# Manuel indirme
# https://www.pgadmin.org/download/pgadmin-4-macos/
```

### Ubuntu/Linux
```bash
# APT ile
sudo apt install pgadmin4

# veya web versiyonu
sudo apt install pgadmin4-web
```

### Windows
[pgAdmin İndir](https://www.pgadmin.org/download/pgadmin-4-windows/)

---

## 🔌 Database Bağlantısı Kurma

### 1️⃣ pgAdmin'i Aç

pgAdmin4'ü başlat

### 2️⃣ Yeni Server Ekle

**Sol menüde:** Servers → Sağ tık → Create → Server

### 3️⃣ Genel Bilgileri Gir

**General Tab:**
```
Name: MoodAtlas Local
```

### 4️⃣ Bağlantı Bilgilerini Gir

**Connection Tab:**

#### Docker kullanıyorsan:
```
Host: localhost
Port: 5432
Maintenance database: moodatlas
Username: moodatlas
Password: moodatlas
```

#### Uzak sunucu kullanıyorsan:
```
Host: <SUNUCU_IP>  (örn: 192.168.1.100)
Port: 5432
Maintenance database: moodatlas
Username: moodatlas
Password: moodatlas
```

### 5️⃣ SSL Ayarları (Opsiyonel)

**SSL Tab:**
```
SSL Mode: Prefer
```

### 6️⃣ Kaydet

"Save" butonuna bas!

---

## 📊 Tabloları Görüntüleme

### Adım Adım:

1. **Sol panelde genişlet:**
   ```
   Servers
   └── MoodAtlas Local
       └── Databases
           └── moodatlas
               └── Schemas
                   └── public
                       └── Tables  ← BURASI!
   ```

2. **Tabloları göreceksin:**
   - `country_mood`
   - `mood_spike`

3. **Tabloya sağ tık → View/Edit Data → All Rows**
   - Tüm verileri görmek için

### Tablo Yapısını Görme:

**Tablo adına sağ tık → Properties**

Veya tablonun altındaki alt menülerden:
- **Columns** → Kolonları göster
- **Constraints** → Kısıtlamaları göster
- **Indexes** → İndeksleri göster

---

## 🔍 SQL Sorguları Çalıştırma

### Query Tool'u Aç:

1. **Sol panelde `moodatlas` database'ine sağ tık**
2. **Query Tool** seç
3. **SQL yaz ve çalıştır!**

### Örnek Sorgular:

```sql
-- Tüm tabloları listele
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- country_mood verilerini göster
SELECT * FROM country_mood 
ORDER BY created_at DESC 
LIMIT 10;

-- Ülke bazında istatistikler
SELECT 
    country_code,
    COUNT(*) as total_records,
    AVG(mood_score) as avg_mood,
    MAX(created_at) as latest_update
FROM country_mood
GROUP BY country_code
ORDER BY total_records DESC;

-- Mood spike'ları göster
SELECT * FROM mood_spike 
ORDER BY detected_at DESC;

-- Son 7 günün verileri
SELECT * FROM country_mood 
WHERE date >= NOW() - INTERVAL '7 days'
ORDER BY date DESC;
```

---

## 📈 Veri İstatistikleri

### Database Boyutu:
```sql
SELECT pg_size_pretty(pg_database_size('moodatlas')) as size;
```

### Tablo Boyutları:
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Satır Sayıları:
```sql
SELECT 
    'country_mood' as table_name,
    COUNT(*) as row_count
FROM country_mood
UNION ALL
SELECT 
    'mood_spike' as table_name,
    COUNT(*) as row_count
FROM mood_spike;
```

---

## 🔧 Tablo İşlemleri

### Yeni Kayıt Ekle:

```sql
INSERT INTO country_mood (
    country_code, 
    country_name, 
    date, 
    mood_score, 
    mood_label, 
    color_code
) VALUES (
    'TR', 
    'Turkey', 
    NOW(), 
    0.75, 
    'Happy', 
    '#FFD700'
);
```

### Kayıt Güncelle:

```sql
UPDATE country_mood 
SET mood_score = 0.80 
WHERE country_code = 'TR' 
  AND date = CURRENT_DATE;
```

### Kayıt Sil:

```sql
DELETE FROM country_mood 
WHERE country_code = 'TR' 
  AND date < NOW() - INTERVAL '30 days';
```

---

## 📊 Grafik ve Görselleştirme

pgAdmin'de **Graphs** sekmesini kullan:

1. Tabloya sağ tık → **View/Edit Data**
2. Üst menüden **Graph** ikonuna tıkla
3. X ve Y eksenlerini seç
4. Grafik türünü seç (Line, Bar, Pie, etc.)

---

## 🔐 Kullanıcı Yönetimi

### Yeni Kullanıcı Oluştur:

```sql
CREATE USER readonly WITH PASSWORD 'readonly123';
GRANT CONNECT ON DATABASE moodatlas TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

### İzinleri Görüntüle:

```sql
SELECT 
    grantee, 
    privilege_type 
FROM information_schema.role_table_grants 
WHERE table_name = 'country_mood';
```

---

## 🔄 Backup ve Restore

### Backup Alma (pgAdmin GUI):

1. Database'e sağ tık → **Backup**
2. Format: **Plain** veya **Custom**
3. Dosya adı: `moodatlas_backup_2026-02-07.sql`
4. **Backup** butonuna bas

### Restore (pgAdmin GUI):

1. Database'e sağ tık → **Restore**
2. Backup dosyasını seç
3. **Restore** butonuna bas

### Backup (Terminal):

```bash
# Plain SQL
pg_dump -U moodatlas -h localhost moodatlas > backup.sql

# Custom format (sıkıştırılmış)
pg_dump -U moodatlas -h localhost -Fc moodatlas > backup.dump

# Sadece schema (tablo yapısı)
pg_dump -U moodatlas -h localhost --schema-only moodatlas > schema.sql

# Sadece data
pg_dump -U moodatlas -h localhost --data-only moodatlas > data.sql
```

### Restore (Terminal):

```bash
# Plain SQL
psql -U moodatlas -h localhost moodatlas < backup.sql

# Custom format
pg_restore -U moodatlas -h localhost -d moodatlas backup.dump
```

---

## 📝 Import/Export

### CSV Export:

1. Tabloya sağ tık → **Import/Export**
2. **Export** seç
3. Format: **csv**
4. Dosya adını seç
5. **OK**

### CSV Import:

1. Tabloya sağ tık → **Import/Export**
2. **Import** seç
3. CSV dosyasını seç
4. Kolon eşleştirmelerini kontrol et
5. **OK**

### SQL ile Export:

```sql
COPY country_mood TO '/tmp/country_mood.csv' 
DELIMITER ',' CSV HEADER;
```

### SQL ile Import:

```sql
COPY country_mood FROM '/tmp/country_mood.csv' 
DELIMITER ',' CSV HEADER;
```

---

## 🔍 Monitoring ve Performance

### Aktif Bağlantılar:

```sql
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query
FROM pg_stat_activity
WHERE datname = 'moodatlas';
```

### Yavaş Sorgular:

```sql
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Tablo İstatistikleri:

```sql
SELECT 
    schemaname,
    tablename,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE schemaname = 'public';
```

---

## 🛠️ Sorun Giderme

### Bağlantı Hatası:

**Hata:** `could not connect to server`

**Çözüm:**
```bash
# PostgreSQL çalışıyor mu kontrol et
pg_isready

# Servisi başlat
# macOS:
brew services start postgresql@16

# Linux:
sudo systemctl start postgresql

# Docker:
docker-compose up -d postgres
```

### Şifre Hatası:

**Hata:** `password authentication failed`

**Çözüm:**
1. `.env` dosyasındaki şifreyi kontrol et
2. pgAdmin'deki şifreyi kontrol et
3. PostgreSQL'de şifreyi resetle:
```sql
ALTER USER moodatlas WITH PASSWORD 'yeni_sifre';
```

### Port Hatası:

**Hata:** `could not connect to server: Connection refused`

**Çözüm:**
```bash
# Hangi port kullanılıyor?
lsof -i :5432

# postgresql.conf'da port'u kontrol et
grep "port" /path/to/postgresql.conf
```

---

## 🎨 pgAdmin Özelleştirme

### Dark Mode:

File → Preferences → Miscellaneous → Themes → **Dark**

### Otomatik Kaydetme:

File → Preferences → Query Tool → **Auto-commit?** → **On**

### Font Boyutu:

File → Preferences → Query Tool → Font size

---

## 🚀 Kısayollar

| Kısayol | Açıklama |
|---------|----------|
| `F5` | Query'yi çalıştır |
| `F7` | Tek satırı çalıştır |
| `Ctrl/Cmd + Shift + C` | Yorum satırı |
| `Ctrl/Cmd + Space` | Auto-complete |
| `Ctrl/Cmd + S` | Kaydet |
| `F8` | Query history |

---

## 📚 Faydalı Linkler

- [pgAdmin Resmi Dökümantasyon](https://www.pgadmin.org/docs/)
- [PostgreSQL Resmi Dökümantasyon](https://www.postgresql.org/docs/)
- [SQL Tutorial](https://www.postgresqltutorial.com/)

---

## 💡 Pro Tips

1. **Query History kullan:** Geçmiş sorguları görmek için `F8`
2. **Snippets kullan:** Sık kullandığın sorguları kaydet
3. **Explain Analyze kullan:** Query performansını analiz et
4. **ERD göster:** Tools → ERD for Database (tablo ilişkilerini gösterir)
5. **Dashboard kullan:** Server'a tıklayınca dashboard ekranı performans metrikleri gösterir

---

**Şimdi migration'lar için [MIGRATION_REHBERI.md](MIGRATION_REHBERI.md) dosyasına bak!**
