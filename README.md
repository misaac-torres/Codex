# Codex

This repository now contains a reusable Python package (`gd/`) extracted from the original `GDv1.ipynb` notebook so the Excel-backed workflow can be reused from a web front end or API service. The notebook remains as a reference UI.

## Python package
- Core helpers live under `gd/` (`config`, `excel`, `catalogs`, `projects`, `metrics`, `suggestions`, and an optional FastAPI surface in `api.py`).
- `requirements.txt` lists the runtime dependencies (`openpyxl`, `fastapi`, `uvicorn`).
- Key environment variables:
  - `GD_EXCEL_PATH` → location of `GD_v1.xlsx` (defaults to the copy in this repo)
    - Only non-binary Excel formats are supported (e.g., `.xlsx`/`.xlsm`; not `.xlsb`).
  - `GD_LOGO_PATH` → optional path to the Telefónica logo image

### Using the FastAPI server
Install dependencies before running the server (helps avoid `ModuleNotFoundError` for packages like `uvicorn`):
```bash
pip install -r requirements.txt
uvicorn gd.api:app --reload --host 0.0.0.0 --port 8000
```

If you prefer an isolated environment, create and activate a virtual environment first:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### codex/create-attractive-user-front-ui-smyqav
Endpoints include `/health`, `/catalogs`, `/projects` (create/update by row), `/metrics`, and `/suggestions`. The `/docs` route now delivers an attractive Telefónica-styled Swagger UI with a short hero banner inspired by the legacy GDv1 experience; once the server is running you can navigate there for a one-click, try-it-out friendly front end.
=======
Endpoints include `/health`, `/catalogs`, `/projects` (create/update by row), `/metrics`, and `/suggestions`. The root path `/` now delivers an attractive Telefónica-branded landing page with quick links to Swagger UI and deployment guidance so users can launch the API experience in one click.
#### main

### One-click test environment
Run the included helper to provision dependencies and start the FastAPI server in one step:
```bash
./deploy_test_env.sh
```

If you only need the Telefónica-styled Swagger UI for the user front, use the short alias:
```bash
./deploy_user_front.sh
```
Optional environment variables:
- `VENV_DIR` → override the virtualenv location (default: `.venv` at the repo root)
- `PYTHON_BIN` → choose which Python interpreter to use (default: `python3`)
- `PORT` → change the exposed port (default: `8000`)
- `GD_EXCEL_PATH`/`GD_LOGO_PATH` → override workbook and logo paths (auto-detected if not set)
  - A lightweight SVG favicon is bundled at `gd/static/telefonica-favicon.svg` to avoid binary assets in PRs; point `GD_LOGO_PATH` to your own SVG/PNG if you prefer.

### Troubleshooting
- **`ModuleNotFoundError: No module named 'uvicorn'`**
  - Make sure you install dependencies with the same interpreter you plan to run: `python -m pip install -r requirements.txt` (repeat after activating `.venv`).
  - If the `uvicorn` shim still fails, call it through the interpreter to avoid PATH mixups: `python -m uvicorn gd.api:app --reload --host 0.0.0.0 --port 8000`.
  - Double-check you are using the intended environment: `which python` should point to `.venv/bin/python` and `python -m pip show uvicorn` should list the package.

## Notebook (legacy)
You can still open `GDv1.ipynb` in Jupyter if you want the ipywidgets UI. Ensure the Excel file and logo are reachable via the same environment variables described above. The notebook will refresh catalogs from the `Datos` sheet and validate dependency column mappings on startup.
