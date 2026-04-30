from __future__ import annotations

import os

from business_entities import ProjectId

from interface_adapters.outward_interfaces.ftrack_interface import FtrackDataPort
from interface_adapters.outward_interfaces.raw_shot_row import RawShotRow


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
                "ftrack_api is not installed. Install with: pip install 'clean-database-architecture[ftrack]'"
            ) from exc

        if not (self._server_url and self._api_key and self._api_user):
            raise RuntimeError(
                "ftrack credentials missing. Set FTRACK_SERVER_URL, FTRACK_API_USER, FTRACK_API_KEY."
            )

        session = ftrack_api.Session(
            server_url=self._server_url,
            api_key=self._api_key,
            api_user=self._api_user,
        )
        project = session.get("Project", project_id)
        children = project.get("children", [])
        rows: list[RawShotRow] = []
        for ent in children:
            if ent.get("entity_type", "").lower() != "shot":
                continue
            status_obj = ent.get("status")
            status = status_obj.get("name") if isinstance(status_obj, dict) else ""
            rows.append(
                RawShotRow(
                    external_id=ent["id"],
                    name=ent.get("name") or "",
                    code=ent.get("name") or "",
                    sequence=None,
                    status_vendor=str(status or ""),
                )
            )
        return rows

    def update_shot_name(self, project_id: ProjectId, shot_external_id: str, new_name: str) -> None:
        raise RuntimeError(
            "Live ftrack shot rename is not implemented in this demo; use tracking=fake."
        )
