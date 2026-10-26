# Model Rocket VTVL Sim

A gamified 2D simulator of a TVC (Thrust Vector Control) model rocket.  
More interactive and lively than my previous versions.

I built this as a digital mirror of my real TVC rocket (currently being fabricated in YSWS).

**Phase 5 is the final and best version** (around 600 lines of code).  
(Note: Phase 5 may have appeared earlier under the name `karman_reusable_rocket`.)

---

## Features

- Throttle + TVC gimbal control
- Adjustable fuel, wind, and target apogee
- COM & COP sliders (stability margin)
- Wind + random gusts
- Parachute on descent( ive added a longer string so that it doesnt look hideous)
- Scoring based on apogee accuracy and landing precision
- Simple flight graph after landing

Physics is simplified for gameplay.

---

## Files

| File                  | Description |
|-----------------------|-----------|
| `Phase1.py`           | First basic version – simple throttle and altitude + background |
| `Phase2.py`           | Added more flight behaviour, controls, and moving background |
| `Phase3.py`           | Improved physics and visuals (includes physics engine from earlier repos) |
| `Phase4.py`           | More complete flight model with extra features |
| `Phase5.py`           | **Final and best version** – full feature set (TVC, fuel, wind, COM/COP, parachute, scoring, etc.) |
| `Types_of_clouds.jpg` | Flight background image |
| `launch_real.JPG`     | Menu / launch background image |

---

## How to Run

**Recommended (best version):**
You also need Pygame:
```bash
pip install pygame
```
## Goal
Try to reach your target apogee and land as close as possible to the pad while keeping the rocket stable.

Your final score is based on apogee accuracy, maximum tilt, and landing offset.

```bash
python Phase5.py
```

