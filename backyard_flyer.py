import argparse
import time
from enum import Enum

import numpy as np

from udacidrone import Drone
from udacidrone.connection import MavlinkConnection, WebSocketConnection  # noqa: F401
from udacidrone.messaging import MsgID


class States(Enum):
    MANUAL = 0
    ARMING = 1
    TAKEOFF = 2
    WAYPOINT = 3
    LANDING = 4
    DISARMING = 5


class BackyardFlyer(Drone):

    def __init__(self, connection):
        super().__init__(connection)
        self.target_position = np.array([0.0, 0.0, 0.0])
        # self.all_waypoints = []
        self.remaining_waypoints = self.calculate_box()
        self.in_mission = True
        self.check_state = {}

        # initial state
        self.flight_state = States.MANUAL

        # TODO: Register all your callbacks here
        self.register_callback(MsgID.LOCAL_POSITION, self.local_position_callback)
        self.register_callback(MsgID.LOCAL_VELOCITY, self.velocity_callback)
        self.register_callback(MsgID.STATE, self.state_callback)

    def local_position_callback(self):
        """
        This triggers when `MsgID.LOCAL_POSITION` is received and self.local_position contains new data
        """
        
        # If we are in the takeoff phase...
        if self.flight_state == States.TAKEOFF:
            height = abs(self.local_position[2])
            target_height = self.target_position[2]

            # and we're less than .1m from the target height...
            if abs(height - target_height) < .1:

                # then transition into waypoint phase.
                self.waypoint_transition()

        # If we are in waypoint phase...
        elif self.flight_state == States.WAYPOINT:
            position = np.concatenate((
                    self.local_position[:2],
                    abs(self.local_position[2:]),       # Correct for negative alt
                ))


            # and we're less than .3m (using city-block distance) from target...
            if sum(abs(self.target_position - position)) < .3:
                
                # and there are remaining waypoints...
                if self.remaining_waypoints:
                    # then transition to the next waypoint.
                    self.waypoint_transition()

                else:
                    # else, land.
                    self.landing_transition()
                

    def velocity_callback(self):
        """
        This triggers when `MsgID.LOCAL_VELOCITY` is received and self.local_velocity contains new data
        """
        if self.flight_state == States.LANDING:
            if ((self.global_position[2] - self.global_home[2] < 0.1) and abs(self.local_position[2]) < 0.01):
                self.disarming_transition()

    def state_callback(self):
        """
        This triggers when `MsgID.STATE` is received and self.armed and self.guided contain new data
        """
        if not self.in_mission:
            return

        try:
            transition = {
                States.MANUAL: self.arming_transition,
                States.ARMING: self.takeoff_transition,
                States.DISARMING: self.manual_transition,
            }[self.flight_state]
        except KeyError:
            return

        transition()

    def calculate_box(self):
        scale = 5.0
        height = 3.0

        return [ 
                np.array([0.0, 0.0, height]),
                np.array([0.0, scale, height]),
                np.array([scale, scale, height]),
                np.array([scale, 0.0, height]),
                np.array([0.0, 0.0, height]),
               ]
            

    def arming_transition(self):
        print("arming transition")

        self.take_control()
        self.arm()

        self.set_home_position(*self.global_position)

        self.flight_state = States.ARMING

    def takeoff_transition(self):
        print("takeoff transition")
        target_altitude = 3.0
        self.target_position[2] = target_altitude
        self.takeoff(target_altitude)
        self.flight_state = States.TAKEOFF

    def waypoint_transition(self):
        print("waypoint transition")
        next_waypoint = self.remaining_waypoints.pop(0)

        self.target_position = next_waypoint
        self.cmd_position(*next_waypoint, 0)

        self.flight_state = States.WAYPOINT


    def landing_transition(self):
        print("landing transition")
        self.land()
        self.flight_state = States.LANDING

    def disarming_transition(self):
        print("disarm transition")
        self.disarm()
        self.flight_state = States.DISARMING

    def manual_transition(self):
        print("manual transition")

        self.release_control()
        self.stop()
        self.in_mission = False
        self.flight_state = States.MANUAL

    def start(self):
        print("Creating log file")
        self.start_log("Logs", "NavLog.txt")
        print("starting connection")
        self.connection.start()
        print("Closing log file")
        self.stop_log()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5760, help='Port number')
    parser.add_argument('--host', type=str, default='127.0.0.1', help="host address, i.e. '127.0.0.1'")
    args = parser.parse_args()

    conn = MavlinkConnection('tcp:{0}:{1}'.format(args.host, args.port), threaded=False, PX4=False)
    #conn = WebSocketConnection('ws://{0}:{1}'.format(args.host, args.port))
    drone = BackyardFlyer(conn)
    time.sleep(2)
    drone.start()
