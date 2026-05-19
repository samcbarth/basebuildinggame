# Base Building Game

A low-resolution base-building prototype about building a scrappy outpost, training workers and soldiers, upgrading your base, and surviving enemy waves.

## Browser Play

The GitHub Pages build lives in `docs/` and runs directly in the browser with HTML5 Canvas.

After GitHub Pages is enabled for the `main` branch and `/docs` folder, it will be playable at:

```txt
https://samcbarth.github.io/basebuildinggame/
```

## Run

Desktop Python/Pygame version:

```bat
run.bat
```

Or:

```bat
py -3.12 src\main.py
```

## Current Prototype

- Place mines, turrets, and barracks.
- Train workers for income.
- Train soldiers from barracks.
- Upgrade economy, weapons, and armor.
- Survive enemy waves that attack your buildings.

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
