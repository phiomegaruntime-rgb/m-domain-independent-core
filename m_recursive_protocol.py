
"""
M Recursive Substrate Saturation Protocol

Primitive mechanics remain in m_core.py.

This layer implements the cumulative recursive sequence:

    POPULATE
    -> RELATE
    -> DERIVE
    -> REINSERT
    -> RECALCULATE
    -> SUBTRACT
    -> INVERSE
    -> REPEAT
    -> FIXED POINT

Central recurrence:

    K_(n+1) = K_n union Derive(K_n)

A fixed point means only that a complete global round produced
no genuinely new information.

Saturation is therefore distinct from epistemic verdict.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Iterable, Tuple

from m_core import (
    Fragment,
    Candidate,
    Direction,
    canonical,
    digest,
    derive_residual,
    inverse_fragment,
    inversion_changes,
)


RelationGenerator = Callable[
    [
        Tuple[Fragment, ...],
        Fragment,
        Direction,
    ],
    Iterable[Candidate],
]


# ============================================================
# SUBSTRATE
# ============================================================

@dataclass
class Substrate:
    """
    Cumulative accessible information K_n.
    """

    cells: dict = field(
        default_factory=dict
    )

    def insert(
        self,
        fragment: Fragment,
    ) -> bool:

        if not isinstance(
            fragment,
            Fragment,
        ):
            raise TypeError(
                "Substrate accepts Fragment objects only."
            )

        key = fragment.identity

        if key in self.cells:
            return False

        self.cells[key] = fragment
        return True

    def snapshot(
        self,
    ) -> Tuple[Fragment, ...]:

        return tuple(
            self.cells[key]
            for key in sorted(
                self.cells
            )
        )

    @property
    def identity(self) -> str:

        return digest(
            tuple(
                canonical(fragment)
                for fragment
                in self.snapshot()
            )
        )

    def __len__(self):
        return len(self.cells)


# ============================================================
# SATURATION STEP
# ============================================================

@dataclass(frozen=True)
class SaturationStep:

    generation: int
    before: str
    after: str
    inserted: Tuple[str, ...]
    new_information: int


# ============================================================
# VERDICT
# ============================================================

class SaturationVerdict(Enum):

    OPEN = auto()

    SATURATED = auto()

    FROZEN = auto()

    OPEN_UNRESOLVED = auto()


@dataclass(frozen=True)
class VerdictEvidence:
    """
    Evidence belongs to the derivation/verdict layer.

    Saturation itself is not allowed to manufacture
    FROZEN or OPEN_UNRESOLVED.
    """

    necessary: Tuple[Any, ...] = ()

    alternatives: Tuple[Any, ...] = ()


def fixed_point_verdict(
    *,
    fixed_point: bool,
    budget_exhausted: bool,
    evidence: VerdictEvidence,
) -> SaturationVerdict:

    # Operational interruption is not epistemic closure.
    if budget_exhausted and not fixed_point:

        return SaturationVerdict.OPEN

    # No terminal verdict before saturation.
    if not fixed_point:

        return SaturationVerdict.OPEN

    # Explicitly established necessary result.
    if evidence.necessary:

        return SaturationVerdict.FROZEN

    # Genuine unresolved alternatives must be distinct.
    unique_alternatives = {
        digest(
            canonical(value)
        )
        for value
        in evidence.alternatives
    }

    if len(
        unique_alternatives
    ) >= 2:

        return SaturationVerdict.OPEN_UNRESOLVED

    # Fixed point alone means saturation only.
    return SaturationVerdict.SATURATED


# ============================================================
# RECURSIVE ENGINE
# ============================================================

class RecursiveSubstrateEngine:
    """
    Cumulative recursive execution of M.

    New information is reinserted into the whole accessible
    substrate rather than being treated only as an isolated
    next frontier.
    """

    def __init__(
        self,
        relation_generator: RelationGenerator,
    ):

        self.generator = relation_generator

        self.substrate = Substrate()

        self.steps = []

        self.fixed_point = False

        self.generation = 0

    # --------------------------------------------------------
    # POPULATE
    # --------------------------------------------------------

    def populate(
        self,
        fragments,
    ):

        for fragment in fragments:

            self.substrate.insert(
                fragment
            )

    # --------------------------------------------------------
    # RELATE
    # --------------------------------------------------------

    def _candidates(
        self,
        source,
        direction,
    ):

        generated = tuple(
            self.generator(
                self.substrate.snapshot(),
                source,
                direction,
            )
        )

        unique = {}

        for candidate in generated:

            if not isinstance(
                candidate,
                Candidate,
            ):
                raise TypeError(
                    "relation_generator must yield Candidate objects"
                )

            unique[
                candidate.identity
            ] = candidate

        return tuple(
            unique.values()
        )

    # --------------------------------------------------------
    # DERIVE / SUBTRACT / INVERSE
    # --------------------------------------------------------

    def _derive_from(
        self,
        source,
        direction,
    ):

        candidates = self._candidates(
            source,
            direction,
        )

        # Local absence is NOT global unresolved.
        if not candidates:

            return ()

        # One derivable continuation is new information.
        if len(candidates) == 1:

            candidate = candidates[0]

            return (
                Fragment(
                    content=candidate.content,
                    context=source.context + (
                        (
                            "derived_from",
                            source.identity,
                        ),
                        (
                            "direction",
                            direction.name,
                        ),
                    ),
                ),
            )

        # Multiple candidates:
        # derive structural distinguishing residual.
        residual = derive_residual(
            candidates
        )

        if residual is None:

            return ()

        delta = residual.as_fragment()

        derived = [
            delta
        ]

        # Structural inverse remains accessible when distinct.
        if inversion_changes(
            delta
        ):

            derived.append(
                inverse_fragment(
                    delta
                )
            )

        return tuple(
            derived
        )

    # --------------------------------------------------------
    # COMPLETE GLOBAL ROUND
    # --------------------------------------------------------

    def cycle(self):
        """
        One complete global saturation round.

        Important:
        K_n is frozen during the round.

        All newly derived information is collected first.

        Only after the round is complete is it reinserted,
        producing K_(n+1).
        """

        before = self.substrate.identity

        snapshot = self.substrate.snapshot()

        pending = {}

        for source in snapshot:

            for direction in (
                Direction.DIRECT,
                Direction.INVERSE,
            ):

                for fragment in self._derive_from(
                    source,
                    direction,
                ):

                    if (
                        fragment.identity
                        not in self.substrate.cells
                    ):

                        pending[
                            fragment.identity
                        ] = fragment

        # ----------------------------------------------------
        # REINSERT
        # ----------------------------------------------------

        inserted = []

        for key in sorted(
            pending
        ):

            fragment = pending[key]

            if self.substrate.insert(
                fragment
            ):

                inserted.append(
                    key
                )

        after = self.substrate.identity

        step = SaturationStep(
            generation=self.generation,
            before=before,
            after=after,
            inserted=tuple(
                inserted
            ),
            new_information=len(
                inserted
            ),
        )

        self.steps.append(
            step
        )

        self.generation += 1

        # A fixed point requires an entire zero-novelty round.
        self.fixed_point = (
            len(inserted) == 0
        )

        return step

    # --------------------------------------------------------
    # REPEAT UNTIL FIXED POINT OR BUDGET
    # --------------------------------------------------------

    def run(
        self,
        execution_budget=None,
        evidence=None,
    ):

        if evidence is None:

            evidence = VerdictEvidence()

        rounds = 0

        while True:

            # Budget is operational only.
            if (
                execution_budget is not None
                and rounds >= execution_budget
            ):

                verdict = fixed_point_verdict(
                    fixed_point=False,
                    budget_exhausted=True,
                    evidence=evidence,
                )

                return {
                    "status": verdict.name,
                    "verdict": verdict,
                    "fixed_point": False,
                    "substrate":
                        self.substrate.snapshot(),
                    "steps":
                        tuple(self.steps),
                    "generations":
                        rounds,
                    "evidence":
                        evidence,
                }

            step = self.cycle()

            rounds += 1

            if (
                step.new_information
                == 0
            ):

                verdict = fixed_point_verdict(
                    fixed_point=True,
                    budget_exhausted=False,
                    evidence=evidence,
                )

                return {
                    "status": verdict.name,
                    "verdict": verdict,
                    "fixed_point": True,
                    "substrate":
                        self.substrate.snapshot(),
                    "steps":
                        tuple(self.steps),
                    "generations":
                        rounds,
                    "evidence":
                        evidence,
                }


# Compatibility name used by the previous local audit.
VerdictAwareRecursiveSubstrateEngine = RecursiveSubstrateEngine
