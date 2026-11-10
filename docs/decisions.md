# Design decisions

Short records: context, options, decision, rationale, consequences.
Newest decisions are added at the bottom.

---

## D1. Build own robot (DIY) instead of buying a ready kit

**Date:** 2026-11-10

**Context.** The project should show modern C++ on Linux with ROS 2 on real hardware, within a
budget of roughly €300–500. A Raspberry Pi 4 Model B 8 GB was already available.

**Options considered.**

| Option | Pros | Cons |
|---|---|---|
| FastBot (~€489, Pi 4 2 GB) | open design, ROS 2 ready | price; 2 GB Pi is tight for Nav2 + SLAM |
| Hiwonder MentorPi (from ~$300, Pi 5) | complete ecosystem | Python-centric, little room for own low-level code |
| TurtleBot 4 Lite (~€2,000) | reference platform | far over budget |
| **DIY: Pololu Romi + 32U4 board + RPLIDAR C1 + own Pi 4** | most own C++ (firmware, driver, odometry); reuses the Pi; cheapest | risk of time lost on hardware issues |

**Decision.** DIY on the Pololu Romi platform.

**Rationale.**
- The interesting work for this project is exactly what a kit hides: the motor-controller protocol,
  the ROS 2 driver, odometry, the speed controller.
- Romi is a well-documented platform with an official Raspberry Pi integration path, which limits
  the hardware risk.
- Reusing the 8 GB Pi 4 keeps the cost to about CHF 295 and gives enough memory for
  ROS 2 Jazzy + Nav2 + SLAM (headless).

**Consequences.** Estimated +15–35 h compared with a kit, of which ~3–11 h is pure overhead
(soldering, hardware debugging); the rest is C++/firmware work that is the point of the project.

---

## D2. Power

**Date:** 2026-11-10

**Context.** The Pi 4 (+ lidar over USB) needs a stable 5 V supply from the 6× AA NiMH pack
(~7.2 V nominal). The Romi 32U4 board has its own 5 V regulator and a Raspberry Pi connector.

**Options.**
1. Power the Pi from the 32U4 board's regulator through the Pi connector (Pololu's default).
2. Separate 5 V regulator (Pololu D36V28F5, 3.2 A) for the Pi and lidar, independent of the board.

**Decision.** Start with option 1 (off-the-shelf, as Pololu designed it). The lidar is powered
from the Pi's USB port.

**Rationale.** Fewest parts and wiring changes; validate first, add complexity only if measured
need. The D36V28F5 was bought as a cheap reserve so a change does not wait for shipping.

**Validation.** After 10–20 minutes of SLAM, check `vcgencmd get_throttled` (undervoltage flags)
and `vcgencmd measure_temp`. Switch to option 2 only if undervoltage shows up; then the board's 5 V
must be separated from the Pi according to Pololu documentation.

---

## D3. Software strategy: off-the-shelf first, then own code

**Date:** 2026-11-10

**Context.** Writing everything from scratch delays the first working robot and leaves no baseline
to compare against.

**Decision.** Get the robot working on existing software first (Pololu examples, `sllidar_ros2`,
SLAM Toolbox, Nav2), then replace selected parts with own C++ one at a time (strangler pattern).

**Rules.**
- Stable ROS 2 interfaces at the seams: `/cmd_vel`, `/odom`, `/scan`. Replacing one component
  does not affect the rest.
- Every replacement comes with a before/after measurement stored in the repo.
- Fixed replacement order (see [README](../README.md#m4--replacement-order)):
  1. ROS 2 driver node in C++,
  2. own I²C protocol (framing, checksum, watchdog),
  3. own odometry with unit tests,
  4. own wheel-speed PID in firmware.
- SLAM and navigation stay off-the-shelf — the algorithm layer is not the goal of this project.

**Rationale.** A working baseline early (milestone M1: keyboard teleop), measurable improvements
later, and each replacement is small enough to finish and review on its own.
