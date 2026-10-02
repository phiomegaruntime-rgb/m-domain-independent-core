# M - Domain-Independent Recursive Core

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23086326.svg)](https://doi.org/10.5281/zenodo.23086326)

Core:

    M = (F <-> F)^infinity

A domain-independent recursive core for preventing false closure and
deriving the next unresolved frontier from the distinguishable residue
of surviving continuations.

## Central rule

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

## Constraints

The core contains no:

- domain-specific physics
- Burgers-specific rule
- time assumption
- fitted parameter
- random selection
- arbitrary perturbation
- artificial recursion-depth rule inside M
- externally manufactured REOPEN block

If the available information does not generate an informative residual,
the branch remains OPEN_UNRESOLVED.

The engine does not manufacture apparent progress merely to force a
closure.

## Separation of responsibilities

CandidateGenerator is deliberately external to the abstract engine.

An abstract engine cannot invent facts about an unknown reality.

Once candidate continuations are supplied, M itself performs:

1. canonical comparison
2. common-structure extraction
3. structural subtraction
4. residual derivation
5. REOPEN
6. direct/inverse frontier generation

The residual is therefore generated internally rather than supplied as
an external Block.

## Validation

Run:

    python -m pytest -q

The repository is published only after the local validation suite passes.

## Status

Initial independent implementation.

This repository intentionally separates the domain-independent M core
from domain-specific runtime implementations and validation cases.


---

## Recursive Substrate Saturation Protocol

The primitive domain-independent core is extended by an explicit
recursive substrate execution protocol.

Required sequence:

    POPULATE
    -> RELATE
    -> DERIVE
    -> REINSERT
    -> RECALCULATE
    -> SUBTRACT
    -> INVERSE
    -> REPEAT
    -> FIXED POINT

Derived information is reinserted into the cumulative accessible
substrate:

    K_(n+1) = K_n union Derive[(F <-> F)_(K_n)]

Saturation requires a complete global round with no new information:

    K_(n+1) = K_n

Saturation and epistemic verdict are separate:

- OPEN: execution stopped before saturation.
- SATURATED: fixed point reached; no stronger verdict established.
- FROZEN: a necessary result is established.
- OPEN_UNRESOLVED: fixed point reached with genuinely distinct
  unresolved alternatives.

Therefore:

    FIXED POINT != OPEN_UNRESOLVED

and:

    INFORMATION NOT EXPLICIT != INFORMATION ABSENT

See `M_RECURSIVE_PROTOCOL.md` for the complete protocol.

The protocol remains domain-independent.

