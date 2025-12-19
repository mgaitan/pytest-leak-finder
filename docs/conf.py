from importlib import metadata

project = "pytest-leak-finder"
author = "Martín Gaitán"
copyright = "2021-2025, Martín Gaitán"


def get_version() -> str:
    try:
        return metadata.version("pytest-leak-finder")
    except metadata.PackageNotFoundError:  # pragma: no cover - runtime fallback
        return "unknown"


version = get_version()
release = version

extensions = []

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "alabaster"
html_static_path = ["_static"]
