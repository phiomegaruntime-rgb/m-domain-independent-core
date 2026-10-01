"""
M — DOMAIN-INDEPENDENT RECURSIVE CORE
=====================================

Core:
    M = (F <-> F)^infinity

Purpose:
    Prevent false closure AND derive the next unresolved frontier
    from the distinguishable residue of the failed closure itself.

NO domain-specific physics.
NO Burgers.
NO time.
NO fitted parameters.
NO random choice.
NO arbitrary perturbation.
NO artificial depth limit.
NO externally manufactured Block.

Central rule:

    candidate closures
          |
          v
       compare
          |
          v
    common / different
          |
          v
    subtraction test
          |
          v
    exact residual Delta
          |
          v
       REOPEN
          |
          v
      F_next = Delta
          |
      direct / inverse
          |
          v
          M

If no informative residual can be derived, M stops that branch as
OPEN_UNRESOLVED rather than manufacturing apparent progress.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
import hashlib
import json


# ============================================================
# 0. STATES
# ============================================================

class Direction(Enum):
    DIRECT = auto()
    INVERSE = auto()


class Status(Enum):
    OPEN = auto()
    FROZEN = auto()
    REOPEN = auto()
    OPEN_UNRESOLVED = auto()


# ============================================================
# 1. CANONICAL STRUCTURE
# ============================================================

def canonical(x: Any) -> Any:

    if isinstance(x, Fragment):
        return {
            "content": canonical(x.content),
            "context": canonical(x.context),
        }

    if isinstance(x, Candidate):
        return {
            "content": canonical(x.content),
            "evidence": canonical(x.evidence),
        }

    if isinstance(x, Residual):
        return {
            "common": canonical(x.common),
            "distinguishing": canonical(x.distinguishing),
            "source_candidates": canonical(x.source_candidates),
        }

    if isinstance(x, dict):
        return {
            str(k): canonical(v)
            for k, v in sorted(
                x.items(),
                key=lambda item: str(item[0])
            )
        }

    if isinstance(x, (tuple, list)):
        return [canonical(v) for v in x]

    if isinstance(x, set):
        vals = [canonical(v) for v in x]
        return sorted(
            vals,
            key=lambda v: json.dumps(
                v,
                sort_keys=True,
                default=str
            )
        )

    if isinstance(x, Enum):
        return x.name

    if isinstance(x, (str, int, float, bool, type(None))):
        return x

    return repr(x)


def digest(x: Any) -> str:

    raw = json.dumps(
        canonical(x),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")

    return hashlib.sha256(raw).hexdigest()


def equal(a: Any, b: Any) -> bool:
    return canonical(a) == canonical(b)


# ============================================================
# 2. FRAGMENT
# ============================================================

@dataclass(frozen=True)
class Fragment:
    """
    Currently accessible distinction.

    It is NOT assumed to be isolated, complete or sufficient.
    """

    content: Any
    context: Tuple[Any, ...] = ()

    @property
    def identity(self) -> str:
        return digest(self)


# ============================================================
# 3. CANDIDATE
# ============================================================

@dataclass(frozen=True)
class Candidate:
    """
    One surviving continuation / closure candidate.

    The engine does not prefer one candidate over another.
    """

    content: Any
    evidence: Tuple[Any, ...] = ()

    @property
    def identity(self) -> str:
        return digest(self)


# ============================================================
# 4. RESIDUAL
# ============================================================

@dataclass(frozen=True)
class Residual:
    """
    Delta generated internally by comparison of surviving candidates.

    common:
        structure shared by all candidates.

    distinguishing:
        exact structure preventing collapse into one closure.

    source_candidates:
        identities of candidates from which Delta was derived.
    """

    common: Any
    distinguishing: Any
    source_candidates: Tuple[str, ...]

    @property
    def identity(self) -> str:
        return digest(self)

    def as_fragment(self) -> Fragment:
        return Fragment(
            content=self.distinguishing,
            context=(
                ("common", self.common),
                ("derived_from", self.source_candidates),
            ),
        )


# ============================================================
# 5. RESULT TYPES
# ============================================================

@dataclass(frozen=True)
class Frozen:
    source: Fragment
    result: Candidate
    direction: Direction
    generation: int
    evidence: Tuple[Any, ...] = ()


@dataclass(frozen=True)
class Reopen:
    source: Fragment
    residual: Residual
    direction: Direction
    generation: int


@dataclass(frozen=True)
class OpenUnresolved:
    """
    Closure is insufficient but no further informative distinction
    is derivable from currently accessible information.
    """

    source: Fragment
    candidates: Tuple[Candidate, ...]
    direction: Direction
    generation: int
    reason: str


# ============================================================
# 6. FRONTIER NODE
# ============================================================

@dataclass
class Node:
    fragment: Fragment
    direction: Direction
    generation: int = 0
    parent: Optional[str] = None
    status: Status = Status.OPEN
    children: List["Node"] = field(default_factory=list)

    @property
    def identity(self) -> str:
        return digest({
            "fragment": self.fragment.identity,
            "direction": self.direction.name,
            "generation": self.generation,
            "parent": self.parent,
        })


# ============================================================
# 7. EXTERNAL CANDIDATE SOURCE
# ============================================================

CandidateGenerator = Callable[
    [Fragment, Direction],
    Iterable[Candidate]
]


# ============================================================
# 8. STRUCTURAL DECOMPOSITION
# ============================================================

def mapping_view(x: Any) -> Optional[Dict[Any, Any]]:
    """
    Structural key/value representation when available.
    """

    if isinstance(x, dict):
        return dict(x)

    if isinstance(x, (tuple, list)):
        return {
            i: value
            for i, value in enumerate(x)
        }

    return None


# ============================================================
# 9. COMMON STRUCTURE
# ============================================================

def common_structure(values: Sequence[Any]) -> Any:
    """
    Extract only structure identical in every candidate.

    No interpolation.
    No averaging.
    No guessed midpoint.
    """

    if not values:
        return None

    first = values[0]

    if all(equal(first, x) for x in values[1:]):
        return first

    views = [
        mapping_view(x)
        for x in values
    ]

    if all(v is not None for v in views):

        keys = set(views[0].keys())

        for view in views[1:]:
            keys &= set(view.keys())

        result = {}

        for key in sorted(keys, key=str):

            subvalues = [
                view[key]
                for view in views
            ]

            common = common_structure(
                subvalues
            )

            if common is not None:
                result[key] = common

        return result if result else None

    return None


# ============================================================
# 10. STRUCTURAL SUBTRACTION
# ============================================================

def subtract_common(value: Any, common: Any) -> Any:
    """
    Remove only structure demonstrated to be common.

    This is structural subtraction, not arbitrary numerical
    subtraction.
    """

    if common is None:
        return value

    if equal(value, common):
        return None

    value_view = mapping_view(value)
    common_view = mapping_view(common)

    if value_view is not None and common_view is not None:

        residue = {}

        for key in sorted(
            set(value_view.keys()),
            key=str
        ):

            if key not in common_view:
                residue[key] = value_view[key]
                continue

            sub = subtract_common(
                value_view[key],
                common_view[key],
            )

            if sub is not None:
                residue[key] = sub

        return residue if residue else None

    return value


# ============================================================
# 11. DERIVE DELTA INTERNALLY
# ============================================================

def derive_residual(
    candidates: Sequence[Candidate],
) -> Optional[Residual]:
    """
    Delta is derived from surviving candidates themselves.
    """

    unique = {}

    for candidate in candidates:
        unique[candidate.identity] = candidate

    candidates = tuple(unique.values())

    if len(candidates) <= 1:
        return None

    contents = tuple(
        c.content
        for c in candidates
    )

    common = common_structure(
        contents
    )

    residues = tuple(
        subtract_common(
            content,
            common,
        )
        for content in contents
    )

    distinct = []

    for residue in residues:

        if not any(
            equal(residue, previous)
            for previous in distinct
        ):
            distinct.append(residue)

    if len(distinct) <= 1:
        return None

    return Residual(
        common=common,
        distinguishing=tuple(distinct),
        source_candidates=tuple(
            c.identity
            for c in candidates
        ),
    )


# ============================================================
# 12. INVERSION
# ============================================================

def invert_structure(x: Any) -> Any:
    """
    Pure structural inversion.

    Inversion is not numerical negation.
    """

    if isinstance(x, tuple):
        return tuple(
            invert_structure(v)
            for v in reversed(x)
        )

    if isinstance(x, list):
        return [
            invert_structure(v)
            for v in reversed(x)
        ]

    if isinstance(x, dict):
        return {
            k: invert_structure(v)
            for k, v in x.items()
        }

    return x


def inverse_fragment(
    fragment: Fragment
) -> Fragment:

    return Fragment(
        content=invert_structure(
            fragment.content
        ),
        context=fragment.context + (
            ("inverted_from", fragment.identity),
        ),
    )


def inversion_changes(
    fragment: Fragment
) -> bool:

    inverted = inverse_fragment(
        fragment
    )

    return not equal(
        fragment.content,
        inverted.content,
    )


# ============================================================
# 13. M ENGINE
# ============================================================

class MEngine:
    """
    M:

        1. receives surviving continuations;
        2. refuses unjustified selection;
        3. derives Delta from their difference;
        4. makes Delta the next frontier.
    """

    def __init__(
        self,
        generator: CandidateGenerator,
    ):
        self.generator = generator
        self.frontier: List[Node] = []
        self.frozen: List[Frozen] = []
        self.reopened: List[Reopen] = []
        self.unresolved: List[OpenUnresolved] = []
        self.visited = set()

    def start(
        self,
        fragment: Fragment,
    ) -> Node:

        root = Node(
            fragment=fragment,
            direction=Direction.DIRECT,
            generation=0,
        )

        self.frontier.append(root)

        return root

    def candidates_for(
        self,
        node: Node,
    ) -> Tuple[Candidate, ...]:

        generated = tuple(
            self.generator(
                node.fragment,
                node.direction,
            )
        )

        unique = {}

        for candidate in generated:

            if not isinstance(
                candidate,
                Candidate
            ):
                raise TypeError(
                    "Generator must yield Candidate objects."
                )

            unique[
                candidate.identity
            ] = candidate

        return tuple(
            unique.values()
        )

    def process(
        self,
        node: Node,
    ) -> Tuple[Node, ...]:

        attempt = (
            node.fragment.identity,
            node.direction,
        )

        # Exact recurrence without new information.
        if attempt in self.visited:

            node.status = Status.OPEN_UNRESOLVED

            self.unresolved.append(
                OpenUnresolved(
                    source=node.fragment,
                    candidates=(),
                    direction=node.direction,
                    generation=node.generation,
                    reason=(
                        "Exact fragment/direction recurrence "
                        "without new information."
                    ),
                )
            )

            return ()

        self.visited.add(
            attempt
        )

        candidates = self.candidates_for(
            node
        )

        # No derivable continuation.
        if len(candidates) == 0:

            node.status = Status.OPEN_UNRESOLVED

            self.unresolved.append(
                OpenUnresolved(
                    source=node.fragment,
                    candidates=(),
                    direction=node.direction,
                    generation=node.generation,
                    reason=(
                        "No continuation is derivable from "
                        "the accessible information."
                    ),
                )
            )

            return ()

        # Exactly one surviving continuation.
        if len(candidates) == 1:

            frozen = Frozen(
                source=node.fragment,
                result=candidates[0],
                direction=node.direction,
                generation=node.generation,
                evidence=(
                    "single_surviving_candidate",
                ),
            )

            node.status = Status.FROZEN

            self.frozen.append(
                frozen
            )

            return ()

        # Multiple candidates: derive Delta.
        residual = derive_residual(
            candidates
        )

        if residual is None:

            node.status = Status.OPEN_UNRESOLVED

            self.unresolved.append(
                OpenUnresolved(
                    source=node.fragment,
                    candidates=candidates,
                    direction=node.direction,
                    generation=node.generation,
                    reason=(
                        "Multiple continuations survive, "
                        "but structural subtraction cannot "
                        "derive a new informative distinction."
                    ),
                )
            )

            return ()

        reopen = Reopen(
            source=node.fragment,
            residual=residual,
            direction=node.direction,
            generation=node.generation,
        )

        node.status = Status.REOPEN

        self.reopened.append(
            reopen
        )

        next_fragment = residual.as_fragment()

        direct = Node(
            fragment=next_fragment,
            direction=Direction.DIRECT,
            generation=node.generation + 1,
            parent=node.identity,
        )

        children = [
            direct
        ]

        if inversion_changes(
            next_fragment
        ):

            inverse = Node(
                fragment=inverse_fragment(
                    next_fragment
                ),
                direction=Direction.INVERSE,
                generation=node.generation + 1,
                parent=node.identity,
            )

            children.append(
                inverse
            )

        node.children.extend(
            children
        )

        return tuple(
            children
        )

    def advance(self) -> Dict[str, int]:

        current = tuple(
            self.frontier
        )

        self.frontier = []

        for node in current:

            self.frontier.extend(
                self.process(node)
            )

        return {
            "processed": len(current),
            "frontier": len(self.frontier),
            "frozen": len(self.frozen),
            "reopened": len(self.reopened),
            "unresolved": len(self.unresolved),
        }

    def run(
        self,
        fragment: Fragment,
        execution_budget: Optional[int] = None,
    ) -> Dict[str, Any]:

        root = self.start(
            fragment
        )

        generations = 0

        while self.frontier:

            if (
                execution_budget is not None
                and generations >= execution_budget
            ):
                break

            self.advance()

            generations += 1

        return {
            "root": root,
            "generations": generations,
            "frontier": tuple(self.frontier),
            "frozen": tuple(self.frozen),
            "reopened": tuple(self.reopened),
            "unresolved": tuple(self.unresolved),
            "status": (
                "OPEN"
                if self.frontier
                else "QUIESCENT"
            ),
        }


# ============================================================
# 14. AUDIT
# ============================================================

def audit(
    engine: MEngine
) -> Dict[str, Any]:

    return {
        "false_closure_selector": False,
        "externally_supplied_reopen_block": False,
        "internal_residual_derivation": True,
        "structural_subtraction": True,
        "direct_inverse_preserved": True,
        "arbitrary_perturbation": False,
        "random_selection": False,
        "post_hoc_correction": False,
        "fixed_depth_inside_M": False,
        "unproductive_reopen_wrapping": False,
        "can_remain_open": True,
        "frozen": len(engine.frozen),
        "reopened": len(engine.reopened),
        "unresolved": len(engine.unresolved),
        "frontier": len(engine.frontier),
    }
