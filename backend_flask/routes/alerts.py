import logging
from flask import Blueprint, request, jsonify
from datetime import datetime
from utils.db import get_db

logger = logging.getLogger(__name__)

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/user/<int:user_id>/dismiss/<int:alert_id>', methods=['POST'])
def dismiss_alert_for_user(user_id, alert_id):
    """Dismiss an alert for a specific user (user-specific deletion - mobile only)"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO user_alert_dismissals (user_id, alert_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE dismissed_at = NOW()
        """, (user_id, alert_id))
        db.commit()
        return jsonify({"message": "Alert dismissed for user"}), 200
    except Exception as e:
        logger.error("Failed to dismiss alert %s for user %s: %s", alert_id, user_id, e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@alerts_bp.route('/user/<int:user_id>/dismiss/all', methods=['POST'])
def dismiss_all_alerts_for_user(user_id):
    """Dismiss all current active alerts for a specific user"""
    db = get_db()
    cursor = db.cursor()
    try:
        # Efficiently insert all active alerts into this user's dismissal list
        cursor.execute("""
            INSERT INTO user_alert_dismissals (user_id, alert_id)
            SELECT %s, id FROM alerts 
            WHERE status = 'active'
            ON DUPLICATE KEY UPDATE dismissed_at = NOW()
        """, (user_id,))
        
        db.commit()
        return jsonify({"message": "All alerts marked as dismissed"}), 200
    except Exception as e:
        logger.error("Failed to clear alerts for user %s: %s", user_id, e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@alerts_bp.route('/<int:alert_id>', methods=['GET'])
def get_alert(alert_id):
    """Fetch a single alert by ID (used by mobile Alert Detail screen)."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM alerts WHERE id = %s", (alert_id,))
        alert = cursor.fetchone()
        if not alert:
            return jsonify({"error": "Alert not found"}), 404
        return jsonify(alert), 200
    except Exception as e:
        logger.error("Failed to fetch alert %s: %s", alert_id, e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@alerts_bp.route('/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert by ID (system-wide - for LGU/ADMIN only)"""
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM alerts WHERE id = %s", (alert_id,))
        db.commit()

        if cursor.rowcount > 0:
            return jsonify({"message": "Alert deleted successfully"}), 200
        else:
            return jsonify({"error": "Alert not found"}), 404
    except Exception as e:
        logger.error("Failed to delete alert %s: %s", alert_id, e)
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@alerts_bp.route('/', methods=['GET'])
def get_alerts():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    status = request.args.get('status') # e.g. active
    user_id = request.args.get('user_id')  # Optional: filter out dismissed alerts for this user
    
    # Start with base query
    query = "SELECT a.* FROM alerts a"
    params = []
    
    # If user_id provided, use LEFT JOIN to exclude dismissed alerts
    if user_id:
        query += " LEFT JOIN user_alert_dismissals d ON a.id = d.alert_id AND d.user_id = %s"
        params.append(user_id)
        query += " WHERE d.alert_id IS NULL"  # Only get alerts NOT in dismissals
    else:
        query += " WHERE 1=1"
    
    if status:
        query += " AND a.status = %s"
        params.append(status)
        
    query += " ORDER BY a.timestamp DESC"
    
    try:
        cursor.execute(query, params)
        alerts = cursor.fetchall()
        cursor.close()
        return jsonify(alerts)
    except Exception as e:
        cursor.close()
        # If user_alert_dismissals table doesn't exist yet, just return all alerts
        if "doesn't exist" in str(e) or "no such table" in str(e).lower():
            cursor = db.cursor(dictionary=True)
            fallback_query = "SELECT * FROM alerts WHERE 1=1"
            fallback_params = []
            
            if status:
                fallback_query += " AND status = %s"
                fallback_params.append(status)
                
            fallback_query += " ORDER BY timestamp DESC"
            
            cursor.execute(fallback_query, fallback_params)
            alerts = cursor.fetchall()
            cursor.close()
            return jsonify(alerts)
        else:
            return jsonify({"error": str(e)}), 500

@alerts_bp.route('/', methods=['POST'])
def create_alert():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    level = data.get('level') # advisory, warning, critical, evacuation
    barangay = data.get('barangay', 'All')
    recommended_action = data.get('recommended_action', '')
    source = data.get('source', 'manual')
    evacuation_status = data.get('evacuation_status', 'open') if level == 'evacuation' else None
    evacuation_location = data.get('evacuation_location') if level == 'evacuation' else None
    evacuation_capacity = data.get('evacuation_capacity') if level == 'evacuation' else None
    
    if not title or not level:
        return jsonify({"error": "Title and level are required"}), 400
    
    if level.lower() not in ['advisory', 'warning', 'critical', 'evacuation']:
        return jsonify({"error": "Invalid alert level. Only Advisory, Warning, Critical, and Evacuation are allowed."}), 400
        
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        INSERT INTO alerts (title, description, level, barangay, recommended_action, status, source, evacuation_status, evacuation_location, evacuation_capacity, timestamp)
        VALUES (%s, %s, %s, %s, %s, 'active', %s, %s, %s, %s, NOW())
    """, (title, description, level, barangay, recommended_action, source, evacuation_status, evacuation_location, evacuation_capacity))
    
    db.commit()
    alert_id = cursor.lastrowid
    cursor.close()
    
    # ── REAL-TIME BROADCAST: Deliver instantly to mobile apps (latency < 200ms) ──
    try:
        from app import socketio
        
        # Point 4: Mobile App Notification Rules (Evacuation Alerts)
        if level == 'evacuation':
            notification_payload = {
                "type": "alert",
                "id": alert_id,
                "title": title,
                "description": description,
                "level": level,
                "barangay": barangay,
                "evacuation_status": evacuation_status,
                "evacuation_location": evacuation_location,
                "evacuation_capacity": evacuation_capacity,
                "timestamp": datetime.now().isoformat()
                # DO NOT include recommended_action or incident_status for evacuation
            }
        else:
            notification_payload = {
                "type": "alert",
                "id": alert_id,
                "title": title,
                "description": description,
                "level": level,
                "barangay": barangay,
                "recommended_action": recommended_action,
                "timestamp": datetime.now().isoformat()
            }

        socketio.emit("new_notification", notification_payload, namespace="/")
    except Exception as ws_err:
        logger.warning(f"WebSocket broadcast failed: {ws_err}")

    return jsonify({"message": "Alert created successfully", "id": alert_id}), 201
