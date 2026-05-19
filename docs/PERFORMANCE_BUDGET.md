# Performance Budget

## Target

- 60 FPS on a typical Windows laptop.
- 960x640 output scaled from a 480x320 internal canvas.

## Current Budget

- Enemies on screen: 80 target max before optimization.
- Projectiles on screen: 150 target max before optimization.
- Soldiers on screen: 40 target max before optimization.
- Buildings: 100 target max before optimization.

## Risk Areas

- Naive nearest-enemy checks are fine for the prototype but may need spatial partitioning later.
- Direct enemy movement has no pathfinding cost yet.
