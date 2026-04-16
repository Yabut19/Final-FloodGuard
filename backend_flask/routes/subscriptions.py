from flask import Blueprint, request, jsonify
from utils.db import get_db

subscriptions_bp = Blueprint('subscriptions', __name__)

LEVEL_ORDER = ['advisory', 'watch', 'warning', 'critical']


# ─────────────────────────────────────────────────────────────────
# SUBSCRIPTION ENDPOINTS
# ─────────────────────────────────────────────────────────────────

@subscriptions_bp.route('/user/<int:user_id>', methods=['GET'])
def get_subscriptions(user_id):
    """Return all barangays that the user has subscribed to."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT barangay, created_at FROM user_subscriptions WHERE user_id = %s ORDER BY barangay",
        (user_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    return jsonify(rows)


@subscriptions_bp.route('/user/<int:user_id>', methods=['POST'])
def subscribe(user_id):
    """Subscribe a user to one or more barangays (array or single string)."""
    data = request.get_json()
    barangays = data.get('barangays')   # accept list
    barangay  = data.get('barangay')    # or single string

    if barangay and not barangays:
        barangays = [barangay]
    if not barangays:
        return jsonify({"error": "barangay or barangays is required"}), 400

    db = get_db()
    cursor = db.cursor()
    added = []
    for b in barangays:
        try:
            cursor.execute(
                "INSERT IGNORE INTO user_subscriptions (user_id, barangay) VALUES (%s, %s)",
                (user_id, b.strip())
            )
            if cursor.rowcount:
                added.append(b.strip())
        except Exception:
            pass  # duplicate ignored

    db.commit()
    cursor.close()
    return jsonify({"message": f"Subscribed to {len(added)} barangay(s)", "added": added}), 201


@subscriptions_bp.route('/user/<int:user_id>/barangay', methods=['DELETE'])
def unsubscribe(user_id):
    """Unsubscribe a user from a barangay."""
    data = request.get_json()
    barangay = data.get('barangay')
    if not barangay:
        return jsonify({"error": "barangay is required"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "DELETE FROM user_subscriptions WHERE user_id = %s AND barangay = %s",
        (user_id, barangay)
    )
    db.commit()
    removed = cursor.rowcount
    cursor.close()
    return jsonify({"message": "Unsubscribed" if removed else "Subscription not found"})


@subscriptions_bp.route('/user/<int:user_id>/alerts', methods=['GET'])
def get_subscribed_alerts(user_id):
    """Return active alerts relevant to the user's subscribed barangays."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch user's subscriptions
    cursor.execute(
        "SELECT barangay FROM user_subscriptions WHERE user_id = %s",
        (user_id,)
    )
    subs = [row['barangay'] for row in cursor.fetchall()]

    if not subs:
        # No subscriptions — return all active alerts
        cursor.execute(
            "SELECT * FROM alerts WHERE status = 'active' ORDER BY timestamp DESC"
        )
    else:
        # Build placeholders for IN clause
        placeholders = ', '.join(['%s'] * len(subs))
        cursor.execute(
            f"""
            SELECT * FROM alerts
            WHERE status = 'active'
              AND (barangay = 'All' OR barangay IN ({placeholders}))
            ORDER BY timestamp DESC
            """,
            tuple(subs)
        )

    alerts = cursor.fetchall()
    cursor.close()
    return jsonify(alerts)


# ─────────────────────────────────────────────────────────────────
# ESCALATION ENDPOINTS
# ─────────────────────────────────────────────────────────────────

@subscriptions_bp.route('/escalate/<int:alert_id>', methods=['POST'])
def escalate_alert(alert_id):
    """
    Manually escalate an alert to the next severity level.
    Levels: advisory → watch → warning → critical
    """
    data = request.get_json() or {}
    escalated_by = data.get('escalated_by', 'admin')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Fetch current alert
    cursor.execute("SELECT * FROM alerts WHERE id = %s", (alert_id,))
    alert = cursor.fetchone()
    if not alert:
        cursor.close()
        return jsonify({"error": "Alert not found"}), 404

    current_level = alert['level']
    if current_level == 'critical':
        cursor.close()
        return jsonify({"error": "Alert is already at the highest level (critical)"}), 400

    current_idx = LEVEL_ORDER.index(current_level)
    new_level = LEVEL_ORDER[current_idx + 1]

    # Update the alert
    cursor2 = db.cursor()
    cursor2.execute(
        """
        UPDATE alerts
        SET level = %s,
            escalation_count = escalation_count + 1,
            title = CONCAT('[ESCALATED] ', REPLACE(title, '[ESCALATED] ', ''))
        WHERE id = %s
        """,
        (new_level, alert_id)
    )

    # Log the escalation
    cursor2.execute(
        """
        INSERT INTO alert_escalation_log
            (alert_id, from_level, to_level, reason, escalated_by)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (alert_id, current_level, new_level, 'Manual escalation', escalated_by)
    )
    db.commit()
    cursor2.close()
    cursor.close()

    return jsonify({
        "message": f"Alert escalated from '{current_level}' to '{new_level}'",
        "alert_id": alert_id,
        "from_level": current_level,
        "to_level": new_level
    })


@subscriptions_bp.route('/resolve/<int:alert_id>', methods=['POST'])
def resolve_alert(alert_id):
    """Manually resolve (close) an active alert."""
    data = request.get_json() or {}
    resolved_by = data.get('resolved_by', 'admin')

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE alerts SET status = 'resolved' WHERE id = %s AND status = 'active'",
        (alert_id,)
    )
    db.commit()
    updated = cursor.rowcount
    cursor.close()

    if not updated:
        return jsonify({"error": "Alert not found or already resolved"}), 404

    return jsonify({"message": "Alert resolved successfully", "alert_id": alert_id})


@subscriptions_bp.route('/escalation-log/<int:alert_id>', methods=['GET'])
def get_escalation_log(alert_id):
    """Return full escalation history for an alert."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM alert_escalation_log WHERE alert_id = %s ORDER BY escalated_at ASC",
        (alert_id,)
    )
    log = cursor.fetchall()
    cursor.close()
    return jsonify(log)


