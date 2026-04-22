from flask import Blueprint, request, jsonify
from utils.db import get_db

evacuation_bp = Blueprint('evacuation', __name__)

@evacuation_bp.route('/', methods=['GET'])
def get_evacuation_centers():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM evacuation_centers ORDER BY created_at DESC")
        centers = cursor.fetchall()
        return jsonify(centers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@evacuation_bp.route('/', methods=['POST'])
def create_evacuation_center():
    data = request.get_json()
    name = data.get('name')
    location = data.get('location')
    lat = data.get('lat')
    lng = data.get('lng')
    capacity = data.get('capacity', 0)
    phone = data.get('phone', '')

    if not name or not location or not lat or not lng:
        return jsonify({"error": "Name, location, latitude, and longitude are required"}), 400

    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            INSERT INTO evacuation_centers (name, location, lat, lng, capacity, phone)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, location, lat, lng, capacity, phone))
        
        # Automatically create an alert for the new center
        alert_title = f"New Evacuation Center: {name}"
        alert_description = f"{name} in {location} is now available for residents. Capacity: {capacity}."
        cursor.execute("""
            INSERT INTO alerts (title, description, level, barangay, status, evacuation_status, evacuation_location, evacuation_capacity, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """, (alert_title, alert_description, 'evacuation', 'All', 'active', 'open', location, capacity))

        db.commit()
        center_id = cursor.lastrowid
        alert_id = cursor.lastrowid # Note: alerts table id

        # ── REAL-TIME BROADCAST: Instant delivery to mobile apps ──
        try:
            from app import socketio
            # Notify about new evacuation center
            socketio.emit("new_notification", {
                "type": "evacuation_center",
                "id": center_id,
                "title": alert_title,
                "description": alert_description,
                "location": location,
                "capacity": capacity
            }, namespace="/")
        except: pass

        return jsonify({"message": "Evacuation center created successfully", "id": center_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@evacuation_bp.route('/<int:center_id>', methods=['PUT'])
def update_evacuation_center(center_id):
    data = request.get_json()
    name = data.get('name')
    location = data.get('location')
    lat = data.get('lat')
    lng = data.get('lng')
    capacity = data.get('capacity')
    slots_filled = data.get('slots_filled')
    status = data.get('status')
    phone = data.get('phone')

    db = get_db()
    cursor = db.cursor()
    try:
        updates = []
        params = []
        if name: updates.append("name = %s"); params.append(name)
        if location: updates.append("location = %s"); params.append(location)
        if lat: updates.append("lat = %s"); params.append(lat)
        if lng: updates.append("lng = %s"); params.append(lng)
        if capacity is not None: updates.append("capacity = %s"); params.append(capacity)
        if slots_filled is not None: updates.append("slots_filled = %s"); params.append(slots_filled)
        if status: updates.append("status = %s"); params.append(status)
        if phone is not None: updates.append("phone = %s"); params.append(phone)

        if not updates:
            return jsonify({"error": "No updates provided"}), 400

        query = f"UPDATE evacuation_centers SET {', '.join(updates)} WHERE id = %s"
        params.append(center_id)
        
        cursor.execute(query, tuple(params))
        
        # Trigger an alert if status or name/location changed significantly
        if status or name or location or capacity is not None:
            # Fetch current details to build the alert
            cursor.execute("SELECT name, location, status, capacity FROM evacuation_centers WHERE id = %s", (center_id,))
            c = cursor.fetchone()
            if c:
                alert_title = f"Evacuation Update: {c[0]}"
                alert_description = f"Center {c[0]} status is now {c[2].upper()}. Location: {c[1]}."
                cursor.execute("""
                    INSERT INTO alerts (title, description, level, barangay, status, evacuation_status, evacuation_location, evacuation_capacity, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """, (alert_title, alert_description, 'evacuation', 'All', 'active', c[2], c[1], c[3]))

        db.commit()

        # Broadcast the alert via WebSocket
        try:
            from app import socketio
            socketio.emit("new_notification", {"type": "alert", "level": "evacuation"}, namespace="/")
        except: pass

        return jsonify({"message": "Evacuation center updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

@evacuation_bp.route('/<int:center_id>', methods=['DELETE'])
def delete_evacuation_center(center_id):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM evacuation_centers WHERE id = %s", (center_id,))
        db.commit()
        return jsonify({"message": "Evacuation center deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
