import logging
import jwt
from functools import wraps
from flask import request, jsonify
from config import Config
from utils.db import get_db

logger = logging.getLogger(__name__)

def _check_account_status(user_id, role):
    """Helper to verify if account still exists and is active."""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        if role in ('super_admin', 'admin'):
            cursor.execute("SELECT status, 'All Locations' as barangay FROM admins WHERE id = %s", (user_id,))
        else:
            cursor.execute("SELECT status, barangay FROM users WHERE id = %s", (user_id,))
            
        user_row = cursor.fetchone()
        cursor.close()
        
        if not user_row:
            return False, ("User account no longer exists", 401)
        
        if user_row.get('status') == 'inactive':
            return False, ("Account is inactive. Please contact support.", 403)
            
        return True, user_row.get('barangay')
    except Exception as e:
        logger.error("Error checking account status: %s", e)
        return False, ("Server error during authentication", 500)

def token_required(f):
    """Decorator that enforces JWT authentication on a route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token is missing or invalid"}), 401

        token = auth_header.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token: %s", e)
            return jsonify({"error": "Invalid token"}), 401

        user_id = payload.get("user_id")
        role = payload.get("role")
        
        # Real-time account status validation
        is_active, result = _check_account_status(user_id, role)
        if not is_active:
            msg, code = result
            return jsonify({"error": msg}), code

        barangay = result # If active, result is the barangay

        current_user = {
            "user_id": user_id,
            "role": role,
            "barangay": barangay
        }
        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    """Like token_required but also enforces super_admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token is missing or invalid"}), 401

        token = auth_header.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token: %s", e)
            return jsonify({"error": "Invalid token"}), 401

        user_id = payload.get("user_id")
        role = payload.get("role")
        
        # Real-time account status validation
        is_active, result = _check_account_status(user_id, role)
        if not is_active:
            msg, code = result
            return jsonify({"error": msg}), code

        barangay = result

        if role not in ("super_admin", "admin"):
            return jsonify({"error": "Admin access required"}), 403

        current_user = {"user_id": user_id, "role": role, "barangay": barangay}
        return f(current_user, *args, **kwargs)

    return decorated


def lgu_or_admin_required(f):
    """Like token_required but enforces lgu_admin or super_admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization token is missing or invalid"}), 401

        token = auth_header.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid token: %s", e)
            return jsonify({"error": "Invalid token"}), 401

        user_id = payload.get("user_id")
        role = payload.get("role")
        
        # Real-time account status validation
        is_active, result = _check_account_status(user_id, role)
        if not is_active:
            msg, code = result
            return jsonify({"error": msg}), code

        barangay = result

        if role not in ("super_admin", "admin", "lgu_admin", "lgu"):
            return jsonify({"error": "LGU or Admin access required"}), 403

        current_user = {"user_id": user_id, "role": role, "barangay": barangay}
        return f(current_user, *args, **kwargs)

    return decorated
