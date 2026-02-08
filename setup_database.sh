#!/bin/bash
# =================================================================
# WorldMood-AI Quick Database Setup Script
# =================================================================
# This script automates database setup
# =================================================================

set -e  # Stop on error

echo "🚀 WorldMood-AI Database Quick Setup"
echo "================================================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo -e "${RED}❌ PostgreSQL is not installed!${NC}"
    echo ""
    echo "Please install PostgreSQL:"
    echo "  macOS:   brew install postgresql@16"
    echo "  Ubuntu:  sudo apt install postgresql-16"
    exit 1
fi

echo -e "${GREEN}✅ PostgreSQL found${NC}"

# Is PostgreSQL running?
if ! pg_isready -q; then
    echo -e "${YELLOW}⚠️  PostgreSQL is not running, starting...${NC}"

    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql@16
    else
        sudo systemctl start postgresql
    fi

    sleep 2
fi

echo -e "${GREEN}✅ PostgreSQL service is active${NC}"

# Create database
echo ""
echo "📦 Creating database..."
echo "================================================================="

if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw worldmood; then
    echo -e "${YELLOW}⚠️  'worldmood' database already exists${NC}"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        psql -U postgres -c "DROP DATABASE IF EXISTS worldmood;"
        psql -U postgres -c "DROP USER IF EXISTS worldmood;"
        echo -e "${GREEN}✅ Old database deleted${NC}"
    else
        echo "Existing database preserved"
    fi
fi

# Run init_db.sql
echo ""
echo "🔧 Running init_db.sql..."
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
psql -U postgres -f "$SCRIPT_DIR/backend/init_db.sql" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database created successfully${NC}"
else
    echo -e "${RED}❌ Database creation error${NC}"
    exit 1
fi

# Create .env file
echo ""
echo "⚙️  Creating .env file..."
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Don't forget to fill in API keys in the .env file!${NC}"
else
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
fi

# Check Python environment
echo ""
echo "🐍 Checking Python environment..."

if [ -d "$SCRIPT_DIR/backend/venv" ]; then
    source "$SCRIPT_DIR/backend/venv/bin/activate"
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
elif [ -f "$SCRIPT_DIR/backend/pyproject.toml" ]; then
    cd "$SCRIPT_DIR/backend"
    poetry install
    echo -e "${GREEN}✅ Poetry dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  Python environment not found${NC}"
    echo "Install requirements manually:"
    echo "  cd backend"
    echo "  pip install -r requirements.txt"
fi

# Create tables
echo ""
echo "📊 Creating database tables..."
cd "$SCRIPT_DIR/backend"
python scripts/create_tables.py

# Check database status
echo ""
echo "🔍 Checking database status..."
python scripts/check_db.py

# Summary
echo ""
echo "================================================================="
echo -e "${GREEN}✨ Setup completed!${NC}"
echo "================================================================="
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Add API keys:"
echo "   nano .env"
echo ""
echo "2. Start backend:"
echo "   cd backend"
echo "   uvicorn app.main:app --reload"
echo ""
echo "3. Or with Docker:"
echo "   docker-compose up"
echo ""
echo "================================================================="
