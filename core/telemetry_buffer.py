# core/telemetry_buffer.py

import threading
import time
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from config.settings import INFLUX_URL, INFLUX_TOKEN, INFLUX_ORG, INFLUX_BUCKET

# Setup InfluxDB client
client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Buffer to store points temporarily
telemetry_buffer = []

# Lock to prevent threading collisions
buffer_lock = threading.Lock()

# Interval (seconds) between batch flushes
FLUSH_INTERVAL = 3

def log_duration(metric_name, duration, tags=None):
    """Add a metric to the local telemetry buffer."""
    try:
        point = Point(metric_name).field("duration", duration)
        if tags:
            for key, value in tags.items():
                point = point.tag(key, value)
        with buffer_lock:
            telemetry_buffer.append(point)
    except Exception as e:
        print(f"⚠️ Failed to queue telemetry point: {e}")

def flush_telemetry():
    """Flush buffered points to InfluxDB every FLUSH_INTERVAL seconds."""
    while True:
        time.sleep(FLUSH_INTERVAL)
        try:
            points_to_write = []  # ✅ Always initialize safely
            with buffer_lock:
                if telemetry_buffer:
                    points_to_write = telemetry_buffer.copy()
                    telemetry_buffer.clear()

            if points_to_write:
                write_api.write(bucket=INFLUX_BUCKET, record=points_to_write)
                print(f"📈 Flushed {len(points_to_write)} telemetry points to InfluxDB")

        except Exception as e:
            print(f"⚠️ Failed to flush telemetry: {e}")

# Start background flusher thread
flush_thread = threading.Thread(target=flush_telemetry, daemon=True)
flush_thread.start()

