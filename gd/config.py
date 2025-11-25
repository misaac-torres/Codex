"""Shared configuration for the GD backend package.

Environment variables:
- GD_EXCEL_PATH: override the path to the Excel workbook (default: repository GD_v1.xlsx).
- GD_LOGO_PATH: optional path to the Telefónica logo used by front-end shells.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Iterable

from openpyxl.utils import column_index_from_string

# Workbook locations
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXCEL_PATH = REPO_ROOT / "GD_v1.xlsx"
EXCEL_PATH: Path = Path(os.getenv("GD_EXCEL_PATH", DEFAULT_EXCEL_PATH))
LOGO_PATH: Path | None = None
if os.getenv("GD_LOGO_PATH"):
    LOGO_PATH = Path(os.getenv("GD_LOGO_PATH", ""))

# Sheet names
SHEET_PROYECTOS = "ProyectosTI"
SHEET_DATOS = "Datos"
SHEET_SUG = "Sugerencias"

# Row/column layout
START_ROW_PROYECTOS = 12
HEADER_ROW_PROYECTOS = 11

COLS: Dict[str, str] = {
    "ID": "A",
    "Q_RADICADO": "B",
    "PRIORIZADO": "C",
    "ESTADO_PROYECTO": "D",
    "NOMBRE_PROYECTO": "E",
    "DESCRIPCION_PROYECTO": "F",
    "RESPONSABLE_PROYECTO": "G",
    "AREA_SOLICITANTE": "H",
    "FECHA_INICIO": "I",
    "FECHA_ESTIMADA_CIERRE": "J",
    "LINEA_BASE": "K",
    "LINEA_BASE_Q_GESTION": "L",
    "AVANCE": "M",
    "ESTIMADO_AVANCE": "N",
    "PORC_CUMPLIMIENTO": "O",
    "CONTRIBUCION": "P",
    "INICIATIVA_ESTRATEGICA": "Q",
    "TOTAL_DEP": "CN",
    "TOTAL_L": "CO",
    "TOTAL_P": "CP",
    "CUBRIMIENTO_DEP": "CQ",
    "RATING_PO_SYNC": "CR",
}

# Dependency columns
FLAG_START_LETTER = "R"
FLAG_END_LETTER = "BB"
DESC_START_LETTER = "BC"
DESC_END_LETTER = "CM"

FLAG_START_COL = column_index_from_string(FLAG_START_LETTER)
FLAG_END_COL = column_index_from_string(FLAG_END_LETTER)
DESC_START_COL = column_index_from_string(DESC_START_LETTER)
DESC_END_COL = column_index_from_string(DESC_END_LETTER)

# Branding colours used by downstream UIs
PRIMARY_COLOR = "#00a9e0"
DARK_COLOR = "#001b3c"
LIGHT_BG = "#f5f9fc"
CARD_BORDER = "#d0d7de"


def describe_active_paths() -> str:
    """Human-readable summary of current workbook and asset locations."""
    logo = LOGO_PATH if LOGO_PATH is not None else "<not configured>"
    return (
        "Active paths:\n"
        f"- Excel: {EXCEL_PATH}\n"
        f"- Logo:  {logo}\n"
    )


def ensure_required_sheets(sheet_names: Iterable[str]) -> None:
    required = {SHEET_PROYECTOS, SHEET_DATOS}
    missing = required.difference(set(sheet_names))
    if missing:
        raise KeyError(f"Faltan hojas obligatorias en el workbook: {', '.join(sorted(missing))}")
