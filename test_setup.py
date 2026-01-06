"""
Quick test to verify the setup works
Run: python3 test_setup.py
"""
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    from app.config import settings
    print(f"\n✅ Configuration loaded successfully")
    print(f"   APP_NAME: {settings.APP_NAME}")
    print(f"   APP_VERSION: {settings.APP_VERSION}")
except Exception as e:
    print(f"\n❌ Configuration failed: {e}")
    sys.exit(1)

try:
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    logger.info("test_message", status="success")
    print("✅ Logging configured successfully")
except Exception as e:
    print(f"❌ Logging failed: {e}")
    sys.exit(1)

try:
    from app.main import app
    print("✅ FastAPI application created successfully")
    print(f"   Title: {app.title}")
    print(f"   Version: {app.version}")
except Exception as e:
    print(f"❌ FastAPI application failed: {e}")
    sys.exit(1)

print("\n🎉 All basic setup tests passed!")
print("\nNext steps:")
print("1. Copy .env.example to .env and add your credentials")
print("2. Run: uvicorn app.main:app --reload --port 8000")
print("3. Visit: http://localhost:8000")
