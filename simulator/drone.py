import asyncio
import json
import random
import time
import websockets
import httpx
import uuid

class Drone:
    def __init__(self, drone_id, name, initial_lat=34.0700, initial_lng=-118.4398, battery_capacity=100.0):
        self.id = drone_id
        self.name = name
        self.battery = battery_capacity
        self.altitude = 0.0
        self.speed = 0.0
        self.lat = initial_lat
        self.lng = initial_lng
        self.is_flying = False
        self.battery_drain_rate = random.uniform(0.01, 0.05)  # Each drone has different battery consumption
        self.max_altitude = random.uniform(10.0, 30.0)  # Different max altitude per drone
        self.max_speed = random.uniform(8.0, 15.0)  # Different max speed per drone

    def update(self):
        # Simulates battery drain
        self.battery -= self.battery_drain_rate
        if self.battery < 0:
            self.battery = 0
            if self.is_flying:
                self.is_flying = False  # Force landing if battery dies

        # Simulating altitude changes
        if self.is_flying:
            altitude_change = random.uniform(-0.5, 0.8)
            self.altitude += altitude_change
            self.altitude = min(max(0, self.altitude), self.max_altitude)
        else:
            self.altitude = max(0, self.altitude - random.uniform(0.1, 0.3))
        
        # Simulating speed
        if self.is_flying:
            self.speed = random.uniform(0, self.max_speed)
        else: 
            self.speed = 0

        # Simulating position changes if moving
        if self.speed > 0:
            self.lat += random.uniform(-0.0001, 0.0001) * self.speed / 5
            self.lng += random.uniform(-0.0001, 0.0001) * self.speed / 5
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "battery": self.battery, 
            "altitude": self.altitude,
            "speed": self.speed,
            "lat": self.lat,
            "lng": self.lng,
            "is_flying": self.is_flying,
            "timestamp": time.time()
        }
    
    def toggle_flying(self):
        if self.battery <= 5.0 and not self.is_flying:
            print(f"Drone {self.name} battery too low for takeoff!")
            return
            
        self.is_flying = not self.is_flying
        if self.is_flying:
            print(f"Drone {self.name} taking off...")
        else:
            print(f"Drone {self.name} landing...")

async def schedule_landing(drone, delay):
    await asyncio.sleep(delay)
    if drone.is_flying:
        drone.toggle_flying()

async def connect_and_send():
    # Create multiple drones with different parameters
    drones = [
        Drone(str(uuid.uuid4()), "Alpha", initial_lat=34.0700, initial_lng=-118.4398, battery_capacity=100.0),
        Drone(str(uuid.uuid4()), "Beta", initial_lat=34.0705, initial_lng=-118.4388, battery_capacity=95.0),
        Drone(str(uuid.uuid4()), "Gamma", initial_lat=34.0695, initial_lng=-118.4408, battery_capacity=98.0),
        Drone(str(uuid.uuid4()), "Delta", initial_lat=34.0710, initial_lng=-118.4378, battery_capacity=90.0),
        Drone(str(uuid.uuid4()), "Epsilon", initial_lat=34.0690, initial_lng=-118.4418, battery_capacity=97.0)
    ]

    # Stagger drone takeoffs
    takeoff_delays = [5, 10, 15, 20, 25]
    landing_delays = [60, 70, 80, 90, 100]
    
    uri = "ws://backend:8000/api/telemetry/ws"
    print(f"Attempting to connect to {uri}")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server")

            # Schedule takeoffs with different delays
            for i, drone in enumerate(drones):
                asyncio.create_task(delayed_takeoff(drone, takeoff_delays[i]))
                asyncio.create_task(schedule_landing(drone, landing_delays[i]))

            while True:
                # Update and send data for all drones
                all_telemetry = []
                for drone in drones:
                    drone.update()
                    telemetry = drone.to_dict()
                    all_telemetry.append(telemetry)
                    print(f"Drone {drone.name}: Alt={telemetry['altitude']:.2f}m, Batt={telemetry['battery']:.2f}%")
                
                # Send combined data
                await websocket.send(json.dumps({"drones": all_telemetry}))
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"Error: {e}")

async def delayed_takeoff(drone, delay):
    await asyncio.sleep(delay)
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
    asyncio.run(main())