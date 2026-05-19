# Game Design

## Working Title

Base Building Game

## Core Loop

1. Spend scrap to place economy and defense buildings.
2. Train workers to increase resource income.
3. Train soldiers and build turrets to resist enemy waves.
4. Buy upgrades to improve economy, weapons, and armor.
5. Survive longer waves and recover between attacks.

## Current Player Goal

Keep the Core HQ alive as enemy waves escalate.

## Controls

```txt
1        Select mine blueprint
2        Select turret blueprint
3        Select barracks blueprint
Left mouse place selected building
Right mouse cancel building placement
W        Train worker
S        Train soldier
U        Upgrade economy
I        Upgrade weapons
O        Upgrade armor
R        Repair the most damaged building
Space    Start next wave early
Esc      Quit
```

## Systems

- Scrap economy: workers and mines generate scrap over time.
- Buildings: HQ, mine, turret, barracks.
- Units: workers are abstracted into income; soldiers guard the HQ and fire at enemies.
- Weapons: turrets and soldiers shoot projectiles at enemies.
- Enemies: waves spawn from map edges and attack the closest building.
- Upgrades: economy, weapons, and armor each have three levels.

## Feel Goals

- Fast to understand.
- Clearly readable at low resolution.
- Scrappy toy-soldier battlefield energy.
- Short recovery windows between waves.

## Current Priority

Make the 5-minute survival loop fun before adding larger content, tech trees, maps, or art.
