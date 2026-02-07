"""
Database durumunu kontrol eden script.
Bağlantı, tablolar ve veri istatistiklerini gösterir.
"""
import asyncio
import sys
from pathlib import Path

# Backend klasörünü path'e ekle
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import engine
from app.config import get_settings


async def check_database():
    """Database durumunu kontrol et ve rapor ver."""
    settings = get_settings()
    
    print("🔍 MoodAtlas Database Status Check")
    print("=" * 60)
    
    try:
        async with engine.begin() as conn:
            # PostgreSQL versiyonu
            from sqlalchemy import text
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📦 PostgreSQL: {version.split(',')[0]}")
            
            # Database bilgisi
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"🗄️  Database: {db_name}")
            
            # Kullanıcı bilgisi
            result = await conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"👤 User: {user}")
            
            print("\n" + "=" * 60)
            print("📋 Tablolar:")
            print("=" * 60)
            
            # Tabloları listele
            result = await conn.execute(text("""
                SELECT 
                    schemaname,
                    tablename,
                    tableowner
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            tables = result.fetchall()
            
            if not tables:
                print("⚠️  Hiç tablo bulunamadı!")
                print("\n💡 Tabloları oluşturmak için:")
                print("   python backend/scripts/create_tables.py")
                return
            
            for schema, table, owner in tables:
                # Her tablo için satır sayısı
                count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                print(f"\n📊 {table}")
                print(f"   • Owner: {owner}")
                print(f"   • Kayıt sayısı: {count:,}")
                
                # Tablo boyutu
                size_result = await conn.execute(text(f"""
                    SELECT pg_size_pretty(pg_total_relation_size('{table}'))
                """))
                size = size_result.scalar()
                print(f"   • Boyut: {size}")
                
                # Son kayıt tarihi (eğer created_at veya date kolonu varsa)
                if table == 'country_mood':
                    latest = await conn.execute(text(
                        "SELECT MAX(created_at) FROM country_mood"
                    ))
                    latest_date = latest.scalar()
                    if latest_date:
                        print(f"   • Son kayıt: {latest_date}")
                
                elif table == 'mood_spike':
                    latest = await conn.execute(text(
                        "SELECT MAX(detected_at) FROM mood_spike"
                    ))
                    latest_date = latest.scalar()
                    if latest_date:
                        print(f"   • Son tespit: {latest_date}")
            
            print("\n" + "=" * 60)
            print("🔗 İndeksler:")
            print("=" * 60)
            
            # İndeksleri listele
            result = await conn.execute(text("""
                SELECT 
                    tablename,
                    indexname,
                    indexdef
                FROM pg_indexes 
                WHERE schemaname = 'public'
                ORDER BY tablename, indexname
            """))
            indexes = result.fetchall()
            
            for table, index, definition in indexes:
                print(f"\n🔑 {index}")
                print(f"   • Tablo: {table}")
                print(f"   • Tanım: {definition.split('ON')[1].strip()}")
            
            # Database toplam boyutu
            print("\n" + "=" * 60)
            result = await conn.execute(text(f"""
                SELECT pg_size_pretty(pg_database_size('{db_name}'))
            """))
            total_size = result.scalar()
            print(f"💾 Toplam Database Boyutu: {total_size}")
            print("=" * 60)
            
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        print("\n💡 Çözüm önerileri:")
        print("   1. PostgreSQL servisinin çalıştığından emin olun")
        print("   2. .env dosyasındaki DATABASE_URL'i kontrol edin")
        print("   3. Database'in oluşturulduğundan emin olun")
        sys.exit(1)


async def main():
    await check_database()
    print("\n✅ Kontrol tamamlandı!")


if __name__ == "__main__":
    asyncio.run(main())
