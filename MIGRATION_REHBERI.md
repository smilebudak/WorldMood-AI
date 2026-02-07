# 🔄 Database Migration Rehberi (Alembic)

## 📚 Migration Nedir?

Migration, database şemasındaki değişiklikleri versiyonlayarak yönetmenizi sağlar. Örneğin:
- Yeni tablo eklemek
- Kolonları değiştirmek
- İndeks eklemek/silmek
- Veri dönüşümleri yapmak

---

## 🚀 Hızlı Başlangıç

### Tek Komutla Migration Çalıştır:

```bash
# Backend klasöründen
cd backend

# İlk migration'ı oluştur ve uygula
python scripts/run_migrations.py
```

---

## ⚙️ Alembic Kurulumu

### 1️⃣ Alembic Zaten Kurulu

`requirements.txt`'de zaten var:
```txt
alembic>=1.13,<2
```

### 2️⃣ Alembic'i Başlat

```bash
cd backend

# Alembic klasörü oluştur
alembic init alembic
```

Bu komut şu yapıyı oluşturur:
```
backend/
├── alembic/
│   ├── env.py           # Alembic konfigürasyonu
│   ├── script.py.mako   # Migration template
│   └── versions/        # Migration dosyaları
└── alembic.ini          # Alembic ayarları
```

### 3️⃣ alembic.ini'yi Yapılandır

```bash
nano alembic.ini
```

**Değiştir:**
```ini
# Satır 63
sqlalchemy.url = postgresql+asyncpg://moodatlas:moodatlas@localhost:5432/moodatlas
```

**Siliniyor** (çünkü .env'den okuyacağız):
```ini
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

### 4️⃣ alembic/env.py'yi Yapılandır

Aşağıdaki içeriği kullan:

```python
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# Backend path'i ekle
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Config ve modelleri import et
from app.config import get_settings
from app.db.models import Base

# Alembic Config objesi
config = context.config

# Python logging'i yapılandır
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData'yı ekle
target_metadata = Base.metadata

# .env'den DATABASE_URL'i al
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL.replace('+asyncpg', ''))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

---

## 📝 Migration Oluşturma

### Otomatik Migration (Önerilen):

```bash
cd backend

# Mevcut modellerden migration oluştur
alembic revision --autogenerate -m "Initial schema"
```

Bu komut:
- `app/db/models.py`'deki SQLAlchemy modellerini okur
- Mevcut database'le karşılaştırır
- Farkları bulup migration dosyası oluşturur

### Manuel Migration:

```bash
# Boş migration dosyası oluştur
alembic revision -m "Add new column"
```

Sonra `alembic/versions/xxxx_add_new_column.py` dosyasını düzenle:

```python
def upgrade() -> None:
    op.add_column('country_mood', sa.Column('new_field', sa.String(50)))

def downgrade() -> None:
    op.drop_column('country_mood', 'new_field')
```

---

## 🚀 Migration'ları Çalıştırma

### En Son Versiyona Yükselt:

```bash
cd backend

# Tüm migration'ları uygula
alembic upgrade head
```

Çıktı:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> abc123, Initial schema
```

### Belirli Bir Versiyona Git:

```bash
# Belirli revision'a git
alembic upgrade abc123

# Bir önceki versiyona geri dön
alembic downgrade -1

# Tümünü geri al
alembic downgrade base
```

### Migration Geçmişini Gör:

```bash
# Mevcut durum
alembic current

# Tüm migration'lar
alembic history

# Detaylı geçmiş
alembic history --verbose
```

---

## 📊 Örnek Migration'lar

### 1. Yeni Kolon Ekle:

```bash
alembic revision --autogenerate -m "Add spotify_playlist_url to country_mood"
```

Migration dosyası:
```python
def upgrade() -> None:
    op.add_column('country_mood', 
        sa.Column('spotify_playlist_url', sa.String(200), nullable=True))

def downgrade() -> None:
    op.drop_column('country_mood', 'spotify_playlist_url')
```

### 2. İndeks Ekle:

```python
def upgrade() -> None:
    op.create_index('idx_mood_date', 'country_mood', ['date'])

def downgrade() -> None:
    op.drop_index('idx_mood_date', table_name='country_mood')
```

### 3. Yeni Tablo Ekle:

```python
def upgrade() -> None:
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(50), nullable=False),
        sa.Column('favorite_countries', sa.ARRAY(sa.String(3))),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_index('idx_user_id', 'user_preferences', ['user_id'])

def downgrade() -> None:
    op.drop_table('user_preferences')
```

### 4. Veri Dönüşümü:

```python
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Yeni kolon ekle
    op.add_column('country_mood', sa.Column('mood_category', sa.String(20)))
    
    # Mevcut verileri dönüştür
    connection = op.get_bind()
    connection.execute("""
        UPDATE country_mood 
        SET mood_category = CASE 
            WHEN mood_score > 0.5 THEN 'positive'
            WHEN mood_score < -0.5 THEN 'negative'
            ELSE 'neutral'
        END
    """)
    
    # Kolonu nullable=False yap
    op.alter_column('country_mood', 'mood_category', nullable=False)

def downgrade() -> None:
    op.drop_column('country_mood', 'mood_category')
```

---

## 🔧 Faydalı Komutlar

```bash
# Migration durumunu kontrol et
alembic current

# Geçmişi gör
alembic history

# Belirli migration'ı göster
alembic show abc123

