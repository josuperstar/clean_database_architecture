from __future__ import annotations

import os
from typing import Any

from business_entities import ProjectId

from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow
from interface_adapters.outward_interfaces.shotgun_interface import ShotgunDataPort


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

    def find_shots_for_project(self, project_id: ProjectId) -> list[RawShotRow]:
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

        sg: Any = shotgun_api3.Shotgun(
            self._server_path,
            script_name=self._script_name,
            api_key=self._api_key,
        )
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
            status = s.get("sg_status_list") or ""
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
