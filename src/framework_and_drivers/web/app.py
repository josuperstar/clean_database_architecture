from __future__ import annotations

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from framework_and_drivers.composition.factory import (
    build_list_shots_controller,
    build_update_shot_name_controller_web,
)
from framework_and_drivers.view_sinks.web_shots_sink import WebPresentationResult
from interface_adapters.controllers.request_models import ListShotsRequestModel, UpdateShotNameRequestModel
from interface_adapters.presenters.update_shot_name_presenter import WebRenamePresentationResult

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
                "sequence": r.sequence,
                "status_label": r.status_label,
                "color_hint": r.color_hint.value,
                "font_emphasis": r.font_emphasis.value,
            }
            for r in vm.rows
        ],
    }
    return JSONResponse(payload)


class RenameShotBody(BaseModel):
    project_id: str = Field(..., description="Project id or code")
    shot_id: str = Field(..., description="Shot external id in the tracker")
    new_name: str = Field(..., description="Must match <sequence>_<digits> (sequence from shot if omitted)")
    project_code: str | None = Field(
        None,
        description="Optional override for the first name segment (defaults to shot sequence)",
    )


@app.post("/shots/rename")
def rename_shot(
    body: RenameShotBody,
    tracking: str | None = Query(None, description="Override TRACKING_BACKEND"),
    fake_vendor: str | None = Query(None, description="When fake: shotgun|ftrack|kitsu"),
) -> JSONResponse:
    result = WebRenamePresentationResult()
    controller = build_update_shot_name_controller_web(
        tracking=tracking,
        fake_vendor=fake_vendor,
        web_result=result,
    )
    controller.handle(
        UpdateShotNameRequestModel(
            project_id=body.project_id,
            shot_id=body.shot_id,
            new_name=body.new_name,
            project_code=(body.project_code or "").strip(),
        )
    )
    if result.error is not None:
        return JSONResponse({"error": result.error}, status_code=400)
    assert result.message is not None
    return JSONResponse({"ok": True, "message": result.message})
