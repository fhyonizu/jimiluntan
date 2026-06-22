from backend.app import create_app
from backend.app.extensions import socketio
import os

app = create_app()

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    if debug:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
    else:
        # 生产模式：用 socketio.run(eventlet) 支持 WebSocket + 高并发
        # 或: gunicorn -k eventlet -w 4 -b 0.0.0.0:5000 backend.run:app
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
