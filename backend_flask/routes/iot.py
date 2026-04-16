from flask import Blueprint, request, jsonify
from utils.db import get_db
from datetime import datetime

iot_bp = Blueprint("iot", __name__)


@iot_bp.route("/sensor-readings", methods=["POST"])
def sensor_reading():
    data = request.get_json(silent=True) or {}
    sensor_id = data.get("sensor_id")
    if not sensor_id:
        return jsonify({"error": "sensor_id is required"}), 400
        
    raw_distance = data.get("raw_distance", 0)
    flood_level = data.get("flood_level")
    status = data.get("status", "NORMAL")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    maps_url = data.get("maps_url")
    
    # Use provided timestamp or current local time
    timestamp = data.get("timestamp")
    if timestamp:
        if isinstance(timestamp, (list, tuple)):
            try:
                timestamp = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*timestamp[:6])
            except Exception:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(timestamp, str):
            timestamp = timestamp.replace("T", " ")
    else:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if flood_level is None:
        return jsonify({"error": "flood_level is required"}), 400

    db = get_db()
    cur = db.cursor()
    
    try:
        # Verify sensor exists
        cur.execute("SELECT id FROM sensors WHERE id = %s", (sensor_id,))
        if not cur.fetchone():
            return jsonify({"error": f"Sensor {sensor_id} not registered"}), 404

        # Insert into water_levels
        cur.execute("""
            INSERT INTO water_levels (sensor_id, level, timestamp)
            VALUES (%s, %s, %s)
        """, (sensor_id, flood_level, timestamp))

        # Insert into iot_readings
        cur.execute("""
            INSERT INTO iot_readings (sensor_id, raw_distance, flood_level, status, latitude, longitude, maps_url, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (sensor_id, raw_distance, flood_level, status, latitude, longitude, maps_url, timestamp))

        db.commit()
        cur.close()
        return jsonify({"message": "Reading recorded successfully"}), 201
    except Exception as e:
        db.rollback()
        if cur: cur.close()
        return jsonify({"error": str(e)}), 500


@iot_bp.route("/latest", methods=["GET"])
def latest_sensor():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT id, sensor_id, raw_distance, flood_level, status,
               latitude, longitude, maps_url, created_at
        FROM iot_readings
        ORDER BY created_at DESC LIMIT 1
    """)
    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({"error": "No sensor data found"}), 404

    created_at = row.get("created_at")
    if isinstance(created_at, str):
        try:
            created_at_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        except Exception:
            created_at_dt = datetime.now()
    elif isinstance(created_at, datetime):
        created_at_dt = created_at
    else:
        created_at_dt = datetime.now()

    age_seconds = (datetime.now() - created_at_dt).total_seconds()
    is_offline = age_seconds > 30

    row["is_offline"] = is_offline
    row["status"] = "OFFLINE" if is_offline else (row.get("status") or "UNKNOWN")

    try:
        row["flood_level"] = float(row.get("flood_level") or 0)
    except Exception:
        row["flood_level"] = 0.0
    try:
        row["raw_distance"] = float(row.get("raw_distance") or 0)
    except Exception:
        row["raw_distance"] = 0.0

    return jsonify(row), 200


