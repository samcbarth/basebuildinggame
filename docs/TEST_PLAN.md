# Test Plan

## Smoke Test

1. Run `run.bat`.
2. Confirm the game window opens.
3. Confirm the HUD shows scrap, wave, workers, soldiers, timer, and base HP.

## Feature Test

1. Press `1`, click open ground, and confirm a mine is placed and scrap is spent.
2. Press `2`, place a turret near the HQ, and confirm scrap is spent.
3. Press `3`, place a barracks, then press `S` and confirm soldier count increases.
4. Press `W` and confirm worker count increases.
5. Press `U`, `I`, and `O` when enough scrap is available and confirm messages show upgrades.
6. Press `Space` and confirm enemies spawn from the edges.
7. Confirm turrets and soldiers shoot enemies.
8. Let enemies reach a building and confirm building HP decreases.
9. Press `R` after damage and confirm a building repairs.

## Regression Checklist

- Game launches without a traceback.
- Player can place buildings.
- Scrap cannot go below zero.
- Buildings cannot overlap.
- Enemies spawn and move toward buildings.
- Weapons damage enemies.
- HQ death ends the run.
- Enter restarts after game over.
