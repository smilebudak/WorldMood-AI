"""
Migration helper script for easy migration execution.
"""
import subprocess
import sys
from pathlib import Path
import os

def run_command(cmd, cwd=None):
    """Execute command and display output."""
    print(f"🚀 Running: {cmd}")
    print("=" * 60)
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode

def main():
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)

    print("🔄 WorldMood-AI Database Migration")
    print("=" * 60)
    print()

    # Check Python version
    print("🐍 Python version:")
    run_command("python3 --version")
    print()

    # Check if Alembic is installed
    print("🔍 Alembic check:")
    exitcode = run_command("python3 -m alembic --version")
    if exitcode != 0:
        print()
        print("❌ Alembic not installed!")
        print("📦 To install:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    print()

    # Show current status
    print("📍 Current migration status:")
    run_command("python3 -m alembic current")
    print()

    # Run migrations
    print("⬆️  Applying migrations...")
    exitcode = run_command("python3 -m alembic upgrade head")

    if exitcode == 0:
        print()
        print("✅ Migrations applied successfully!")
        print()
        print("📊 New status:")
        run_command("python3 -m alembic current")
        print()
        print("💡 To check database status:")
        print("   python3 scripts/check_db.py")
    else:
        print()
        print("❌ Migration error occurred!")
        print()
        print("🔍 Troubleshooting:")
        print("   1. Check .env file")
        print("   2. Check PostgreSQL service: pg_isready")
        print("   3. Ensure database is created")
        sys.exit(1)

if __name__ == "__main__":
    main()
