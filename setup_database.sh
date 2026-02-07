#!/bin/bash
# =================================================================
# MoodAtlas Quick Database Setup Script
# =================================================================
# Bu script database kurulumunu otomatikleştirir
# =================================================================

set -e  # Hata durumunda dur

echo "🚀 MoodAtlas Database Quick Setup"
echo "================================================================="

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# PostgreSQL kurulu mu kontrol et
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL kurulu değil!${NC}"
    echo ""
    echo "Lütfen PostgreSQL'i kurun:"
    echo "  macOS:   brew install postgresql@16"
    echo "  Ubuntu:  sudo apt install postgresql-16"
    exit 1
fi

echo -e "${GREEN}✅ PostgreSQL bulundu${NC}"

# PostgreSQL çalışıyor mu?
if ! pg_isready -q; then
    echo -e "${YELLOW}⚠️  PostgreSQL çalışmıyor, başlatılıyor...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql@16
    else
        sudo systemctl start postgresql
    fi
    
    sleep 2
fi

echo -e "${GREEN}✅ PostgreSQL servisi aktif${NC}"

# Database'i oluştur
echo ""
echo "📦 Database oluşturuluyor..."
echo "================================================================="

if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw moodatlas; then
    echo -e "${YELLOW}⚠️  'moodatlas' database'i zaten mevcut${NC}"
    read -p "Yeniden oluşturmak istiyor musunuz? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        psql -U postgres -c "DROP DATABASE IF EXISTS moodatlas;"
        psql -U postgres -c "DROP USER IF EXISTS moodatlas;"
        echo -e "${GREEN}✅ Eski database silindi${NC}"
    else
        echo "Mevcut database korundu"
    fi
fi

# init_db.sql'i çalıştır
echo ""
echo "🔧 init_db.sql çalıştırılıyor..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
psql -U postgres -f "$SCRIPT_DIR/backend/init_db.sql" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database başarıyla oluşturuldu${NC}"
else
    echo -e "${RED}❌ Database oluşturma hatası${NC}"
    exit 1
fi

# .env dosyası oluştur
echo ""
echo "⚙️  .env dosyası oluşturuluyor..."
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo -e "${GREEN}✅ .env dosyası oluşturuldu${NC}"
    echo -e "${YELLOW}⚠️  API anahtarlarını .env dosyasında doldurmayı unutmayın!${NC}"
else
    echo -e "${YELLOW}⚠️  .env dosyası zaten mevcut${NC}"
fi

# Python environment kontrol et
echo ""
echo "🐍 Python environment kontrol ediliyor..."

if [ -d "$SCRIPT_DIR/backend/venv" ]; then
    source "$SCRIPT_DIR/backend/venv/bin/activate"
    echo -e "${GREEN}✅ Virtual environment aktifleştirildi${NC}"
elif [ -f "$SCRIPT_DIR/backend/pyproject.toml" ]; then
    cd "$SCRIPT_DIR/backend"
    poetry install
    echo -e "${GREEN}✅ Poetry dependencies yüklendi${NC}"
else
    echo -e "${YELLOW}⚠️  Python environment bulunamadı${NC}"
    echo "Manuel olarak requirements yükleyin:"
    echo "  cd backend"
    echo "  pip install -r requirements.txt"
fi

# Tabloları oluştur
echo ""
echo "📊 Database tabloları oluşturuluyor..."
cd "$SCRIPT_DIR/backend"
python scripts/create_tables.py

# Database durumunu kontrol et
echo ""
echo "🔍 Database durumu kontrol ediliyor..."
python scripts/check_db.py

# Özet
echo ""
echo "================================================================="
echo -e "${GREEN}✨ Kurulum tamamlandı!${NC}"
echo "================================================================="
echo ""
echo "📋 Sonraki adımlar:"
echo ""
echo "1. API anahtarlarını ekleyin:"
echo "   nano .env"
echo ""
echo "2. Backend'i başlatın:"
echo "   cd backend"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. Veya Docker ile:"
echo "   docker-compose up"
echo ""
echo "================================================================="