# SQL'i göster (çalıştırmadan)
alembic upgrade head --sql

# Bir sonraki migration
alembic upgrade +1

# İki versiyon geriye git
alembic downgrade -2

# Belirli bir revision'a git
alembic upgrade abc123

# Base'e dön (tüm migration'ları geri al)
alembic downgrade base
```

---

## 🐳 Docker ile Migration

### Docker Compose ile:

```bash
# Backend container'da migration çalıştır
docker-compose exec backend alembic upgrade head

# Veya script ile
docker-compose exec backend python scripts/run_migrations.py
```

### Dockerfile'da Otomatik Migration:

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Migration'ları otomatik çalıştır
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 📊 pgAdmin'de Migration Sonuçlarını Görme

Migration'dan sonra pgAdmin'de:

1. **Tabloları yenile:**
   - Servers → MoodAtlas → Databases → moodatlas → Schemas → public → Tables
   - Sağ tık → **Refresh**

2. **Yeni kolonları gör:**
   - Tablo → Columns

3. **Migration geçmişi:**
```sql
SELECT * FROM alembic_version;
```

Bu tablo Alembic'in otomatik oluşturduğu versiyon tracking tablosu.

---

## 🛠️ Helper Scripts

### scripts/run_migrations.py

```python
"""
Migration helper script
Kolay migration çalıştırma için
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd):
    """Komutu çalıştır ve outputu göster."""
    print(f"🚀 Çalıştırılıyor: {cmd}")
    print("=" * 60)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode

def main():
    backend_dir = Path(__file__).parent.parent
    
    print("🔄 MoodAtlas Database Migration")
    print("=" * 60)
    print()
    
    # Current durumu göster
    print("📍 Mevcut durum:")
    run_command("alembic current")
    print()
    
    # Migration'ları çalıştır
    print("⬆️  Migration'lar uygulanıyor...")
    exitcode = run_command("alembic upgrade head")
    
    if exitcode == 0:
        print()
        print("✅ Migration'lar başarıyla uygulandı!")
        print()
        print("📊 Yeni durum:")
        run_command("alembic current")
    else:
        print()
        print("❌ Migration'larda hata oluştu!")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### scripts/create_migration.py

```python
"""
Yeni migration oluşturma helper'ı
"""
import subprocess
import sys

def main():
    if len(sys.argv) < 2:
        print("❌ Kullanım: python scripts/create_migration.py 'migration_message'")
        print()
        print("Örnek:")
        print("  python scripts/create_migration.py 'Add user preferences table'")
        sys.exit(1)
    
    message = sys.argv[1]
    
    print(f"🔄 Migration oluşturuluyor: {message}")
    print("=" * 60)
    
    cmd = f'alembic revision --autogenerate -m "{message}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode == 0:
        print()
        print("✅ Migration dosyası oluşturuldu!")
        print()
        print("📝 Sonraki adım:")
        print("   1. alembic/versions/ klasöründeki yeni dosyayı kontrol et")
        print("   2. Gerekirse düzenle")
        print("   3. Migration'ı çalıştır:")
        print("      alembic upgrade head")
    else:
        print()
        print("❌ Migration oluşturma hatası!")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 🚨 Dikkat Edilmesi Gerekenler

### ✅ Yapılması Gerekenler:

1. **Migration'ları test et:** Production'a geçmeden önce test ortamında dene
2. **Backup al:** Önemli migration'lardan önce backup al
3. **Downgrade yaz:** Her migration için downgrade fonksiyonu yaz
4. **Küçük adımlar:** Büyük değişiklikleri küçük migration'lara böl
5. **Gözden geçir:** Auto-generate edilen migration'ları mutlaka kontrol et

### ❌ Yapılmaması Gerekenler:

1. **Production'da manuel SQL çalıştırma:** Migration kullan!
2. **Migration'ları değiştirme:** Uygulandıktan sonra değiştirme, yeni migration oluştur
3. **Downgrade'siz migration:** Her zaman geri alma yolu bırak
4. **Büyük data migration'lar:** Çok veri varsa batch'ler halinde yap

---

## 🔍 Sorun Giderme

### Migration Hatası: "Target database is not up to date"

```bash
# Stamp ile mevcut durumu işaretle
alembic stamp head
```

### Migration Oluşturmuyor (No changes detected)

```bash
# Cache'i temizle
rm -rf __pycache__ app/**/__pycache__

# Tekrar dene
alembic revision --autogenerate -m "message"
```

### Alembic Version Çakışması

```bash
# Mevcut versiyonu kontrol et
alembic current

# Manuel stamp
alembic stamp <revision_id>
```

### PostgreSQL Connection Hatası

```bash
# .env dosyasını kontrol et
cat .env | grep DATABASE_URL

# Database durumunu kontrol et
python scripts/check_db.py
```

---

## 📚 Ek Kaynaklar

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

---

## 🎯 Özet

```bash
# 1. Alembic'i başlat (sadece bir kez)
alembic init alembic

# 2. env.py ve alembic.ini'yi yapılandır

# 3. İlk migration'ı oluştur
alembic revision --autogenerate -m "Initial schema"

# 4. Migration'ı çalıştır
alembic upgrade head

# 5. Sonuçları pgAdmin'de gör!
```

**Artık pgAdmin'de tablolarını görebilir ve migration'larını yönetebilirsin! 🎉**
