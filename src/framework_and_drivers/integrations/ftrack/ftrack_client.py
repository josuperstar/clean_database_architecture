from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

from business_entities import ProjectId

from interface_adapters.outward_interfaces.ftrack_interface import FtrackDataPort
from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow


def _hostname_from_ftrack_server_url(server_url: str) -> str | None:
    parsed = urlparse(server_url.strip())
    return parsed.hostname


def _append_host_to_no_proxy_vars(host: str) -> None:
    """Ensure ``requests`` / urllib3 skip the proxy for this host (both env spellings)."""
    for key in ("NO_PROXY", "no_proxy"):
        existing = os.environ.get(key, "")
        parts = [p.strip() for p in existing.split(",") if p.strip()]
        if host in parts:
            continue
        merged = ",".join([*parts, host]) if parts else host
        os.environ[key] = merged


def ensure_ftrack_host_bypasses_proxy(server_url: str) -> None:
    """
    If ``HTTPS_PROXY`` breaks TLS to ftrack (common with local inspection agents), direct
    connections often work. Append the ftrack host from ``server_url`` to ``NO_PROXY`` and
    ``no_proxy`` unless ``FTRACK_AUTO_NO_PROXY`` is ``0`` / ``false`` / ``no`` / ``off``.
    """
    flag = os.environ.get("FTRACK_AUTO_NO_PROXY", "1").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return
    host = _hostname_from_ftrack_server_url(server_url)
    if not host:
        return
    _append_host_to_no_proxy_vars(host)


def _escape_ftrack_query_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def _resolve_ftrack_project(session: Any, project_ref: str) -> Any:
    """
    ``session.get('Project', ref)`` only works when ``ref`` is the entity id. Users often type
    the short **name** (code) or **full_name**; resolve those with a query.
    """
    ref = project_ref.strip()
    if not ref:
        raise RuntimeError("project id is empty")

    project = session.get("Project", ref)
    if project is not None:
        return project

    safe = _escape_ftrack_query_string(ref)
    for attr in ("name", "full_name"):
        query = f'Project where {attr} is "{safe}"'
        found = session.query(query).all()
        if len(found) == 1:
            return found[0]
        if len(found) > 1:
            raise RuntimeError(
                f"Multiple ftrack projects match {ref!r} on {attr!r}. "
                "Use the unique project id from the ftrack URL (…/projects/<id>)."
            )

    raise RuntimeError(
        f"No ftrack Project found for {ref!r}. "
        "Use the project id from the ftrack URL, or the exact short name / full name."
    )


def _ftrack_entity_id(entity: Any) -> str:
    if hasattr(entity, "get"):
        eid = entity.get("id")
    else:
        eid = getattr(entity, "id", None)
    if eid is None:
        raise RuntimeError("ftrack entity has no id")
    return str(eid)


def _ftrack_attr(entity: Any, key: str, default: Any = None) -> Any:
    if hasattr(entity, "get"):
        return entity.get(key, default)
    return getattr(entity, key, default)


def _ftrack_status_vendor(status_obj: Any) -> str:
    if status_obj is None:
        return ""
    if isinstance(status_obj, dict):
        return str(status_obj.get("name") or "")
    return str(getattr(status_obj, "name", None) or "")


def _ftrack_sequence_from_shot_parent(parent: Any) -> str | None:
    if parent is None:
        return None
    ptype = str(_ftrack_attr(parent, "entity_type", "") or "").lower()
    if "sequence" not in ptype:
        return None
    name = _ftrack_attr(parent, "name")
    if name:
        return str(name)
    code = _ftrack_attr(parent, "code")
    return str(code) if code else None


def _ftrack_shot_to_raw_row(ent: Any) -> RawShotRow:
    status_obj = _ftrack_attr(ent, "status")
    parent = _ftrack_attr(ent, "parent")
    return RawShotRow(
        external_id=_ftrack_entity_id(ent),
        name=str(_ftrack_attr(ent, "name") or ""),
        code=str(_ftrack_attr(ent, "name") or ""),
        sequence=_ftrack_sequence_from_shot_parent(parent),
        status_vendor=_ftrack_status_vendor(status_obj),
    )


def _query_shots_for_ftrack_project(session: Any, project: Any) -> list[RawShotRow]:
    """Shots are not necessarily in ``project['children']``; query by project id."""
    safe = _escape_ftrack_query_string(_ftrack_entity_id(project))
    shots = session.query(f'Shot where project.id is "{safe}"').all()
    return [_ftrack_shot_to_raw_row(s) for s in shots if s is not None]


class FtrackClient(FtrackDataPort):
    """ftrack API integration. Optional extra: `[ftrack]`."""

    def __init__(
        self,
        *,
        server_url: str | None = None,
        api_key: str | None = None,
        api_user: str | None = None,
    ) -> None:
        self._server_url = server_url or os.environ.get("FTRACK_SERVER_URL", "")
        self._api_key = api_key or os.environ.get("FTRACK_API_KEY", "")
        self._api_user = api_user or os.environ.get("FTRACK_API_USER", "")

    def find_shots_for_project(self, project_id: ProjectId) -> list[RawShotRow]:
        try:
            import ftrack_api  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "ftrack_api is not installed (PyPI package: ftrack-python-api). Install the optional extra, e.g. "
                "from this repo: pip install -e '.[ftrack]' — or from PyPI: "
                "pip install 'clean-database-architecture[ftrack]'"
            ) from exc

        if not (self._server_url and self._api_key and self._api_user):
            raise RuntimeError(
                "ftrack credentials missing. Set FTRACK_SERVER_URL, FTRACK_API_USER, FTRACK_API_KEY."
            )

        ensure_ftrack_host_bypasses_proxy(self._server_url)

        session = ftrack_api.Session(
            server_url=self._server_url,
            api_key=self._api_key,
            api_user=self._api_user,
        )
        project = _resolve_ftrack_project(session, str(project_id))
        return _query_shots_for_ftrack_project(session, project)

    def update_shot_name(self, project_id: ProjectId, shot_external_id: str, new_name: str) -> None:
        raise RuntimeError(
            "Live ftrack shot rename is not implemented in this demo; use tracking=fake."
        )
