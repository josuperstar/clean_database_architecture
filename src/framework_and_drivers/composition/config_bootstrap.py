from __future__ import annotations

import os
from pathlib import Path

# Full path to config file; if unset, ``config.ini`` is searched (cwd, then parents of this package).
_ENV_CONFIG_PATH = "CLEAN_DATABASE_CONFIG_INI"


def _discover_config_ini() -> Path | None:
    explicit = os.environ.get(_ENV_CONFIG_PATH, "").strip()
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if p.is_file():
            return p
    cwd = Path.cwd() / "config.ini"
    if cwd.is_file():
        return cwd.resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "config.ini"
        if cand.is_file():
            return cand
    return None


def _parse_env_style_ini(path: Path) -> dict[str, str]:
    """Parse ``KEY=value`` lines (same shape as ``.env``), UTF-8, ``#`` comments."""
    text = path.read_text(encoding="utf-8")
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        out[key] = value
    return out


def bootstrap_config_from_ini() -> Path | None:
    """
    Load ``config.ini`` into the process environment using ``setdefault`` only.

    Keys already present in ``os.environ`` (e.g. exported in the shell or set by the host)
    are left unchanged so deployment secrets override local files.

    Returns the path that was loaded, or ``None`` if no file was found.
    """
    path = _discover_config_ini()
    if path is None:
        return None
    for key, value in _parse_env_style_ini(path).items():
        os.environ.setdefault(key, value)
    return path
