import sys
import os

# Add backend directory to sys.path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app import app, create_app

if __name__ == '__main__':
    app.run(debug=True, port=5000)
