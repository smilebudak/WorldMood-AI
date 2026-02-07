"""
Database tables oluşturma scripti.
SQLAlchemy modellerinden tabloları otomatik oluşturur.
"""
import asyncio
import sys
from pathlib import Path

# Backend klasörünü path'e ekle
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import engine
from app.db.models import Base
from app.config import get_settings


async def create_tables():
    """Tüm tabloları oluştur."""
    settings = get_settings()
    
    print("🗄️  MoodAtlas Database Initialization")
    print("=" * 60)
    print(f"📍 Database URL: {settings.DATABASE_URL.split('@')[-1]}")  # IP'yi göster, şifreyi gizle
    print("=" * 60)
    
    try:
        async with engine.begin() as conn:
            print("\n🔍 Mevcut tabloları kontrol ediliyor...")
            
            # Tabloları oluştur (DROP yapmaz, sadece mevcut olmayanları oluşturur)
            await conn.run_sync(Base.metadata.create_all)
            
            print("✅ Tablolar başarıyla oluşturuldu!")
            print("\n📋 Oluşturulan tablolar:")
            for table in Base.metadata.sorted_tables:
                print(f"   • {table.name}")
            
            # Tablo sayısını kontrol et
            result = await conn.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = result.fetchall()
            print(f"\n📊 Toplam tablo sayısı: {len(tables)}")
            
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
        print("\n💡 Çözüm önerileri:")
        print("   1. PostgreSQL servisinin çalıştığından emin olun")
        print("   2. .env dosyasındaki DATABASE_URL'i kontrol edin")
        print("   3. Database ve kullanıcının oluşturulduğundan emin olun:")
        print("      psql -U postgres -f backend/init_db.sql")
        sys.exit(1)


async def check_connection():
    """Database bağlantısını test et."""
    print("\n🔌 Database bağlantısı test ediliyor...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            print(f"✅ Bağlantı başarılı!")
            print(f"📦 PostgreSQL version: {version.split(',')[0]}")
            return True
    except Exception as e:
        print(f"❌ Bağlantı hatası: {e}")
        return False


async def main():
    """Ana fonksiyon."""
    # Önce bağlantıyı test et
    if not await check_connection():
        sys.exit(1)
    
    # Tabloları oluştur
    await create_tables()
    
    print("\n✨ Kurulum tamamlandı!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
