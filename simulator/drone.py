import asyncio
import json
import random
import time
import websockets
import httpx

class Drone:
    def __init__(self):
        self.battery = 100.0
        self.altitude = 0.0
        self.speed = 0.0
        self.lat = 34.0700
        self.lng = -118.4398 # UCLA coordinates lmao
        self.is_flying = False

    def update(self):
        # simulates battery drain
        self.battery -= random.uniform(0.01, 0.05)
        if self.battery < 0:
            self.battery =0

        # simulating altitude changes
        if self.is_flying:
            self.altitude += random.uniform(-0.5, 0.8)
            self.altitude = max(0, self.altitude)
        else:
            self.altitude = max(0, self.altitude - random.uniform(0.1, 0.3))
        
        # simulating speed
        if self.is_flying:
            self.speed = random.uniform(0, 10)
        else: 
            self.speed = 0

        # simulating position changes if moving
        if self.speed > 0:
            self.lat += random.uniform(-0.0001, 0.0001)
            self.lng += random.uniform(-0.0001, 0.0001)
    
    def to_dict(self):
        return {
            "battery": self.battery, 
            "altitude": self.altitude,
            "speed": self.speed,
            "lat": self.lat,
            "lng": self.lng,
            "is_flying": self.is_flying,
            "timestamp": time.time()
        }
    
    def toggle_flying(self):
        self.is_flying = not self.is_flying
        if self.is_flying:
            print("Taking off...")
        else:
            print("Landing...")

async def connect_and_send():
    drone = Drone()

    await asyncio.sleep(5)
    drone.toggle_flying()

    uri = "ws://backend:8000/api/telemetry/ws"
    print(f"Attempting to connect to {uri}")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")

            asyncio.create_task(schedule_landing(drone, 60))

            while True:
                drone.update()
                telemetry = drone.to_dict()
                await websocket.send(json.dumps(telemetry))
                print(f"Sent telemetry: Alt={telemetry['altitude']:.2f}m, Batt={telemetry['battery']:.2f}%")
                await asyncio.sleep(1)
    except Exception as e:
        print(f"Error: {e}")

async def schedule_landing(drone, delay):
    await asyncio.sleep(delay)
    if drone.is_flying:
        drone.toggle_flying()

async def main():
    print("Simulator starting...")
    try:
        while True:
            try:
                print(f"Checking if backend is up at http://backend:8000/health")
                async with httpx.AsyncClient() as client:
                    resp = await client.get("http://backend:8000/health")
                    print(f"Backend health check response: {resp.status_code}")
                    if resp.status_code == 200:
                        print("Backend server is up")
                        break
            except Exception as e:
                print(f"Error connecting to backend: {str(e)}")
            print("Backend server not available yet, retrying...")
            await asyncio.sleep(5)

        print("Calling connect_and_send()...")
        await connect_and_send()
    except Exception as e:
        print(f"Fatal error in main(): {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Simulator script started")
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error running main async function: {str(e)}")