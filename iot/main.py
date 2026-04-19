import time, network, urequests, machine, utime

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
WIFI_SSID         = "ZTE_2.4G_w724Q6"
WIFI_PASS         = "H42R2cc9"
BACKEND_URL       = "http://192.168.1.13:5000/api/iot/sensor-readings"
THRESHOLD_URL     = "http://192.168.1.13:5000/api/iot/thresholds"
SENSOR_ID         = "Sensor-02"

# Water detection: reading must be this much less than baseline to count as water
NOISE_TOLERANCE   = 1.0    # cm

# Water is "stable" if flood level changes less than this per loop
STABLE_TOLERANCE  = 0.5    # cm
STABLE_MS         = 10000  # recalibrate after 10 s of stable water

# Send interval
SEND_INTERVAL_MS  = 5000   # 5 seconds

# ─── DEFAULT THRESHOLDS (cm flood depth) ─────────────────────────────────────
threshold_advisory = 10.0
threshold_warning  = 15.0
threshold_critical = 25.0
last_threshold_fetch = -300

# ─── HARDWARE ────────────────────────────────────────────────────────────────
p_trig = machine.Pin(26, machine.Pin.OUT)
p_echo = machine.Pin(27, machine.Pin.IN)
p_trig.value(0)

buzzer = machine.PWM(machine.Pin(4))
buzzer.duty(0)

# ─── BUZZER ──────────────────────────────────────────────────────────────────
def _beep(freq, duty, ms):
    buzzer.freq(freq)
    buzzer.duty(duty)
    utime.sleep_ms(ms)
    buzzer.duty(0)

def buzz_warning():
    """3 short beeps — WARNING."""
    for _ in range(3):
        _beep(2800, 600, 150)
        utime.sleep_ms(100)

def buzz_critical():
    """8 long loud beeps — CRITICAL."""
    for _ in range(8):
        _beep(3500, 900, 600)
        utime.sleep_ms(120)

_last_buzz_level = 0

def handle_buzzer(flood_cm):
    global _last_buzz_level
    if flood_cm >= threshold_critical:
        if _last_buzz_level < 2:
            buzz_critical()
            _last_buzz_level = 2
    elif flood_cm >= threshold_warning:
        if _last_buzz_level < 1:
            buzz_warning()
            _last_buzz_level = 1
    else:
        _last_buzz_level = 0

# ─── WiFi ─────────────────────────────────────────────────────────────────────
def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)   # reset internal state from any previous run
    time.sleep(0.5)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(20):
            if wlan.isconnected(): break
            time.sleep(1)
    return wlan.isconnected()

# ─── THRESHOLD FETCH ─────────────────────────────────────────────────────────
def fetch_thresholds():
    global threshold_advisory, threshold_warning, threshold_critical
    try:
        res  = urequests.get(THRESHOLD_URL, timeout=3.0)
        data = res.json()
        res.close()
        threshold_advisory = float(data.get("advisory_cm", threshold_advisory))
        threshold_warning  = float(data.get("warning_cm",  threshold_warning))
        threshold_critical = float(data.get("critical_cm", threshold_critical))
    except Exception:
        pass

# ─── ULTRASONIC — SINGLE FAST MEASUREMENT ────────────────────────────────────
def measure_distance():
    """
    Single pulse measurement — fast, used in the main loop for real-time tracking.
    Returns distance in cm or None on timeout.
    """
    p_trig.value(0); utime.sleep_ms(2)
    p_trig.value(1); utime.sleep_us(10)
    p_trig.value(0)
    dur = machine.time_pulse_us(p_echo, 1, 40000)
    if dur > 0:
        dist = (dur * 0.0343) / 2
        if 2.0 <= dist <= 400.0:
            return round(dist, 2)
    return None

