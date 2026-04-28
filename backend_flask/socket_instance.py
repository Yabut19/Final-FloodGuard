from flask_socketio import SocketIO
import logging

logger = logging.getLogger(__name__)

# Initialize SocketIO without an app first
# This allows us to import it in routes without circular dependencies
socketio = SocketIO(
    cors_allowed_origins="*", 
    async_mode="threading", 
    logger=False,           # Disable verbose logging in production
    engineio_logger=False, 
    ping_timeout=30,        # Increased from 10 to be more robust
    ping_interval=15,       # Increased from 5
    manage_session=False
)

def emit_user_update():
    """Centralized function to broadcast user changes."""
    try:
        socketio.emit("user_update", {"message": "refresh"}, namespace="/")
        logger.info("[WS] Broadcasted user_update")
    except Exception as e:
        logger.error("[WS] Failed to broadcast user_update: %s", e)

