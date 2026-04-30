from __future__ import annotations

import os

from business_entities import ProjectId

from interface_adapters.outward_interfaces.kitsu_interface import KitsuDataPort
from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow


class KitsuClient(KitsuDataPort):
    """Kitsu / Zou integration via `gazu`. Optional extra: `[kitsu]`."""

    def __init__(
        self,
        *,
        host: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> None:
        self._host = host or os.environ.get("KITSU_HOST", "")
        self._email = email or os.environ.get("KITSU_EMAIL", "")
        self._password = password or os.environ.get("KITSU_PASSWORD", "")

    def find_shots_for_project(self, project_id: ProjectId) -> list[RawShotRow]:
        try:
            import gazu  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "gazu is not installed. Install with: pip install 'clean-database-architecture[kitsu]'"
            ) from exc

        if not (self._host and self._email and self._password):
            raise RuntimeError("Kitsu credentials missing. Set KITSU_HOST, KITSU_EMAIL, KITSU_PASSWORD.")

        gazu.client.set_host(self._host)
        gazu.log_in(self._email, self._password)
        shots = gazu.shot.all_shots_for_project({"id": str(project_id)}) or []
        rows: list[RawShotRow] = []
        for s in shots:
            st = s.get("task_status") or s.get("status") or {}
            status_name = st.get("short_name") or st.get("name") or ""
            rows.append(
                RawShotRow(
                    external_id=str(s.get("id", "")),
                    name=str(s.get("name", "")),
                    code=str(s.get("name", "")),
                    sequence=None,
                    status_vendor=str(status_name),
                )
            )
        return rows

    def update_shot_name(self, project_id: ProjectId, shot_external_id: str, new_name: str) -> None:
        raise RuntimeError(
            "Live Kitsu shot rename is not implemented in this demo; use tracking=fake."
        )
