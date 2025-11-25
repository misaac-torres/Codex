"""Persistence helpers for the Feedback/Sugerencias sheet."""
from __future__ import annotations

from .config import EXCEL_PATH
from .excel import get_ws_sugerencias, load_workbook


def append_suggestion(usuario: str, texto: str, path=EXCEL_PATH):
    wb = load_workbook(path)
    ws = get_ws_sugerencias(wb)

    next_row = ws.max_row + 1
    if next_row == 2 and ws["A1"].value is None:
        ws["A1"] = "Usuario"
        ws["B1"] = "Sugerencia"
        next_row = 2

    ws.cell(row=next_row, column=1).value = usuario or ""
    ws.cell(row=next_row, column=2).value = texto or ""
    wb.save(path)


def get_last_suggestions(limit: int = 5, path=EXCEL_PATH):
    wb = load_workbook(path)
    ws = get_ws_sugerencias(wb)

    rows = []
    for row in range(2, ws.max_row + 1):
        usuario = ws.cell(row=row, column=1).value
        texto = ws.cell(row=row, column=2).value
        if usuario is None and texto is None:
            continue
        rows.append(
            {
                "usuario": str(usuario) if usuario is not None else "",
                "texto": str(texto) if texto is not None else "",
            }
        )

    if not rows:
        return []

    return rows[-limit:]
