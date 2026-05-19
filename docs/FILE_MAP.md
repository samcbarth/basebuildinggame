# File Map

## Runtime

- `docs/index.html`: GitHub Pages browser-playable landing page.
- `docs/styles.css`: responsive page and control-panel styling.
- `docs/game.js`: browser-native Canvas implementation of the playable prototype.
- `src/main.py`: application entry point.
- `src/engine/settings.py`: resolution, grid, timing, and color constants.
- `src/engine/game.py`: main game loop, input handling, economy, wave flow, placement, and rendering orchestration.
- `src/gameplay/buildings.py`: building definitions and building drawing.
- `src/gameplay/units.py`: worker roster and soldier unit model.
- `src/ai/enemies.py`: enemy model and spawn helper.
- `src/combat/projectiles.py`: projectile model.
- `src/combat/weapons.py`: targeting and projectile firing helpers.
- `src/ui/hud.py`: HUD rendering.

## Project

- `README.md`: quick overview and controls.
- `run.bat`: Windows launcher.
- `requirements.txt`: Python dependency list.

## Documentation

- `docs/GAME_DESIGN.md`: current design and loop.
- `docs/BUILD_AND_TEST.md`: run and health-check commands.
- `docs/TEST_PLAN.md`: smoke, feature, and regression checks.
- `docs/FILE_MAP.md`: important file responsibilities.
- `docs/KNOWN_ISSUES.md`: active issues and placeholders.
- `docs/ROADMAP.md`: next development priorities.
- `docs/CHANGELOG.md`: meaningful changes.
