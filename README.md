# mobile-robot-platform

Indoor autonomous mobile robot — ROS 2 Jazzy, C++, lidar SLAM + Nav2, Raspberry Pi 4 + Pololu Romi.

## Goal

One project on real hardware, built the way production systems are built: modern C++ on Linux,
clear architecture, tests, measurements, and written-down decisions.

The focus is **systems engineering for robotics** — drivers, communication protocols, concurrency,
reliability, testability and tooling (e.g. record & replay) — not research on new algorithms.
SLAM and navigation come from proven open-source stacks (SLAM Toolbox, Nav2).

## Hardware (summary)

| Role | Part |
|---|---|
| Chassis, motors, wheels | Pololu Romi chassis kit, 2× 120:1 HP motors |
| Wheel encoders | Pololu Romi encoder pair kit, 12 CPR |
| Motor control, power | Pololu Romi 32U4 Control Board (ATmega32U4) |
| Main computer | Raspberry Pi 4 Model B, 8 GB |
| Lidar | Slamtec RPLIDAR C1 |
| Power | 6× AA NiMH (Panasonic eneloop) |

Full parts list with part numbers and prices: [docs/bom.md](docs/bom.md).

## Status

| Area | State |
|---|---|
| Hardware | 🟡 parts ordered (2026-11-10), waiting for delivery |
| Assembly | ⚪ not started |
| Software | ⚪ not started |

## Milestones

| # | Milestone | Done when |
|---|---|---|
| M0 | Parts and documentation | BOM, decisions and photos in the repo |
| M1 | **Teleop on off-the-shelf software** | Robot drives from the keyboard (`/cmd_vel`), using Pololu's examples and existing ROS 2 packages only |
| M2 | Lidar + SLAM | `/scan` from RPLIDAR C1, map of a room built with SLAM Toolbox |
| M3 | Autonomous navigation | Nav2 drives the robot to a goal on the saved map |
| M4 | Own C++ replaces off-the-shelf parts | Each replacement (below) merged with before/after measurements |
| M5 | Natural-language commands | LLM produces a plan, deterministic C++ validates and executes it |

### M4 — replacement order

Start from working off-the-shelf components, then replace them one at a time with own code
([strangler pattern](docs/decisions.md#d3-software-strategy-off-the-shelf-first-then-own-code)).
The ROS 2 interfaces `/cmd_vel`, `/odom`, `/scan` stay fixed, so one swap does not touch the rest.

| # | Off-the-shelf at start | Replaced by |
|---|---|---|
| 1 | Pololu Python example on the Pi | ROS 2 driver node in C++ |
| 2 | I²C protocol from the Pololu example | Own protocol: framing, checksum, watchdog |
| 3 | Simple / ready-made odometry | Own odometry + unit tests |
| 4 | PID from the example firmware | Own wheel-speed PID in firmware |
| — | `sllidar_ros2`, SLAM Toolbox, Nav2 | stay as they are |

## Repository layout

```
docs/
  bom.md          parts list
  decisions.md    design decisions with rationale
  photos/         parts and assembly photos (resized, metadata stripped)
.github/workflows/photos.yml   CI: photo check
scripts/
  prepare_photos.py   resize + strip EXIF before committing photos
```

## Use of AI tools

Generated with AI help: package skeletons, launch files, URDF, Nav2/SLAM parameters, helper scripts,
code review. Written by hand (AI for review only): the C++ driver node, the I²C protocol,
odometry and the PID controller — the M4 replacements.