@iot_bp.route("/latest-readings", methods=["GET"])
def latest_readings():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT id, sensor_id, raw_distance, flood_level, status,
               latitude, longitude, maps_url, created_at
        FROM iot_readings
        ORDER BY created_at DESC LIMIT 50
    """)
    rows = cur.fetchall()
    cur.close()
    return jsonify(rows), 200


# ── NEW: Heartbeat endpoint polled every 1 second by frontend ─────────────────
@iot_bp.route("/status", methods=["GET"])
def sensor_status():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""
        SELECT sensor_id, raw_distance, flood_level, status, created_at
        FROM iot_readings
        ORDER BY created_at DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({
            "status": "OFFLINE",
            "flood_level": 0,
            "raw_distance": 0,
            "sensor_id": None
        }), 200

    created_at = row.get("created_at")

    # Handle both datetime object (MySQL connector) and string
    if isinstance(created_at, datetime):
        created_at_dt = created_at
    elif isinstance(created_at, str):
        # Strip T separator just in case old rows have it
        created_at_clean = created_at.replace("T", " ").split(".")[0]
        try:
            created_at_dt = datetime.strptime(created_at_clean, "%Y-%m-%d %H:%M:%S")
        except Exception:
            created_at_dt = datetime.now()
    else:
        created_at_dt = datetime.now()

    age_seconds = (datetime.now() - created_at_dt).total_seconds()

    # 10 seconds buffer: covers 1s ESP32 interval + network jitter
    if age_seconds > 10:
        return jsonify({
            "status": "OFFLINE",
            "flood_level": 0,
            "raw_distance": 0,
            "sensor_id": row.get("sensor_id")
        }), 200

    try:
        flood_level = float(row.get("flood_level") or 0)
    except Exception:
        flood_level = 0.0

    try:
        raw_distance = float(row.get("raw_distance") or 0)
    except Exception:
        raw_distance = 0.0

    return jsonify({
        "status": "ONLINE",
        "flood_level": flood_level,
        "raw_distance": raw_distance,
        "sensor_id": row.get("sensor_id"),
        "sensor_status": row.get("status")  # NORMAL / WARNING / ALARM
    }), 200


@iot_bp.route("/sensor-by-location", methods=["GET"])
def sensor_by_location():
    """Fetch latest sensor data - optionally filtered by location via query param"""
    location = request.args.get('location')  # Optional: barangay name or 'All'
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # Get latest sensor readings (most recent first)
    # If a location is specified, we could filter here if sensors had barangay fields
    # For now, just return the latest sensor(s)
    cur.execute("""
        SELECT id, sensor_id, raw_distance, flood_level, status,
               latitude, longitude, maps_url, created_at
        FROM iot_readings
        ORDER BY created_at DESC LIMIT 1
    """)
    row = cur.fetchone()
    cur.close()

    if not row:
        return jsonify({"error": "No sensor data found"}), 404

    created_at = row.get("created_at")
    if isinstance(created_at, str):
        try:
            created_at_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        except Exception:
            created_at_dt = datetime.now()
    elif isinstance(created_at, datetime):
        created_at_dt = created_at
    else:
        created_at_dt = datetime.now()

    age_seconds = (datetime.now() - created_at_dt).total_seconds()
    is_offline = age_seconds > 30

    row["is_offline"] = is_offline
    row["status"] = "OFFLINE" if is_offline else (row.get("status") or "UNKNOWN")

    try:
        row["flood_level"] = float(row.get("flood_level") or 0)
    except Exception:
        row["flood_level"] = 0.0
    try:
        row["raw_distance"] = float(row.get("raw_distance") or 0)
    except Exception:
        row["raw_distance"] = 0.0

    return jsonify(row), 200


# ── SENSOR MANAGEMENT ENDPOINTS ────────────────────────────────────────────────

@iot_bp.route("/sensors", methods=["GET"])
def get_all_sensors():
    """Fetch all registered sensors with details"""
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT id, name, barangay, description, lat, lng, status, battery_level, 
                   signal_strength, last_update
            FROM sensors
            ORDER BY last_update DESC
        """)
        sensors = cur.fetchall()
        
        for sensor in sensors:
            if sensor['lat']: sensor['lat'] = float(sensor['lat'])
            if sensor['lng']: sensor['lng'] = float(sensor['lng'])
            if sensor['last_update']:
                sensor['last_update'] = sensor['last_update'].isoformat() if isinstance(sensor['last_update'], datetime) else str(sensor['last_update'])
        
        cur.close()
        return jsonify({"sensors": sensors}), 200
    except Exception as e:
        cur.close()
        return jsonify({"error": str(e)}), 500


