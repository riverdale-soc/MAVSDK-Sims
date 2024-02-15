"""
Initiate Mission Builder and start the mission
"""

import asyncio
from mavsdk import System
from Mission import Mission, LocationGlobal
import argparse


class SurveyMission:
    def __init__(self, args):
        self.args = args
        vehicle = System()

        self.mission = Mission(args.TargetAltitude, args.Area, args.Cam_FOV, args.MAX_RANGE)

    async def run(self):
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

            # get the current location (home)
            home_base = await vehicle.telemetry.position()
            home = LocationGlobal(home_base.latitude_deg, home_base.longitude_deg, target_altitude)
            self.mission.build_mission(home, args.Area, args.Cam_FOV, args.MAX_RANGE)

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

        await arm_and_takeoff(args.TargetAltitude)

        print("Set default/target airspeed to 3")
        await vehicle.action.set_maximum_speed(3)

        index = 0
        waypoint = self.mission.go_to_next()
        while waypoint is not None:
            print(f"Going to point {index} at {waypoint} ...")
            await vehicle.action.goto_location(waypoint.point)
            waypoint = self.mission.go_to_next()
            index += 1

        # land the vehicle
        print("Landing...")
        await vehicle.action.land()

        # Close the vehicle
        await vehicle.close()

        print("Mission complete")


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument('--TargetAltitude', type=int, default=30)
    args.add_argument('--Area', type=int, default=100*10)
    args.add_argument('--Cam_FOV', type=int, default=160)
    args.add_argument('--MAX_RANGE', type=int, default=150)
    args = args.parse_args()
    sm = SurveyMission(args)
    asyncio.run(sm.run())
