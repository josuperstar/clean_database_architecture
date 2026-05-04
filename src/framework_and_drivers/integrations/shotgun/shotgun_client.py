from __future__ import annotations

import os
from typing import Any

from business_entities import ProjectId

from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow
from interface_adapters.outward_interfaces.shotgun_interface import ShotgunDataPort


def _coerce_sg_status_list_field(value: Any) -> str:
    """
    ``sg_status_list`` may be a short code string, a Status entity dict, or a single-element list.

    Prefer ``code`` (workflow short code, e.g. ``fin``), then ``name`` (often the display label
    ``Final``). The repository adapter maps these to ``ShotStatus`` via ``normalize_vendor_status``.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list) and value:
        return _coerce_sg_status_list_field(value[0])
    if isinstance(value, dict):
        for key in ("code", "name"):
            v = value.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
        return ""
    return str(value).strip()


class ShotgunClient(ShotgunDataPort):
    """ShotGrid / Shotgun API integration (`shotgun_api3`). Optional extra: `[shotgun]`."""

    def __init__(
        self,
        *,
        server_path: str | None = None,
        script_name: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self._server_path = server_path or os.environ.get("SHOTGUN_SERVER_PATH", "")
        self._script_name = script_name or os.environ.get("SHOTGUN_SCRIPT_NAME", "")
        self._api_key = api_key or os.environ.get("SHOTGUN_API_KEY", "")

    def _shotgun(self) -> Any:
        try:
            import shotgun_api3  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise RuntimeError(
                "shotgun_api3 is not installed. Install with: pip install 'clean-database-architecture[shotgun]'"
            ) from exc

        if not (self._server_path and self._script_name and self._api_key):
            raise RuntimeError(
                "ShotGrid credentials missing. Set SHOTGUN_SERVER_PATH, SHOTGUN_SCRIPT_NAME, SHOTGUN_API_KEY."
            )

        return shotgun_api3.Shotgun(
            self._server_path,
            script_name=self._script_name,
            api_key=self._api_key,
        )

    def find_shots_for_project(self, project_id: ProjectId) -> list[RawShotRow]:
        sg = self._shotgun()
        pid = str(project_id)
        try:
            pid_int = int(pid)
            filters = [["project", "is", {"type": "Project", "id": pid_int}]]
        except ValueError:
            filters = [["project.Project.name", "is", pid]]
        fields = ["id", "code", "description", "sg_sequence", "sg_status_list"]
        shots = sg.find("Shot", filters, fields=fields) or []
        rows: list[RawShotRow] = []
        for s in shots:
            seq = s.get("sg_sequence")
            seq_name = seq.get("name") if isinstance(seq, dict) else None
            status = _coerce_sg_status_list_field(s.get("sg_status_list"))
            name = (s.get("description") or s.get("code") or "").strip() or str(s.get("id"))
            rows.append(
                RawShotRow(
                    external_id=str(s.get("id")),
                    name=name,
                    code=str(s.get("code") or ""),
                    sequence=seq_name,
                    status_vendor=str(status),
                )
            )
        return rows

    def update_shot_name(self, project_id: ProjectId, shot_external_id: str, new_name: str) -> None:
        rows = self.find_shots_for_project(project_id)
        if not any(r.external_id == shot_external_id for r in rows):
            raise LookupError(shot_external_id)
        sg = self._shotgun()
        try:
            sid = int(shot_external_id)
        except ValueError as exc:
            raise LookupError(shot_external_id) from exc
        sg.update("Shot", sid, {"description": new_name})
