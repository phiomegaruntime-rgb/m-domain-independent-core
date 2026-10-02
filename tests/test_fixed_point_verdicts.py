
from m_core import Fragment, Candidate

from m_recursive_protocol import (
    RecursiveSubstrateEngine,
    VerdictEvidence,
    SaturationVerdict,
)


def empty_generator(
    substrate,
    source,
    direction,
):
    return ()


def staged_generator(
    substrate,
    source,
    direction,
):

    known = [
        x.content
        for x
        in substrate
    ]

    if (
        source.content == "A"
        and "B" not in known
    ):
        yield Candidate("B")
        return

    if (
        source.content == "B"
        and "C" not in known
    ):
        yield Candidate("C")
        return


def test_fixed_point_alone_means_saturated():

    engine = RecursiveSubstrateEngine(
        empty_generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run()

    assert result["fixed_point"] is True

    assert (
        result["verdict"]
        is SaturationVerdict.SATURATED
    )


def test_budget_before_fixed_point_is_open():

    engine = RecursiveSubstrateEngine(
        staged_generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run(
        execution_budget=1
    )

    assert result["fixed_point"] is False

    assert (
        result["verdict"]
        is SaturationVerdict.OPEN
    )


def test_necessary_result_at_fixed_point_freezes():

    engine = RecursiveSubstrateEngine(
        empty_generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run(
        evidence=VerdictEvidence(
            necessary=("RESULT",)
        )
    )

    assert result["fixed_point"] is True

    assert (
        result["verdict"]
        is SaturationVerdict.FROZEN
    )


def test_distinct_alternatives_are_unresolved():

    engine = RecursiveSubstrateEngine(
        empty_generator
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


def test_duplicate_alternative_does_not_fake_unresolved():

    engine = RecursiveSubstrateEngine(
        empty_generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run(
        evidence=VerdictEvidence(
            alternatives=(
                "SAME",
                "SAME",
            )
        )
    )

    assert (
        result["verdict"]
        is SaturationVerdict.SATURATED
    )


def test_necessary_result_has_priority():

    engine = RecursiveSubstrateEngine(
        empty_generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run(
        evidence=VerdictEvidence(
            necessary=(
                "NECESSARY",
            ),
            alternatives=(
                "X",
                "Y",
            ),
        )
    )

    assert (
        result["verdict"]
        is SaturationVerdict.FROZEN
    )


def test_recursive_derivation_can_saturate_without_resolution():

    engine = RecursiveSubstrateEngine(
        staged_generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run()

    known = [
        x.content
        for x
        in result["substrate"]
    ]

    assert "A" in known
    assert "B" in known
    assert "C" in known

    assert result["fixed_point"] is True

    assert (
        result["verdict"]
        is SaturationVerdict.SATURATED
    )
