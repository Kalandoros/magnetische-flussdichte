import sys
import traceback
from functools import lru_cache
from pathlib import Path
import json

from src.utils import traceback_detail

_MAPPINGS_PATH = Path(__file__).with_name("mapping.json")
_REVERSE_MAPPINGS_PATH = Path(__file__).with_name("mappingreversed.json")

@lru_cache(maxsize=1)
def _load_field_mappings() -> dict[str, dict[str, str]]:
    try:
        with _MAPPINGS_PATH.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        error_msg = traceback_detail.get_exception_message(e)
        sys.stderr.write(f"{error_msg}\n")
        traceback.print_exc(limit=10, file=sys.stderr, chain=True)
        raise

@lru_cache(maxsize=1)
def _load_reverse_field_mappings() -> dict[str, dict[str, str]]:
    try:
        with _REVERSE_MAPPINGS_PATH.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        error_msg = traceback_detail.get_exception_message(e)
        sys.stderr.write(f"{error_msg}\n")
        traceback.print_exc(limit=10, file=sys.stderr, chain=True)
        raise

@lru_cache(maxsize=5)
def get_mapping(mapping: str) -> dict[str, str]:
    # Für den Excel import zum Laden der Vorlage. Benutzt das str Argument als mapping key.
    key = mapping
    try:
        return _load_field_mappings()[key]
    except KeyError as e:
        error_msg = traceback_detail.get_exception_message(e)
        sys.stderr.write(f"{error_msg}\n")
        traceback.print_exc(limit=10, file=sys.stderr, chain=True)
        raise ValueError(f"No mapping for template: {key}") from e

@lru_cache(maxsize=5)
def get_reverse_mapping(template_path: str | Path) -> dict[str, str]:
    # Für den Excel export. Benutzt den Datei-Namen vom Template path als mapping key.
    key = Path(template_path).name
    try:
        return _load_reverse_field_mappings()[key]
    except KeyError as e:
        error_msg = traceback_detail.get_exception_message(e)
        sys.stderr.write(f"{error_msg}\n")
        traceback.print_exc(limit=10, file=sys.stderr, chain=True)
        raise ValueError(f"No mapping for template: {key}") from e
