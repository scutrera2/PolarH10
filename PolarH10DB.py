import asyncio
import requests
from bleak import BleakClient
from datetime import datetime

# Supabase Config
SUPABASE_URL = "https://xgsdysggyavrqqemdwky.supabase.co/rest/v1/heart_rate_logs"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhnc2R5c2dneWF2cnFxZW1kd2t5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQ0NTc5MDAsImV4cCI6MjA2MDAzMzkwMH0.L-gV8YefxFtrdP1evIblne-3UJxtDmOeMGzqc2G-kiA"

# Polar H10 BLE Config
POLAR_H10_ADDRESS = "A0:9E:1A:EB:AF:E4"
HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Supabase Headers
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json",
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

async def upload_to_supabase(timestamp, heart_rate):
    """Uploads heart rate data to Supabase with enhanced error handling."""
    payload = {
        "timestamp": timestamp,
        "heart_rate": heart_rate
    }
    try:
        response = requests.post(SUPABASE_URL, json=payload, headers=HEADERS)
        
        print(f"📡 Attempting Upload: {payload}")  # Debugging Output
        
        if response.status_code in [200, 201]:
            print(f"✅ Data uploaded: {heart_rate} BPM at {timestamp}")
        else:
            print(f"⚠️ Upload failed: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Supabase connection error: {e}")

async def handle_hr_data(sender, data):
    """Extracts heart rate data and sends it to Supabase."""
    if len(data) < 2:
        print("⚠️ Invalid heart rate data received.")
        return
    
    heart_rate = data[1]
    timestamp = datetime.utcnow().isoformat()
    print(f"💓 Heart Rate: {heart_rate} BPM at {timestamp}")

    await upload_to_supabase(timestamp, heart_rate)

async def main():
    """Connects to Polar H10 and streams heart rate data to Supabase."""
    try:
        async with BleakClient(POLAR_H10_ADDRESS) as client:
            print("🔗 Connected to Polar H10!")
            await client.start_notify(HEART_RATE_UUID, handle_hr_data)
            print("📶 Receiving heart rate data... Press Ctrl+C to stop.")

            await asyncio.sleep(60)  # Runs for 60 seconds before stopping
            await client.stop_notify(HEART_RATE_UUID)
            
            # ✅ Confirm Data in Supabase with a GET Request
            print("🔍 Fetching stored data from Supabase...")
            response = requests.get(SUPABASE_URL, headers=HEADERS)
            print(f"📝 Supabase Response: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ BLE Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())