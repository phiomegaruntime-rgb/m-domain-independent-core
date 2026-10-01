from m_core import (
    Fragment,
    Candidate,
    MEngine,
    audit,
)


# IMPORTANT:
# This is deliberately NOT named test_generator.
# Pytest treats test_* generator functions as tests.

def candidate_generator(fragment, direction):

    if fragment.content == "F":

        yield Candidate(
            content={
                "stable": "A",
                "relation": ("L", "R"),
            }
        )

        yield Candidate(
            content={
                "stable": "A",
                "relation": ("R", "L"),
            }
        )


def test_internal_residual_reopen():

    engine = MEngine(
        generator=candidate_generator
    )

    result = engine.run(
        Fragment("F"),
        execution_budget=10,
    )

    assert len(
        result["reopened"]
    ) == 1

    assert len(
        result["frozen"]
    ) == 0

    assert len(
        result["unresolved"]
    ) >= 1

    delta = result[
        "reopened"
    ][0].residual

    assert delta.common == {
        "stable": "A"
    }

    assert len(
        delta.distinguishing
    ) == 2

    report = audit(
        engine
    )

    assert report[
        "externally_supplied_reopen_block"
    ] is False

    assert report[
        "internal_residual_derivation"
    ] is True

    assert report[
        "unproductive_reopen_wrapping"
    ] is False


def test_zero_candidates_stays_open_unresolved():

    def empty_generator(
        fragment,
        direction,
    ):
        return ()

    engine = MEngine(
        empty_generator
    )

    result = engine.run(
        Fragment("F")
    )

    assert len(
        result["frozen"]
    ) == 0

    assert len(
        result["reopened"]
    ) == 0

    assert len(
        result["unresolved"]
    ) == 1

    assert result[
        "status"
    ] == "QUIESCENT"


def test_single_candidate_freezes():

    def single_generator(
        fragment,
        direction,
    ):
        yield Candidate(
            content="only"
        )

    engine = MEngine(
        single_generator
    )

    result = engine.run(
        Fragment("F")
    )

    assert len(
        result["frozen"]
    ) == 1

    assert len(
        result["reopened"]
    ) == 0

    assert len(
        result["unresolved"]
    ) == 0


def test_duplicate_candidates_do_not_fake_ambiguity():

    def duplicate_generator(
        fragment,
        direction,
    ):
        yield Candidate(
            content="same"
        )

        yield Candidate(
            content="same"
        )

    engine = MEngine(
        duplicate_generator
    )

    result = engine.run(
        Fragment("F")
    )

    assert len(
        result["frozen"]
    ) == 1

    assert len(
        result["reopened"]
    ) == 0


def test_common_structure_is_removed_from_delta():

    def generator(
        fragment,
        direction,
    ):

        if fragment.content == "F":

            yield Candidate(
                content={
                    "shared": "X",
                    "difference": "A",
                }
            )

            yield Candidate(
                content={
                    "shared": "X",
                    "difference": "B",
                }
            )

    engine = MEngine(
        generator
    )

    result = engine.run(
        Fragment("F"),
        execution_budget=1,
    )

    assert len(
        result["reopened"]
    ) == 1

    delta = result[
        "reopened"
    ][0].residual

    assert delta.common == {
        "shared": "X"
    }

    assert delta.distinguishing == (
        {"difference": "A"},
        {"difference": "B"},
    )
