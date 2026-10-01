# M - Domain-Independent Recursive Core

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