@iot_bp.route("/sensors/status-all", methods=["GET"])
def get_all_sensors_status():
    """Fetch all sensors with their latest readings"""
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        # Get all registered sensors (include status to check active/inactive)
        cur.execute("SELECT id, name, barangay, lat, lng, status, battery_level, signal_strength FROM sensors")
        sensors = cur.fetchall()
        
        # Get latest reading for EACH sensor
        cur.execute("""
            SELECT r1.sensor_id, r1.flood_level, r1.status as reading_status, r1.created_at, r1.latitude, r1.longitude
            FROM iot_readings r1
            INNER JOIN (
                SELECT sensor_id, MAX(created_at) as max_at
                FROM iot_readings
                GROUP BY sensor_id
            ) r2 ON r1.sensor_id = r2.sensor_id AND r1.created_at = r2.max_at
        """)
        readings = cur.fetchall()
        readings_map = {r['sensor_id']: r for r in readings}
        
        for s in sensors:
            s['lat'] = float(s['lat']) if s['lat'] else 0
            s['lng'] = float(s['lng']) if s['lng'] else 0

            # If sensor is disabled (inactive), force it offline regardless of readings
            is_disabled = s.get('status') == 'inactive'

            latest = readings_map.get(s['id'])
            if latest:
                s['flood_level'] = float(latest['flood_level']) if latest['flood_level'] else 0
                s['reading_status'] = latest['reading_status']
                s['last_seen'] = latest['created_at'].isoformat() if isinstance(latest['created_at'], datetime) else str(latest['created_at'])
                
                if is_disabled:
                    s['is_offline'] = True
                else:
                    # Check if offline by reading age (using local time to match DB)
                    created_at_dt = latest['created_at']
                    age_seconds = (datetime.now() - created_at_dt).total_seconds()
                    s['is_offline'] = age_seconds > 30
            else:
                s['flood_level'] = 0
                s['reading_status'] = 'OFFLINE'
                s['is_offline'] = True
                s['last_seen'] = None

        # Add enabled flag so frontend knows the switch state
        for s in sensors:
            s['enabled'] = s.get('status') != 'inactive'
                
        cur.close()
        return jsonify(sensors), 200
    except Exception as e:
        if cur: cur.close()
        return jsonify({"error": str(e)}), 500




@iot_bp.route("/registers-sensor", methods=["POST"])
def register_sensor():
    """Register a new sensor"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['id', 'name', 'lat', 'lng', 'barangay']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    sensor_id = data.get('id')
    name = data.get('name')
    barangay = data.get('barangay')
    description = data.get('description', '')
    lat = data.get('lat')
    lng = data.get('lng')
    status = data.get('status', 'active')
    battery_level = data.get('battery_level', 100)
    signal_strength = data.get('signal_strength', 'strong')
    
    # Validate coordinates
    try:
        lat = float(lat)
        lng = float(lng)
        if lat < -90 or lat > 90 or lng < -180 or lng > 180:
            return jsonify({"error": "Invalid coordinates"}), 400
    except (TypeError, ValueError):
        return jsonify({"error": "Coordinates must be numeric"}), 400
    
    # Validate status
    valid_statuses = ['active', 'inactive', 'maintenance']
    if status not in valid_statuses:
        return jsonify({"error": f"Status must be one of: {', '.join(valid_statuses)}"}), 400
    
    # Validate signal strength
    valid_signals = ['strong', 'medium', 'weak']
    if signal_strength not in valid_signals:
        return jsonify({"error": f"Signal strength must be one of: {', '.join(valid_signals)}"}), 400
    
    db = get_db()
    cur = db.cursor()
    
    try:
        # Check if sensor already exists
        cur.execute("SELECT id FROM sensors WHERE id = %s", (sensor_id,))
        if cur.fetchone():
            cur.close()
            return jsonify({"error": "Sensor with this ID already exists"}), 409
        
        # Insert new sensor
        cur.execute("""
            INSERT INTO sensors (id, name, barangay, description, lat, lng, status, battery_level, signal_strength)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (sensor_id, name, barangay, description, lat, lng, status, battery_level, signal_strength))
        
        db.commit()
        cur.close()
        
        return jsonify({
            "message": "Sensor registered successfully",
            "sensor": {
                "id": sensor_id,
                "name": name,
                "barangay": barangay,
                "description": description,
                "lat": lat,
                "lng": lng,
                "status": status,
                "battery_level": battery_level,
                "signal_strength": signal_strength
            }
        }), 201
    except Exception as e:
        db.rollback()
        cur.close()
        return jsonify({"error": str(e)}), 500


