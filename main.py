# Import the app from app.py to be used by the WSGI server
from app import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
