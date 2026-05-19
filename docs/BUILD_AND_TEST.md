# Build And Test

## Requirements

- Python 3.12
- Pygame 2.6.1

Install if needed:

```bat
py -3.12 -m pip install -r requirements.txt
```

## Run Locally

```bat
run.bat
```

Or:

```bat
py -3.12 src\main.py
```

## Health Check

```bat
py -3.12 -m py_compile src\main.py src\engine\game.py src\engine\settings.py src\gameplay\buildings.py src\gameplay\units.py src\ai\enemies.py src\combat\projectiles.py src\combat\weapons.py src\ui\hud.py
```

## Current Build Output

No packaged build yet. The current deliverable is the local Python/Pygame prototype.
