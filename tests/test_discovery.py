from src.discovery import CandidateRecord, deduplicate_candidates


def test_deduplicate_candidates_merges_evidence():
    items = deduplicate_candidates([
        CandidateRecord(name="Cable Organizer", source_url="https://a.example", evidence=[{"claim": "a"}]),
        CandidateRecord(name="cable-organizer", source_url="https://b.example", evidence=[{"claim": "b"}]),
    ])
    assert len(items) == 1
    assert len(items[0].evidence) == 2


def test_empty_names_are_not_candidates():
    assert deduplicate_candidates([CandidateRecord(name="   ")]) == []
