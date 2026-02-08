"""
Helper script for creating new database migrations.
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python3 scripts/create_migration.py 'migration_message'")
        print()
        print("Example:")
        print("  python3 scripts/create_migration.py 'Add user preferences table'")
        sys.exit(1)

    message = sys.argv[1]
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)

    print(f"🔄 Creating migration: {message}")
    print("=" * 60)

    cmd = f'python3 -m alembic revision --autogenerate -m "{message}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    if result.returncode == 0:
        print()
        print("✅ Migration file created!")
        print()
        print("📝 Next steps:")
        print("   1. Review the new file in alembic/versions/")
        print("   2. Edit if necessary")
        print("   3. Run the migration:")
        print("      python3 scripts/run_migrations.py")
    else:
        print()
        print("❌ Migration creation error!")
        sys.exit(1)

if __name__ == "__main__":
    main()
