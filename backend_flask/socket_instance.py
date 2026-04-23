from flask_socketio import SocketIO

# Initialize SocketIO without an app first
# This allows us to import it in routes without circular dependencies
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading", 
                    logger=False, engineio_logger=False)
