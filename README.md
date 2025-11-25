# Codex

This repository now contains a reusable Python package (`gd/`) extracted from the original `GDv1.ipynb` notebook so the Excel-backed workflow can be reused from a web front end or API service. The notebook remains as a reference UI.

## Python package
- Core helpers live under `gd/` (`config`, `excel`, `catalogs`, `projects`, `metrics`, `suggestions`, and an optional FastAPI surface in `api.py`).
- `requirements.txt` lists the runtime dependencies (`openpyxl`, `fastapi`, `uvicorn`).
- Key environment variables:
  - `GD_EXCEL_PATH` → location of `GD_v1.xlsx` (defaults to the copy in this repo)
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

Endpoints include `/health`, `/catalogs`, `/projects` (create/update by row), `/metrics`, and `/suggestions`.

### Troubleshooting
- **`ModuleNotFoundError: No module named 'uvicorn'`**
  - Make sure you install dependencies with the same interpreter you plan to run: `python -m pip install -r requirements.txt` (repeat after activating `.venv`).
  - If the `uvicorn` shim still fails, call it through the interpreter to avoid PATH mixups: `python -m uvicorn gd.api:app --reload --host 0.0.0.0 --port 8000`.
  - Double-check you are using the intended environment: `which python` should point to `.venv/bin/python` and `python -m pip show uvicorn` should list the package.

## Notebook (legacy)
You can still open `GDv1.ipynb` in Jupyter if you want the ipywidgets UI. Ensure the Excel file and logo are reachable via the same environment variables described above. The notebook will refresh catalogs from the `Datos` sheet and validate dependency column mappings on startup.
