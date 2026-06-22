from backend.app import create_app
from backend.app.extensions import socketio
import os

app = create_app()

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    socketio.run(app, host='0.0.0.0', port=5000, debug=debug, allow_unsafe_werkzeug=debug)