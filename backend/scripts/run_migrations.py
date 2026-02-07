"""
Migration helper script
Kolay migration çalıştırma için
"""
import subprocess
import sys
from pathlib import Path
import os

def run_command(cmd, cwd=None):
    """Komutu çalıştır ve outputu göster."""
    print(f"🚀 Çalıştırılıyor: {cmd}")
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
    
    print("🔄 MoodAtlas Database Migration")
    print("=" * 60)
    print()
    
    # Python versiyonunu kontrol et
    print("🐍 Python versiyonu:")
    run_command("python3 --version")
    print()
    
    # Alembic kurulu mu kontrol et
    print("🔍 Alembic kontrolü:")
    exitcode = run_command("python3 -m alembic --version")
    if exitcode != 0:
        print()
        print("❌ Alembic kurulu değil!")
        print("📦 Kurulum için:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    print()
    
    # Current durumu göster
    print("📍 Mevcut migration durumu:")
    run_command("python3 -m alembic current")
    print()
    
    # Migration'ları çalıştır
    print("⬆️  Migration'lar uygulanıyor...")
    exitcode = run_command("python3 -m alembic upgrade head")
    
    if exitcode == 0:
        print()
        print("✅ Migration'lar başarıyla uygulandı!")
        print()
        print("📊 Yeni durum:")
        run_command("python3 -m alembic current")
        print()
        print("💡 Database durumunu kontrol etmek için:")
        print("   python3 scripts/check_db.py")
    else:
        print()
        print("❌ Migration'larda hata oluştu!")
        print()
        print("🔍 Sorun giderme:")
        print("   1. .env dosyasını kontrol et")
        print("   2. PostgreSQL servisini kontrol et: pg_isready")
        print("   3. Database'in oluşturulduğundan emin ol")
        sys.exit(1)

if __name__ == "__main__":
    main()
