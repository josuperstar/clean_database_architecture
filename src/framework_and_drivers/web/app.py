from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from framework_and_drivers.composition.factory import build_list_shots_controller
from framework_and_drivers.view_sinks.web_shots_sink import WebPresentationResult
from interface_adapters.controllers.request_models import ListShotsRequestModel

app = FastAPI(title="Shots listing (Clean Architecture demo)", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/shots")
def list_shots(
    project_id: str = Query(..., description="Project id or code"),
    tracking: str | None = Query(None, description="Override TRACKING_BACKEND"),
    fake_vendor: str | None = Query(None, description="When fake: shotgun|ftrack|kitsu"),
) -> JSONResponse:
    result = WebPresentationResult()
    controller = build_list_shots_controller(
        tracking=tracking,
        ui="web",
        web_result=result,
        fake_vendor=fake_vendor,
    )
    controller.handle(ListShotsRequestModel(project_id=project_id))
    if result.error is not None:
        return JSONResponse({"error": result.error}, status_code=400)
    assert result.view_model is not None
    vm = result.view_model
    payload = {
        "project_id": vm.project_id,
        "rows": [
            {
                "shot_id": r.shot_id,
                "name": r.name,
                "code": r.code,
                "sequence": r.sequence,
                "status_label": r.status_label,
                "color_hint": r.color_hint.value,
                "font_emphasis": r.font_emphasis.value,
            }
            for r in vm.rows
        ],
    }
    return JSONResponse(payload)
