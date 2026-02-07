"""
Yeni migration oluşturma helper'ı
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("❌ Kullanım: python3 scripts/create_migration.py 'migration_message'")
        print()
        print("Örnek:")
        print("  python3 scripts/create_migration.py 'Add user preferences table'")
        sys.exit(1)
    
    message = sys.argv[1]
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    print(f"🔄 Migration oluşturuluyor: {message}")
    print("=" * 60)
    
    cmd = f'python3 -m alembic revision --autogenerate -m "{message}"'
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
        print("      python3 scripts/run_migrations.py")
    else:
        print()
        print("❌ Migration oluşturma hatası!")
        sys.exit(1)

if __name__ == "__main__":
    main()
