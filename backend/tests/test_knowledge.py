import pytest

from backend.app.knowledge import (
    filter_existing_card_ids,
    load_cards,
    load_golden_cases,
    retrieve_cards,
    sources_for_card_ids,
    validate_knowledge_base,
)


def test_knowledge_cards_validate_and_have_required_review_metadata():
    validate_knowledge_base()
    cards = load_cards()

    assert sorted(cards) == ["U1-C01", "U1-C02", "U1-C03", "U1-C04", "U1-C05"]
    for card in cards.values():
        assert card.version >= 1
        assert card.status == "model_checked"
        assert card.review.evidence_audit
        assert card.review.rebuttal_audit
        assert len(card.sources) >= 2


@pytest.mark.parametrize("case", load_golden_cases(), ids=lambda case: case.id)
def test_golden_question_retrieval(case):
    actual_card_ids = [card.id for card in retrieve_cards(case.question)]

    for expected_card_id in case.expected_card_ids:
        assert expected_card_id in actual_card_ids
    if not case.expected_card_ids:
        assert actual_card_ids == []


def test_source_mapping_only_uses_existing_card_ids():
    assert filter_existing_card_ids(["U1-C02", "BAD-CARD", "U1-C02", "U1-C04"]) == [
        "U1-C02",
        "U1-C04",
    ]

    sources = sources_for_card_ids(["BAD-CARD"])

    assert sources == []


def test_source_mapping_comes_from_cards_not_model_output():
    sources = sources_for_card_ids(["U1-C04"])

    assert sources
    assert all(source["url"].startswith("https://") for source in sources)
    assert "https://fake.example/not-allowed" not in [source["url"] for source in sources]
