# Build And Test

## Requirements

- Python 3.12
- Pygame 2.6.1

Install if needed:

```bat
py -3.12 -m pip install -r requirements.txt
```

## Run Locally

### Browser Build

```bat
py -3.12 -m http.server 8000
```

Then open:

```txt
http://localhost:8000/docs/
```

### Desktop Pygame Build

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

The browser build is static and lives in `docs/` for GitHub Pages.

The desktop Python/Pygame prototype remains available through `run.bat`.
