"""
Database table creation script.
Automatically creates tables from SQLAlchemy models.
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import engine
from app.db.models import Base
from app.config import get_settings


async def create_tables():
    """Create all database tables."""
    settings = get_settings()

    print("🗄️  WorldMood-AI Database Initialization")
    print("=" * 60)
    print(f"📍 Database URL: {settings.DATABASE_URL.split('@')[-1]}")  # Show host, hide password
    print("=" * 60)

    try:
        async with engine.begin() as conn:
            print("\n🔍 Checking existing tables...")

            # Create tables (doesn't DROP, only creates missing ones)
            await conn.run_sync(Base.metadata.create_all)

            print("✅ Tables created successfully!")
            print("\n📋 Created tables:")
            for table in Base.metadata.sorted_tables:
                print(f"   • {table.name}")

            # Check table count
            result = await conn.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = result.fetchall()
            print(f"\n📊 Total table count: {len(tables)}")

    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("\n💡 Troubleshooting suggestions:")
        print("   1. Ensure PostgreSQL service is running")
        print("   2. Verify DATABASE_URL in .env file")
        print("   3. Ensure database and user are created:")
        print("      psql -U postgres -f backend/init_db.sql")
        sys.exit(1)


async def check_connection():
    """Test database connection."""
    print("\n🔌 Testing database connection...")
    try:
        async with engine.begin() as conn:
            result = await conn.execute("SELECT version()")
            version = result.scalar()
            print(f"✅ Connection successful!")
            print(f"📦 PostgreSQL version: {version.split(',')[0]}")
            return True
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


async def main():
    """Main function."""
    # Test connection first
    if not await check_connection():
        sys.exit(1)

    # Create tables
    await create_tables()

    print("\n✨ Setup completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
