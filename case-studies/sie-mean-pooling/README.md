# M case study: lower-memory CPU mean pooling in SIE

**Status: independently reproducible component experiment; not adopted upstream.**

M principle and research direction: **Massimiliano Brighindi**. Implementation,
code inspection and measurements: AI-assisted. Upstream SIE adapter: Superlinked
and its contributors, Apache-2.0; see [LICENSE.upstream](LICENSE.upstream).

## Problem and proposed change

At [SIE commit b80a0292](https://github.com/superlinked/sie/blob/b80a0292fee27c25da7fd606776a5e24cdac3aac/packages/sie_server/src/sie_server/adapters/pytorch_embedding/__init__.py),
mean pooling materializes `(hidden_state * mask)` before reducing it. The output
requires the reduced result, not a stored copy of every masked hidden state.

For CPU float32 only, the candidate uses
`torch.bmm(mask.transpose(1, 2), hidden_state).squeeze(1)`. It keeps the original
denominator/clamp and disables CPU autocast locally around `bmm`. Other devices,
precisions, pooling strategies and subsequent normalization are unchanged.

## Results, including the negative result

Linux x86_64, PyTorch 2.14.1+cpu, one thread, seed 20261019. Three fresh
processes per variant and shape; alternating order; nine timed calls per process.
Numbers below are medians of process medians for **pooling only**.

| [batch, sequence, hidden] | Original | Candidate | Component speedup |
| --- | ---: | ---: | ---: |
| [4, 512, 384] | 0.137 ms | 0.203 ms | 0.67x: slower |
| [8, 2048, 768] | 19.995 ms | 3.329 ms | 6.01x |
| [16, 4096, 1024] | 114.076 ms | 17.108 ms | 6.67x |

For the largest shape, the profiler records a **256 MiB multiplication
temporary** in the original. The candidate's `bmm` allocates a **64 KiB result**.
This is not a comparison of total server memory: inputs, masks, model weights
and other allocations remain. See [raw measurements](comparison.json).

Maximum absolute output difference across the benchmark shapes: **1.304e-7**.
Twenty-five standalone tests pass with declared `rtol=2e-5, atol=1e-6` for the
changed path; untouched dtype/pooling fixtures require exact equality.
Reduction order changes: **no bitwise-equivalence claim**.

## Reproduce

Use Linux and Python 3.12 for the recorded environment. No checkpoints, external
services, accounts or credentials are required. Install PyTorch 2.14.1 CPU and
pytest 9.1.1 using your usual trusted package source, then in this directory:

```bash
python3 -m pytest -q test_pooling.py
python3 run_comparison.py
```

The second command regenerates `comparison.json`. It runs isolated subprocesses
sequentially. Runtime and allocator behavior vary by hardware and build.

The method is extracted by AST from the complete frozen source files, not
reimplemented in the benchmark. [pooling.py](pooling.py) performs the extraction.
The proposed source change is in [repair.patch](repair.patch).

## M: conceptual solution, public trace, then measurement

The conceptual question is which intermediate relations are actually necessary
to produce the requested mean. The candidate removes the materialized product,
while keeping the masked reduction and normalization relation. Inspection then
includes the candidate, the verifier and the interpretation of the timings.

Re-examining the correction exposes two important limits: small batches are
slower, and the numerical result is not bitwise identical. Both remain in the
record. No threshold was fitted afterward to hide the negative result.

The matrix primitive and numerical comparison rules are explicit engineering
knowledge supplied by the assistant. This study does not show that M's Python
core autonomously generated the patch, nor that M outperforms other engineering
methods. Reproducing the optimization tests the optimization; attributing a
general methodological advantage to M requires a separate comparison.

## What remains open

- Full SIE integration, trained-checkpoint fidelity, ranking ties and real workloads.
- GPU performance and server-wide latency, throughput, energy or financial savings.
- Upstream acceptance and an independent reproduction by another environment.
- High-condition-number inputs beyond the declared fixtures and tolerances.

The upstream `mise` workflow/full suite was not executed in this component-only
audit. Before deployment, follow SIE's contributor instructions and validate on
the target workloads. No production deployment or upstream modification is claimed.

To report a reproduction, include CPU, OS, PyTorch build, thread settings,
commands, full `comparison.json`, test output and numerical/quality observations.

## Sintesi italiana

Il caso mostra una proposta verificabile per evitare una copia temporanea durante
la media degli embedding. Nei due casi grandi provati la sola fase accelera di
circa 6–6,7 volte; nel caso piccolo rallenta. Non dimostra un server 6,7 volte
piu veloce o un risparmio economico gia misurato. Il dossier distingue metodo,
codice, misure, compromessi e verifiche ancora aperte. La versione italiana
estesa e in [README.txt](README.txt).