# ─── CALIBRATION — MEDIAN OF 10 SAMPLES ──────────────────────────────────────
def calibrate():
    """
    Called ONCE at boot only.
    Baseline is locked after boot — moving the sensor does NOT change it.
    Tries up to 5 rounds; falls back to 50 cm if sensor never responds.
    """
    print("[Calibration] Measuring baseline...")
    for attempt in range(5):
        samples = []
        for _ in range(10):
            d = measure_distance()
            if d is not None:
                samples.append(d)
            utime.sleep_ms(80)
        if len(samples) >= 3:
            samples.sort()
            baseline = round(samples[len(samples) // 2], 2)
            print("[Calibration] Baseline locked = {}cm".format(baseline))
            return baseline
        print("[Calibration] Attempt {}/5 — only {}/10 samples, retrying...".format(attempt + 1, len(samples)))
        utime.sleep_ms(500)
    print("[Calibration] Sensor not responding — using default 50cm")
    return 50.0

# ─── STATUS ──────────────────────────────────────────────────────────────────
def classify(flood_cm):
    if flood_cm >= threshold_critical: return "CRITICAL"
    if flood_cm >= threshold_warning:  return "WARNING"
    if flood_cm >= threshold_advisory: return "ADVISORY"
    return "NORMAL"

# ─── MAIN ─────────────────────────────────────────────────────────────────────
print("[FloodGuard V12] Starting...")
connect()
fetch_thresholds()

# Calibrate once at boot — never changes again even if sensor is moved
baseline_cm = calibrate()

last_send_ms     = utime.ticks_ms() - SEND_INTERVAL_MS
last_flood_level = 0.0
stable_since_ms  = None

while True:

    # ── Refresh thresholds every 5 minutes ───────────────────────────────────
    now_s = utime.ticks_ms() // 1000
    if utime.ticks_diff(now_s, last_threshold_fetch) >= 300:
        if network.WLAN(network.STA_IF).isconnected():
            fetch_thresholds()
        last_threshold_fetch = now_s

    # ── Measure ───────────────────────────────────────────────────────────────
    current_dist = measure_distance()
    if current_dist is None:
        current_dist = baseline_cm

    # ── Water detection only ──────────────────────────────────────────────────
    # baseline_cm is fixed — flood = how far water surface is from the floor
    # No water → flood_level = 0
    # Water present → flood_level = baseline - current (depth of water)
    water_detected = current_dist < (baseline_cm - NOISE_TOLERANCE)

    if water_detected:
        flood_level = max(0.0, round(baseline_cm - current_dist, 2))
    else:
        flood_level = 0.0

    # ── Recalibrate when water becomes stable ─────────────────────────────────
    # If water stops rising for STABLE_MS, treat current surface as new floor.
    if water_detected:
        if abs(flood_level - last_flood_level) <= STABLE_TOLERANCE:
            if stable_since_ms is None:
                stable_since_ms = utime.ticks_ms()
            elif utime.ticks_diff(utime.ticks_ms(), stable_since_ms) >= STABLE_MS:
                baseline_cm     = current_dist   # lock to stable water surface
                flood_level     = 0.0
                stable_since_ms = None
                print("[Calibration] Water stable — baseline updated to {}cm".format(baseline_cm))
        else:
            stable_since_ms = None
    else:
        stable_since_ms = None

    last_flood_level = flood_level
    status = classify(flood_level)

    # ── Buzzer ────────────────────────────────────────────────────────────────
    handle_buzzer(flood_level)

    # ── Send every 5 seconds ──────────────────────────────────────────────────
    if utime.ticks_diff(utime.ticks_ms(), last_send_ms) >= SEND_INTERVAL_MS:
        last_send_ms = utime.ticks_ms()

        t  = utime.localtime(utime.time() + 28800)
        ts = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*t[:6])

        print("[{}] Flood: {}cm | Status: {} | Baseline: {}cm".format(
            ts[11:], flood_level, status, baseline_cm))

        payload = {
            "sensor_id":    SENSOR_ID,
            "flood_level":  flood_level,
            "raw_distance": current_dist,
            "status":       status,
            "latitude":     0,
            "longitude":    0,
            "maps_url":     None,
            "timestamp":    ts,
        }
        try:
            if network.WLAN(network.STA_IF).isconnected():
                res = urequests.post(BACKEND_URL, json=payload, timeout=2.0)
                res.close()
            else:
                connect()
        except Exception:
            pass

    utime.sleep_ms(100)
