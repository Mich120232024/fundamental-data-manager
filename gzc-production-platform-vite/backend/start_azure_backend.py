#!/usr/bin/env python3
"""
Start Azure Backend with PostgreSQL and Redis
This is a simplified startup script that imports from the main app
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the main app
if __name__ == "__main__":
    try:
        # Use uvicorn programmatically
        import uvicorn
        from app.main import app
        
        print("🚀 Starting Azure Backend on http://localhost:8000")
        print("📊 PostgreSQL: Azure Database")
        print("💹 Redis: Azure Cache for FX Prices")
        print("🔌 WebSocket: Real-time price streaming")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Installing required packages...")
        os.system("pip3 install --user fastapi uvicorn redis azure-identity azure-keyvault-secrets sqlalchemy asyncpg psycopg2-binary python-socketio")
        print("\n✅ Please run this script again after installation")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()