@subscriptions_bp.route('/auto-escalate', methods=['POST'])
def auto_escalate():
    """
    System-triggered endpoint: checks verified report counts per barangay.
    - 2+ verified reports → create/upgrade alert to 'watch' if not already >= watch
    - 5+ verified reports → create/upgrade alert to 'warning' if not already >= warning
    - 8+ verified reports → create/upgrade alert to 'critical' if not already critical
    Can be called after verifying a report (POST /api/reports/<id>/status).
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)

    THRESHOLDS = [
        (8, 'critical'),
        (5, 'warning'),
        (2, 'watch'),
    ]

    # Count verified reports per barangay in last 6 hours
    cursor.execute("""
        SELECT location AS barangay, COUNT(*) AS count
        FROM reports
        WHERE status = 'verified'
          AND timestamp >= NOW() - INTERVAL 6 HOUR
        GROUP BY location
    """)
    barangay_counts = cursor.fetchall()

    results = []
    for row in barangay_counts:
        barangay = row['barangay']
        count = row['count']

        target_level = None
        for threshold, level in THRESHOLDS:
            if count >= threshold:
                target_level = level
                break

        if not target_level:
            continue

        # Check if there's already an active alert for this barangay at or above target
        cursor2 = db.cursor(dictionary=True)
        cursor2.execute("""
            SELECT id, level FROM alerts
            WHERE status = 'active'
              AND (barangay = %s OR barangay = 'All')
            ORDER BY FIELD(level, 'advisory', 'watch', 'warning', 'critical') DESC
            LIMIT 1
        """, (barangay,))
        existing = cursor2.fetchone()

        if existing:
            existing_idx = LEVEL_ORDER.index(existing['level'])
            target_idx = LEVEL_ORDER.index(target_level)

            if existing_idx >= target_idx:
                # Already at or above required level
                cursor2.close()
                continue

            # Escalate existing alert
            cursor2.execute(
                """
                UPDATE alerts SET level = %s, escalation_count = escalation_count + 1
                WHERE id = %s
                """,
                (target_level, existing['id'])
            )
            cursor2.execute(
                """
                INSERT INTO alert_escalation_log
                    (alert_id, from_level, to_level, reason, escalated_by)
                VALUES (%s, %s, %s, %s, 'system')
                """,
                (existing['id'], existing['level'], target_level,
                 f'Auto-escalated: {count} verified reports in last 6h')
            )
            db.commit()
            results.append({
                "barangay": barangay,
                "action": "escalated",
                "alert_id": existing['id'],
                "to_level": target_level
            })
        else:
            # Create a new alert for this barangay
            cursor2.execute(
                """
                INSERT INTO alerts (title, description, level, barangay, status, timestamp)
                VALUES (%s, %s, %s, %s, 'active', NOW())
                """,
                (
                    f"Flood Alert — {barangay}",
                    f"Automatic alert: {count} verified flood report(s) received from {barangay} in the last 6 hours.",
                    target_level,
                    barangay
                )
            )
            new_id = cursor2.lastrowid
            cursor2.execute(
                """
                INSERT INTO alert_escalation_log
                    (alert_id, from_level, to_level, reason, escalated_by)
                VALUES (%s, NULL, %s, %s, 'system')
                """,
                (new_id, target_level,
                 f'Auto-created: {count} verified reports in last 6h')
            )
            db.commit()
            results.append({
                "barangay": barangay,
                "action": "created",
                "alert_id": new_id,
                "level": target_level
            })
        cursor2.close()

    cursor.close()
    return jsonify({
        "message": f"Auto-escalation processed {len(results)} barangay(s)",
        "results": results
    })
