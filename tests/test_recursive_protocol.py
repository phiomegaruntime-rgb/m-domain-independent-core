
from m_core import Fragment, Candidate

from m_recursive_protocol import (
    RecursiveSubstrateEngine,
)


def contents(substrate):
    return [
        fragment.content
        for fragment
        in substrate
    ]


def staged_generator(
    substrate,
    source,
    direction,
):

    known = contents(
        substrate
    )

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

    if (
        source.content == "C"
        and "RESULT" not in known
    ):
        yield Candidate("RESULT")
        return


def test_information_is_reinserted_recursively():

    engine = RecursiveSubstrateEngine(
        staged_generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run()

    known = contents(
        result["substrate"]
    )

    assert "A" in known
    assert "B" in known
    assert "C" in known
    assert "RESULT" in known

    assert result["fixed_point"] is True

    # B, C, RESULT, then zero-novelty confirmation.
    assert result["generations"] >= 4


def test_budget_does_not_fake_unresolved():

    engine = RecursiveSubstrateEngine(
        staged_generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run(
        execution_budget=1
    )

    assert result["status"] == "OPEN"
    assert result["fixed_point"] is False

    known = contents(
        result["substrate"]
    )

    assert "B" in known
    assert "RESULT" not in known


def test_fixed_point_without_evidence_is_saturated():

    def empty_generator(
        substrate,
        source,
        direction,
    ):
        return ()

    engine = RecursiveSubstrateEngine(
        empty_generator
    )

    engine.populate([
        Fragment("A")
    ])

    result = engine.run()

    assert result["status"] == "SATURATED"
    assert result["fixed_point"] is True
    assert result["steps"][-1].new_information == 0


def test_new_information_relates_again_to_whole_substrate():

    def generator(
        substrate,
        source,
        direction,
    ):

        known = contents(
            substrate
        )

        if (
            source.content == "X"
            and "Y" in known
            and "Z" not in known
        ):
            yield Candidate("Z")

        if (
            source.content == "Z"
            and "Y" in known
            and "W" not in known
        ):
            yield Candidate("W")

    engine = RecursiveSubstrateEngine(
        generator
    )

    engine.populate([
        Fragment("X"),
        Fragment("Y"),
    ])

    result = engine.run()

    known = contents(
        result["substrate"]
    )

    assert "Z" in known
    assert "W" in known
    assert result["fixed_point"] is True
