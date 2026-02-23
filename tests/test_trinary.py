"""Tests for trinary logic system."""
import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'blackroad-math', 'src'))

try:
    from trinary import Trinary, BeliefState
    HAS_TRINARY = True
except ImportError:
    HAS_TRINARY = False

@pytest.mark.skipif(not HAS_TRINARY, reason="trinary module not in path")
class TestTrinary:
    def test_values(self):
        assert Trinary(1).v == 1
        assert Trinary(-1).v == -1
        assert Trinary(0).v == 0

    def test_and(self):
        assert (Trinary(1) & Trinary(-1)).v == -1
        assert (Trinary(1) & Trinary(1)).v == 1
        assert (Trinary(0) & Trinary(1)).v == 0

    def test_or(self):
        assert (Trinary(1) | Trinary(-1)).v == 1
        assert (Trinary(-1) | Trinary(-1)).v == -1

    def test_not(self):
        assert (~Trinary(1)).v == -1
        assert (~Trinary(-1)).v == 1
        assert (~Trinary(0)).v == 0

    def test_confidence(self):
        assert Trinary(1).confidence() == 1.0
        assert Trinary(0).confidence() == 0.0
        assert Trinary(-1).confidence() == 1.0

    def test_from_probability(self):
        t = Trinary.from_probability(1.0)
        assert t.v == 1.0
        t = Trinary.from_probability(0.0)
        assert t.v == -1.0
        t = Trinary.from_probability(0.5)
        assert t.v == 0.0


@pytest.mark.skipif(not HAS_TRINARY, reason="trinary module not in path")
class TestBeliefState:
    def test_assert_true(self):
        b = BeliefState()
        b.assert_true("sky_is_blue")
        assert b.evaluate("sky_is_blue").v == 1.0

    def test_quarantine(self):
        b = BeliefState()
        b.assert_true("claim_a")
        b.quarantine("claim_a")
        assert b.evaluate("claim_a").v == 0
        assert "claim_a" in b._quarantined

    def test_unknown_default(self):
        b = BeliefState()
        result = b.evaluate("nonexistent_claim")
        assert result.v == 0  # Unknown
