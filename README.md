# Codex

Single Jupyter notebook app (`GDv1.ipynb`) that manages project intake/metrics against the `GD_v1.xlsx` workbook using `openpyxl`, `ipywidgets`, and `matplotlib`.

## Running
1. Open `GDv1.ipynb` in Jupyter (Voilá/Notebook).
2. Ensure the Excel file and Telefónica logo are reachable. You can override default paths via environment variables:
   - `GD_EXCEL_PATH` → location of `GD_v1.xlsx`
   - `GD_LOGO_PATH` → path to the Telefónica logo image
   - `GD_WRITE_DATA_DICTIONARY` → set to `0`/`false`/`no` to avoid auto-escribir el diccionario de datos en `Datos`
3. Run the cells; the notebook will refresh catalogs from the `Datos` sheet and validate dependency column mappings.

## Utilities
- The notebook auto-writes a **data dictionary** into the `Datos` sheet documenting key columns and dependency ranges.
- Dependency mappings are validated against the configured flag/description ranges; inconsistencies are printed as warnings.
- Call `export_support_modules()` from the notebook to generate reusable helper modules in `./gd_modules/` if you want to start modularizing the code.
