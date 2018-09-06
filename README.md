# Backyard Flyer

This is my submission for the first project in Udacity's Flying Car Nanodegree program. The goal was to make a simulated drone takeoff, fly in a square, and land:

![image of drone flying in a square](backyard_flyer.gif)

The following documentation is my notes on the project, **not** the [original project description](https://github.com/udacity/FCND-Backyard-Flyer).

## Background

Autonomous flight is goverend by two sets of interacting control loops:

### The Autopilot Loop

The autopilot is responsible for low-level maintenance of flight goals. Its responsibilities are analogous to the "aviate" in "aviate, navigate, communicate". Specifically, the autopilot has direct access to the flight sensors and GPS and can maintain station, or be programmed with and achieve a particular heading or destination.

The autopilot loop consists of:

1. control inputs made by the autopilot upon the craft's flight surfaces or motors
2. the motion of the craft as effected by those flight surfaces or motors
3. the readings of the craft's sensors, as effected by the motion of the craft
4. the new control inputs made by the autopilot as effected by its readings of its sensors

### The Flight Computer Loop

The flight computer is responsible for more high-level goals. It might have an ultimate destination in mind (eg: fly from a building's helipad to the air port) and also be responsible for determining the best path to that destination on an up-to-date basis, bearing in mind any obstacles that it either knows about ahead of time or encounters in flight. The flight computer's responsibilities are analogous to the "navigate" in "aviate, navigate, communicate".

The flight computer loop consists of:

1. the destination or heading goal inputs made by the flight computer upon the autopilot
2. the motion of the craft, as achieved by the autopilot
3. the readings of the craft's sensors, as effected by the motion of the craft
4. the new destination or heading goal inputs made the flight computer as effected by its readings of its sensors

For example, the flight computer might program the autopilot with the first of several waypoint destinations en route to the ultimate airport destination. When the flight computer detects that the craft has reached that first waypoint, it might program the autopilot with the second waypoint destination. If, while en route to that second waypoint, the craft detected another aircraft in its flight path, then the autopilot could update the autopilot with a new destination meant to take the craft closer to its ultimate destination while avoiding collision with that second aircraft.

## Assignment

### Task

The assignment provided a simulated quadcopter drone in a simulated physical environment. The assignment also provided the drone with an autopilot. Our challenge was to program a flight computer that could takeoff, fly the drone in a square, and then land the craft.

The central challenge was programming the flight computer in such a way that it could:

1. pursue its goal of flying in a square
2. while also yielding control to any more important, emergent goals

For example, it wouldn't do to let the square-flying goal system keep control in a tight loop while another craft approached and placed itself in the quadcopter's path. In that case, some more import goal system should have the opportunity to intervene and keep the quadcopter from collision.

### Solution

The solution was to program the flight computer as an event-driven state machine: I programmed the flight computer to move through a sequence of states (pre-flight, takeoff, waypoint navigation, landing, post-flight) where each transition was driven by state-updates from the craft sensors. This model of programming would allow the flight computer to pass control to a different state (eg: collision avoidance) if another craft were detected by the sensors.


