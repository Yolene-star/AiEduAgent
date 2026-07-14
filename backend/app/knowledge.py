import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, HttpUrl


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CARDS_DIR = PROJECT_ROOT / "content" / "cards" / "u1"
ALIASES_FILE = PROJECT_ROOT / "content" / "aliases.yml"
GOLDEN_CASES_FILE = PROJECT_ROOT / "evals" / "stage4_golden_cases.json"

ContentStatus = Literal[
    "draft",
    "source_verified",
    "model_checked",
    "peer_reviewed",
    "demo_published",
]


class KnowledgeSource(BaseModel):
    title: str = Field(min_length=1)
    url: HttpUrl
    license: str = Field(min_length=1)


class ReviewRecord(BaseModel):
    evidence_audit: str = Field(min_length=1)
    rebuttal_audit: str = Field(min_length=1)
    reviewed_at: str = Field(min_length=1)


class KnowledgeCard(BaseModel):
    id: str = Field(pattern=r"^U1-C\d{2}$")
    title: str = Field(min_length=1)
    version: int = Field(ge=1)
    status: ContentStatus
    prerequisites: list[str]
    aliases: list[str] = Field(min_length=1)
    keywords: list[str] = Field(min_length=1)
    canonical_claims: list[str] = Field(min_length=1)
    misconceptions: list[str] = Field(min_length=1)
    sources: list[KnowledgeSource] = Field(min_length=1)
    review: ReviewRecord


class GoldenCase(BaseModel):
    id: str
    question: str
    expected_card_ids: list[str]


def _load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


@lru_cache
def load_cards() -> dict[str, KnowledgeCard]:
    cards: dict[str, KnowledgeCard] = {}
    for path in sorted(CARDS_DIR.glob("*.yaml")):
        card = KnowledgeCard.model_validate(_load_yaml(path))
        if card.id in cards:
            raise ValueError(f"Duplicate knowledge card id: {card.id}")
        cards[card.id] = card

    expected_ids = {f"U1-C0{index}" for index in range(1, 6)}
    if set(cards) != expected_ids:
        raise ValueError(f"Expected U1 cards {sorted(expected_ids)}, got {sorted(cards)}")

    for card in cards.values():
        for prerequisite in card.prerequisites:
            if prerequisite not in cards:
                raise ValueError(f"{card.id} references missing prerequisite {prerequisite}")

    return cards


@lru_cache
def load_aliases() -> dict[str, str]:
    aliases = _load_yaml(ALIASES_FILE)
    cards = load_cards()
    if not isinstance(aliases, dict):
        raise ValueError("aliases.yml must be a mapping")

    result: dict[str, str] = {}
    for alias, card_id in aliases.items():
        if card_id not in cards:
            raise ValueError(f"Alias {alias} points to missing card {card_id}")
        result[str(alias)] = str(card_id)
    return result


@lru_cache
def load_golden_cases() -> list[GoldenCase]:
    with GOLDEN_CASES_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)
    cases = [GoldenCase.model_validate(item) for item in data]
    cards = load_cards()
    for case in cases:
        for card_id in case.expected_card_ids:
            if card_id not in cards:
                raise ValueError(f"Golden case {case.id} references missing card {card_id}")
    return cases


def validate_knowledge_base() -> None:
    load_cards()
    load_aliases()
    load_golden_cases()


def retrieve_cards(message: str, *, limit: int = 3) -> list[KnowledgeCard]:
    text = message.lower()
    cards = load_cards()
    scores: dict[str, int] = {card_id: 0 for card_id in cards}

    for alias, card_id in load_aliases().items():
        if alias.lower() in text:
            scores[card_id] += 6

    for card_id, card in cards.items():
        if card_id.lower() in text or card.title.lower() in text:
            scores[card_id] += 8
        for keyword in card.keywords:
            if keyword.lower() in text:
                scores[card_id] += 3
        for alias in card.aliases:
            if alias.lower() in text:
                scores[card_id] += 4

    ranked_ids = [
        card_id
        for card_id, score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        if score > 0
    ]
    return [cards[card_id] for card_id in ranked_ids[:limit]]


def filter_existing_card_ids(card_ids: list[str]) -> list[str]:
    cards = load_cards()
    seen: set[str] = set()
    result: list[str] = []
    for card_id in card_ids:
        if card_id in cards and card_id not in seen:
            seen.add(card_id)
            result.append(card_id)
    return result


def sources_for_card_ids(card_ids: list[str]) -> list[dict[str, str]]:
    cards = load_cards()
    sources: list[dict[str, str]] = []
    seen_urls: set[str] = set()
    for card_id in filter_existing_card_ids(card_ids):
        for source in cards[card_id].sources:
            url = str(source.url)
            if url in seen_urls:
                continue
            seen_urls.add(url)
            sources.append(
                {
                    "card_id": card_id,
                    "title": source.title,
                    "url": url,
                }
            )
    return sources
