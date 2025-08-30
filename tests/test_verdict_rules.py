import pytest
from app.schemas import Source
from app.nlp.verdict import make_verdict

def _src(url, ev):
    return Source(title="t", url=url, snippet=None, evidence=[ev])

@pytest.mark.asyncio
async def test_true_case():
    # Simple smoke: reliant on model, so only check label is among allowed and code runs
    claim = "Paris is the capital of France."
    sources = [
        _src("https://example.com/a", "The capital of France is Paris according to official resources."),
        _src("https://example.com/b", "France's capital city is Paris."),
    ]
    label, conf, rationale, _ = make_verdict(claim, sources)
    assert label in {"True", "Misleading", "Unverified", "False"}
    assert isinstance(conf, float)
    assert isinstance(rationale, str)


@pytest.mark.asyncio
async def test_no_evidence():
    """Test handling of sources with no evidence."""
    claim = "Test claim."
    sources = [
        Source(title="Test", url="https://example.com", snippet="snippet", evidence=[]),
        Source(title="Test2", url="https://example2.com", snippet="snippet2"),  # Uses default empty list
    ]
    label, conf, rationale, cites = make_verdict(claim, sources)
    assert label == "Unverified"
    assert conf < 0.001  # Essentially zero
    assert "No strong evidence available" in rationale
    assert cites == {}


@pytest.mark.asyncio
async def test_short_evidence_filtered():
    """Test that very short evidence is filtered out."""
    claim = "Test claim for filtering."
    sources = [
        _src("https://example.com", "Short."),  # Too short, should be filtered
        _src("https://example.com", "This is a much longer piece of evidence that should be included in the analysis."),
    ]
    label, conf, rationale, _ = make_verdict(claim, sources)
    # Should process successfully even with some evidence filtered out
    assert label in {"True", "Misleading", "Unverified", "False"}
    assert isinstance(conf, float)
    assert isinstance(rationale, str)
