# M Recursive Substrate Saturation Protocol

## 1. Primitive relation

The primitive mechanics remain:

    M = (F <-> F)^infinity

The recursive protocol does not replace this relation.

It defines how information derived through M is retained and
made available to subsequent relations.

## 2. Initial substrate

Let:

    K_0 = {F_1, F_2, ..., F_N}

contain all accessible information admitted to the execution.

Population does not itself select a solution.

## 3. Mandatory sequence

Every complete execution follows:

    POPULATE
    -> RELATE
    -> DERIVE
    -> REINSERT
    -> RECALCULATE
    -> SUBTRACT
    -> INVERSE
    -> REPEAT
    -> FIXED POINT

## 4. Recursive recurrence

Every genuinely new derivation is reinserted:

    K_(n+1)
    =
    K_n union Derive[(F <-> F)_(K_n)]

The new information is therefore available to relations with
information already present in K_n.

## 5. Local absence is not global exhaustion

A fragment that produces no continuation does not establish
that the complete substrate contains no further derivable
information.

Therefore local absence alone cannot establish:

    OPEN_UNRESOLVED

## 6. Structural subtraction

Common structure may be removed only where equivalence has
actually been established.

In particular:

    F_A = F_B

does not establish:

    (F_A <-> K_A) = (F_B <-> K_B)

Relational placement remains part of the accessible structure.

## 7. Inverse

Inverse traversal is structural rather than numerical negation.

Where inversion changes accessible structure, direct and inverse
forms remain available to subsequent recursive cycles.

## 8. Fixed point

Saturation is reached only when one complete global round adds
no genuinely new information:

    K_(n+1) = K_n

Execution-budget exhaustion is not saturation.

## 9. Saturation and verdict are different

The following equivalence is forbidden:

    FIXED POINT = OPEN_UNRESOLVED

A fixed point means only:

    no new information was derived in the completed global round

Verdicts are:

OPEN
    Execution stopped before saturation.

SATURATED
    A fixed point was reached, but no stronger epistemic verdict
    was established.

FROZEN
    A necessary result has been explicitly established.

OPEN_UNRESOLVED
    Saturation has been reached while at least two genuinely
    distinguishable alternatives remain unresolved.

## 10. Anti-false-closure rule

    INFORMATION NOT EXPLICIT
    !=
    INFORMATION ABSENT

Before information is declared unavailable, the protocol must
exhaust what is recursively derivable from the relations among
the accessible information.

## 11. Domain independence

The recursive protocol contains no domain-specific physical law.

A domain supplies:

    K_0

and the candidate relation generator.

The protocol controls only:

    retention
    relation
    derivation
    reinsertion
    recalculation
    subtraction
    inversion
    saturation
    verdict separation

## 12. Required invariants

1. No fitted selector chooses among competing candidates.
2. Derived information is reinserted into the substrate.
3. Reinserted information can relate to older information.
4. Duplicate information does not create false novelty.
5. Local absence does not establish global exhaustion.
6. Budget exhaustion does not create epistemic closure.
7. Fixed point does not automatically mean OPEN_UNRESOLVED.
8. OPEN_UNRESOLVED requires distinct surviving alternatives.
9. Necessary result and saturation remain distinct.
10. No domain-specific law is introduced by this protocol.
