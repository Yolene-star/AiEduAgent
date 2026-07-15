from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from backend.app.knowledge import PROJECT_ROOT, filter_existing_card_ids
from backend.app.schemas import CourseResourceCreate, CourseResourceResponse


RESOURCE_DRAFTS_FILE = PROJECT_ROOT / "data" / "demo" / "course_resources.jsonl"


def create_course_resource(resource: CourseResourceCreate) -> CourseResourceResponse:
    _validate_card_ids(resource.card_ids)
    response = CourseResourceResponse(
        **resource.model_dump(),
        id=f"res-{uuid4()}",
        status="draft",
        created_at=datetime.now(UTC).isoformat(),
    )
    append_course_resource(response)
    return response


def list_course_resources() -> list[CourseResourceResponse]:
    if not RESOURCE_DRAFTS_FILE.exists():
        return []

    resources: list[CourseResourceResponse] = []
    with RESOURCE_DRAFTS_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                resources.append(CourseResourceResponse.model_validate_json(line))
    return resources


def append_course_resource(resource: CourseResourceResponse) -> None:
    RESOURCE_DRAFTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with RESOURCE_DRAFTS_FILE.open("a", encoding="utf-8") as file:
        file.write(resource.model_dump_json())
        file.write("\n")


def _validate_card_ids(card_ids: list[str]) -> None:
    if filter_existing_card_ids(card_ids) != card_ids:
        raise ValueError("resource references unknown card_id")
