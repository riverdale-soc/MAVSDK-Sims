"""
Author: Dmitri Lyalikov 

This script connects to the Copter and polls for armability and armed status.
Run this simulation in PC Docker Environment. as python connect-arm.py
Careful, we are using python 2.7 here.
"""

from mavsdk import System
import asyncio


async def run():
    # Start a connection to the drone
    drone = System()
    await drone.connect(system_address="udp://:14540")

    # Check if vehicle is armable
    async for is_armable in drone.telemetry.armed():
        print(f"Is armable: {is_armable}")
        break

    # Check if vehicle is armed
    async for is_armed in drone.telemetry.armed():
        print(f"Is armed: {is_armed}")
        break

    async def callback(is_armable):
        print(f"Is armable: {is_armable}")
        print(" Battery: ", await drone.telemetry.battery())
        print(" GPS: ", await drone.telemetry.gps_info())
        print(" System status: ", await drone.telemetry.status_text())
        print(" Attitude: ", await drone.telemetry.attitude_euler())
        print(" Position: ", await drone.telemetry.position())
        print(" Ground speed: ", await drone.telemetry.ground_speed())
        print(" Heading: ", await drone.telemetry.heading())
        print(" Home position: ", await drone.telemetry.home())
        print(" In air: ", await drone.telemetry.in_air())
        print(" Landed state: ", await drone.telemetry.landed_state())
        print(" RC status: ", await drone.telemetry.rc_status())
        print(" Timestamp: ", await drone.telemetry.timestamp())
        print(" Health: ", await drone.telemetry.health())
        print(" Connection info: ", await drone.telemetry.health())
        print(" Arming status: ", await drone.telemetry.armed())
        print(" Flight mode: ", await drone.telemetry.flight_mode())
        print(" Last Heartbeat: ", await drone.telemetry.last_heartbeat())

    drone.subscribe_telemetry(callback)

    async def wait():
        while not await drone.telemetry.health_all_ok():
            print("Waiting for system to be ready")
            await asyncio.sleep(1)

    await asyncio.gather(wait(), asyncio.sleep(5))

    # Close the drone
    await drone.close()

if __name__ == "__main__":
    asyncio.run(run())
