from backend.app import create_app
from backend.app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    # 🔥 使用 socketio.run 替代 app.run
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)