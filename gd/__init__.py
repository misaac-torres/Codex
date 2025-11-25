"""Backend package extracted from the GD_v1 notebook."""
from .config import *  # noqa: F401,F403
from .models import Dependency, Project, Catalogs
from .catalogs import load_catalogs
from .projects import (
    write_project_with_dependencies,
    get_all_project_names,
    summarize_by_equipo,
    summarize_by_proyecto,
    update_project_row_and_dependencies,
)
from .metrics import compute_metrics
from .suggestions import append_suggestion, get_last_suggestions
