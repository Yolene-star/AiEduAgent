import json
from functools import lru_cache
from pathlib import Path

from backend.app.knowledge import PROJECT_ROOT, filter_existing_card_ids
from backend.app.schemas import AnimationSpec, StorybookSpec


MULTIMODAL_DIR = PROJECT_ROOT / "content" / "multimodal"
ANIMATION_FILE = MULTIMODAL_DIR / "animation_u1_image_classification.json"
STORYBOOK_FILE = MULTIMODAL_DIR / "storybook_u1_lower_primary.json"


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@lru_cache
def load_animation_spec() -> AnimationSpec:
    spec = AnimationSpec.model_validate(_load_json(ANIMATION_FILE))
    if spec.concept_id not in filter_existing_card_ids([spec.concept_id]):
        raise ValueError(f"Animation references missing concept {spec.concept_id}")
    expected_visuals = ["image-card", "pixel-grid", "feature-lines", "score-bars", "label-badge"]
    actual_visuals = [step.visual for step in spec.steps]
    if actual_visuals != expected_visuals:
        raise ValueError("Animation steps must use the approved image classification sequence")
    return spec


@lru_cache
def load_storybook_spec() -> StorybookSpec:
    spec = StorybookSpec.model_validate(_load_json(STORYBOOK_FILE))
    if spec.concept_id not in filter_existing_card_ids([spec.concept_id]):
        raise ValueError(f"Storybook references missing concept {spec.concept_id}")
    expected_pages = list(range(1, 7))
    actual_pages = [page.page for page in spec.pages]
    if actual_pages != expected_pages:
        raise ValueError("Storybook pages must be numbered 1 through 6")
    for page in spec.pages:
        if not page.image.startswith("/assets/storybook/") or not page.image.endswith(".svg"):
            raise ValueError(f"Storybook page {page.page} uses an unapproved image path")
    return spec


def validate_multimodal_assets() -> None:
    load_animation_spec()
    load_storybook_spec()
