import os
import time
import random
import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if not cred_path:
    print("Please set GOOGLE_APPLICATION_CREDENTIALS to run the simulator.")
    exit(1)

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()

def simulate_data():
    """Continuously push fake IoT data to Firestore."""
    print("Starting SmartArena IoT Simulator...")
    try:
        while True:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
            
            # Simulate Crowd Zones
            zones = [
                {"zone_id": "North_Gate", "occupancy": random.randint(100, 5000), "capacity": 5000},
                {"zone_id": "South_Gate", "occupancy": random.randint(100, 5000), "capacity": 5000},
                {"zone_id": "Food_Court_A", "occupancy": random.randint(50, 1000), "capacity": 1000},
            ]
            
            db.collection("iot_telemetry").document("crowd_live").set({
                "zones": zones,
                "updated_at": timestamp
            })
            
            # Simulate Sustainability Metrics
            metrics = {
                "power_usage_kw": random.uniform(150.0, 450.0),
                "water_usage_gal": random.uniform(50.0, 200.0),
                "active_hvac_units": random.randint(10, 40)
            }
            
            db.collection("iot_telemetry").document("sustainability_live").set({
                "metrics": metrics,
                "updated_at": timestamp
            })
            
            print(f"[{timestamp}] Pushed live IoT data...")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nSimulator stopped.")

if __name__ == "__main__":
    simulate_data()
