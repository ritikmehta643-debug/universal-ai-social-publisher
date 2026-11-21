import os
import sys
from pathlib import Path

# Ensure backend root is in sys.path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def main():
    try:
        import uvicorn
        from app.config import HOST, PORT, DEBUG
        print(f"Starting Universal AI Social Publisher on http://{HOST}:{PORT}")
        uvicorn.run("app.main:app", host=HOST, port=PORT, reload=DEBUG)
    except ImportError:
        print("[Notice] 'uvicorn' or 'fastapi' is not yet installed in your Python environment.")
        print("To install dependencies, please run: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
