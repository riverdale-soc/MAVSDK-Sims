"""
Author: Dmitri Lyalikov

This script connects to the Copter and polls for armability and armed status.
We then launch the vehicle and command it to loiter at a specific location. 

"""

from mavsdk import System
import asyncio


async def run():
    # Start a connection to the vehicle
    vehicle = System()
    await vehicle.connect(system_address="udp://:14540")

    async def arm_and_takeoff(target_altitude):
        print("Basic pre-arm checks")

        # Don't try to arm until autopilot is ready
        async def wait_for_armable():
            while not await vehicle.telemetry.health_all_ok():
                print(" Waiting for vehicle to initialise...")
                await asyncio.sleep(1)

        await wait_for_armable()

        print("Arming motors")
        # Copter should arm in GUIDED mode
        await vehicle.action.set_takeoff_altitude(target_altitude)
        await vehicle.action.arm()
        await vehicle.action.takeoff()

        # Confirm vehicle armed before attempting to take off
        while not await vehicle.telemetry.armed():
            print(" Waiting for arming...")
            await asyncio.sleep(1)

        print("Taking off!")

        # Wait until the vehicle reaches a safe height before processing the goto
        async def wait_until_altitude_reached():
            while (await vehicle.telemetry.position()).relative_altitude_m >= target_altitude * 0.95:
                print(" Altitude: ", (await vehicle.telemetry.position()).relative_altitude_m)
                await asyncio.sleep(1)

        await wait_until_altitude_reached()

    await arm_and_takeoff(10)

    print("Set default/target airspeed to 3")
    await vehicle.action.set_maximum_speed(3)

    print("Going to first point for 30 seconds ...")
    point1 = (37.8736, -122.254, 10)
    await vehicle.action.goto_location(*point1)

    # sleep so we can see the change in map
    await asyncio.sleep(30)

    # Loiter at the current location for 30 seconds
    print("Loitering for 30 seconds ...")
    await asyncio.sleep(30)

    # Return to launch
    print("Returning to Launch")
    await vehicle.action.return_to_launch()

    # Close vehicle object before exiting script
    print("Close vehicle object")
    await vehicle.close()

if __name__ == "__main__":
    asyncio.run(run())