@iot_bp.route("/sensors/<string:sensor_id>", methods=["PUT"])
def update_sensor(sensor_id):
    """Update sensor information"""
    data = request.get_json()
    
    db = get_db()
    cur = db.cursor()
    
    try:
        # Check if sensor exists
        cur.execute("SELECT id FROM sensors WHERE id = %s", (sensor_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Sensor not found"}), 404
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("name = %s")
            params.append(data['name'])
        
        if 'status' in data:
            valid_statuses = ['active', 'inactive', 'maintenance']
            if data['status'] not in valid_statuses:
                cur.close()
                return jsonify({"error": f"Status must be one of: {', '.join(valid_statuses)}"}), 400
            update_fields.append("status = %s")
            params.append(data['status'])
        
        if 'battery_level' in data:
            update_fields.append("battery_level = %s")
            params.append(data['battery_level'])
        
        if 'signal_strength' in data:
            valid_signals = ['strong', 'medium', 'weak']
            if data['signal_strength'] not in valid_signals:
                cur.close()
                return jsonify({"error": f"Signal strength must be one of: {', '.join(valid_signals)}"}), 400
            update_fields.append("signal_strength = %s")
            params.append(data['signal_strength'])
        
        if not update_fields:
            cur.close()
            return jsonify({"error": "No fields to update"}), 400
        
        update_fields.append("last_update = CURRENT_TIMESTAMP")
        params.append(sensor_id)
        
        query = f"UPDATE sensors SET {', '.join(update_fields)} WHERE id = %s"
        cur.execute(query, params)
        
        db.commit()
        cur.close()
        
        return jsonify({"message": "Sensor updated successfully"}), 200
    except Exception as e:
        db.rollback()
        cur.close()
        return jsonify({"error": str(e)}), 500


@iot_bp.route("/sensors/<string:sensor_id>/toggle", methods=["PATCH"])
def toggle_sensor(sensor_id):
    """Enable or disable a sensor (on/off switch).
    Body: { "enabled": true | false }
    When disabled the sensor is treated as offline everywhere.
    """
    data = request.get_json(silent=True) or {}
    enabled = data.get("enabled")
    if enabled is None:
        return jsonify({"error": "enabled (bool) is required"}), 400

    db = get_db()
    cur = db.cursor()
    try:
        cur.execute("SELECT id FROM sensors WHERE id = %s", (sensor_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Sensor not found"}), 404

        new_status = "active" if enabled else "inactive"
        cur.execute(
            "UPDATE sensors SET status = %s, last_update = CURRENT_TIMESTAMP WHERE id = %s",
            (new_status, sensor_id)
        )
        db.commit()
        cur.close()
        return jsonify({
            "message": f"Sensor {'enabled' if enabled else 'disabled'} successfully",
            "sensor_id": sensor_id,
            "enabled": enabled,
            "status": new_status
        }), 200
    except Exception as e:
        db.rollback()
        if cur:
            cur.close()
        return jsonify({"error": str(e)}), 500


@iot_bp.route("/sensors/<string:sensor_id>", methods=["DELETE"])
def delete_sensor(sensor_id):
    """Delete a sensor"""
    db = get_db()
    cur = db.cursor()
    
    try:
        # Check if sensor exists
        cur.execute("SELECT id FROM sensors WHERE id = %s", (sensor_id,))
        if not cur.fetchone():
            cur.close()
            return jsonify({"error": "Sensor not found"}), 404
        
        # Delete associated water level records first (if foreign key constraint exists)
        cur.execute("DELETE FROM water_levels WHERE sensor_id = %s", (sensor_id,))
        
        # Delete sensor
        cur.execute("DELETE FROM sensors WHERE id = %s", (sensor_id,))
        db.commit()
        cur.close()
        
        return jsonify({"message": "Sensor deleted successfully"}), 200
    except Exception as e:
        db.rollback()
        cur.close()
        return jsonify({"error": str(e)}), 500