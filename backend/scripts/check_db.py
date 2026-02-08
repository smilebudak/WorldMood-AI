"""
Database status checking script.
Displays connection, tables, and data statistics.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import engine
from app.config import get_settings


async def check_database():
    """Check database status and generate report."""
    settings = get_settings()

    print("🔍 WorldMood-AI Database Status Check")
    print("=" * 60)

    try:
        async with engine.begin() as conn:
            # PostgreSQL version
            from sqlalchemy import text
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📦 PostgreSQL: {version.split(',')[0]}")

            # Database info
            result = await conn.execute(text("SELECT current_database()"))
            db_name = result.scalar()
            print(f"🗄️  Database: {db_name}")

            # User info
            result = await conn.execute(text("SELECT current_user"))
            user = result.scalar()
            print(f"👤 User: {user}")

            print("\n" + "=" * 60)
            print("📋 Tables:")
            print("=" * 60)

            # List tables
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
                print("⚠️  No tables found!")
                print("\n💡 To create tables:")
                print("   python backend/scripts/create_tables.py")
                return

            for schema, table, owner in tables:
                # Row count for each table
                count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = count_result.scalar()
                print(f"\n📊 {table}")
                print(f"   • Owner: {owner}")
                print(f"   • Record count: {count:,}")

                # Table size
                size_result = await conn.execute(text(f"""
                    SELECT pg_size_pretty(pg_total_relation_size('{table}'))
                """))
                size = size_result.scalar()
                print(f"   • Size: {size}")

                # Latest record date (if created_at or date column exists)
                if table == 'country_mood':
                    latest = await conn.execute(text(
                        "SELECT MAX(created_at) FROM country_mood"
                    ))
                    latest_date = latest.scalar()
                    if latest_date:
                        print(f"   • Latest record: {latest_date}")

                elif table == 'mood_spike':
                    latest = await conn.execute(text(
                        "SELECT MAX(detected_at) FROM mood_spike"
                    ))
                    latest_date = latest.scalar()
                    if latest_date:
                        print(f"   • Latest detection: {latest_date}")

            print("\n" + "=" * 60)
            print("🔗 Indexes:")
            print("=" * 60)

            # List indexes
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
                print(f"   • Table: {table}")
                print(f"   • Definition: {definition.split('ON')[1].strip()}")

            # Total database size
            print("\n" + "=" * 60)
            result = await conn.execute(text(f"""
                SELECT pg_size_pretty(pg_database_size('{db_name}'))
            """))
            total_size = result.scalar()
            print(f"💾 Total Database Size: {total_size}")
            print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting suggestions:")
        print("   1. Ensure PostgreSQL service is running")
        print("   2. Verify DATABASE_URL in .env file")
        print("   3. Ensure database is created")
        sys.exit(1)


async def main():
    await check_database()
    print("\n✅ Check completed!")


if __name__ == "__main__":
    asyncio.run(main())
