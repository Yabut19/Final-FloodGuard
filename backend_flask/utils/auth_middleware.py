import logging
from functools import wraps
from flask import request, jsonify
import jwt
from config import Config

logger = logging.getLogger(__name__)


def token_required(f):
    """Decorator that enforces JWT authentication on a route.

    Expects: Authorization: Bearer <token>

    Injects `current_user` dict (keys: user_id, role) as the first arg
    after self/cls (if any) into the wrapped function.
    """
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

        current_user = {
            "user_id": payload.get("user_id"),
            "role": payload.get("role"),
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

        role = payload.get("role")
        if role not in ("super_admin", "admin"):
            return jsonify({"error": "Admin access required"}), 403

        current_user = {"user_id": payload.get("user_id"), "role": role}
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

        role = payload.get("role")
        if role not in ("super_admin", "admin", "lgu_admin"):
            return jsonify({"error": "LGU or Admin access required"}), 403

        current_user = {"user_id": payload.get("user_id"), "role": role}
        return f(current_user, *args, **kwargs)

    return decorated
