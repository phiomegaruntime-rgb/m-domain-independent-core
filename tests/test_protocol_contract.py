
from m_core import (
    Fragment,
    Candidate,
    MEngine,
)

from m_recursive_protocol import (
    RecursiveSubstrateEngine,
    VerdictEvidence,
    SaturationVerdict,
)


def values(substrate):
    return [
        f.content
        for f
        in substrate
    ]


def test_primitive_core_remains_available():

    assert MEngine is not None

    assert (
        RecursiveSubstrateEngine
        is not None
    )


def test_derived_information_becomes_substrate_information():

    def generator(
        substrate,
        source,
        direction,
    ):

        known = values(
            substrate
        )

        if (
            source.content == "A"
            and "B" not in known
        ):
            yield Candidate("B")

        if (
            source.content == "B"
            and "A" in known
            and "C" not in known
        ):
            yield Candidate("C")

    engine = RecursiveSubstrateEngine(
        generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run()

    known = set(
        values(
            result["substrate"]
        )
    )

    assert {
        "A",
        "B",
        "C",
    }.issubset(
        known
    )


def test_multiple_reinsertions_are_supported():

    def generator(
        substrate,
        source,
        direction,
    ):

        known = values(
            substrate
        )

        chain = {
            "A": "B",
            "B": "C",
            "C": "D",
            "D": "E",
        }

        if source.content in chain:

            nxt = chain[
                source.content
            ]

            if nxt not in known:

                yield Candidate(
                    nxt
                )

    engine = RecursiveSubstrateEngine(
        generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run()

    known = set(
        values(
            result["substrate"]
        )
    )

    assert {
        "A",
        "B",
        "C",
        "D",
        "E",
    }.issubset(
        known
    )

    assert result["generations"] >= 5


def test_global_context_unlocks_later_relation():

    def generator(
        substrate,
        source,
        direction,
    ):

        known = values(
            substrate
        )

        if (
            source.content == "A"
            and "B" in known
            and "C" not in known
        ):
            yield Candidate("C")

        if (
            source.content == "C"
            and "B" in known
            and "D" not in known
        ):
            yield Candidate("D")

    engine = RecursiveSubstrateEngine(
        generator
    )

    engine.populate([
        Fragment("A"),
        Fragment("B"),
    ])

    result = engine.run()

    known = values(
        result["substrate"]
    )

    assert "C" in known
    assert "D" in known


def test_budget_is_operational_not_epistemic():

    def generator(
        substrate,
        source,
        direction,
    ):

        known = values(
            substrate
        )

        if (
            source.content == "A"
            and "B" not in known
        ):
            yield Candidate("B")

        if (
            source.content == "B"
            and "C" not in known
        ):
            yield Candidate("C")

    engine = RecursiveSubstrateEngine(
        generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run(
        execution_budget=1
    )

    assert result["status"] == "OPEN"

    assert result["fixed_point"] is False


def test_saturation_without_evidence_is_not_unresolved():

    def generator(
        substrate,
        source,
        direction,
    ):
        return ()

    engine = RecursiveSubstrateEngine(
        generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run()

    assert (
        result["verdict"]
        is SaturationVerdict.SATURATED
    )


def test_unresolved_requires_distinct_alternatives():

    def generator(
        substrate,
        source,
        direction,
    ):
        return ()

    engine = RecursiveSubstrateEngine(
        generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run(
        evidence=VerdictEvidence(
            alternatives=(
                "LEFT",
                "RIGHT",
            )
        )
    )

    assert (
        result["verdict"]
        is SaturationVerdict.OPEN_UNRESOLVED
    )


def test_duplicate_alternatives_do_not_create_false_ambiguity():

    def generator(
        substrate,
        source,
        direction,
    ):
        return ()

    engine = RecursiveSubstrateEngine(
        generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run(
        evidence=VerdictEvidence(
            alternatives=(
                "LEFT",
                "LEFT",
            )
        )
    )

    assert (
        result["verdict"]
        is SaturationVerdict.SATURATED
    )
