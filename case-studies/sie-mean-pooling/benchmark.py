import argparse
import hashlib
import json
import resource
import statistics
import time
import torch
from pooling import load_pooling

parser = argparse.ArgumentParser()
parser.add_argument('which', choices=['original', 'patched'])
parser.add_argument('--batch', type=int, default=16)
parser.add_argument('--seq', type=int, default=4096)
parser.add_argument('--hidden', type=int, default=1024)
args = parser.parse_args()
torch.set_num_threads(1)
torch.manual_seed(20261019)
fn = load_pooling(args.which)
h = torch.randn(args.batch, args.seq, args.hidden)
mask = (torch.rand(args.batch, args.seq) > 0.2).long()
with torch.inference_mode():
    # Warm only a tiny same-rank case before the separate memory observation.
    fn(h[:1, :8, :8].contiguous(), mask[:1, :8])
    peak_before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    result = fn(h, mask)
    peak_after = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    durations = []
    for _ in range(9):
        t0 = time.perf_counter()
        result = fn(h, mask)
        durations.append(time.perf_counter()-t0)
    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU], profile_memory=True) as prof:
        result = fn(h, mask)
    allocs = [{'operation': event.key, 'self_cpu_memory_bytes': event.self_cpu_memory_usage}
              for event in prof.key_averages() if event.self_cpu_memory_usage > 0]
print(json.dumps({'variant': args.which, 'torch': torch.__version__, 'threads': 1,
    'shape': [args.batch, args.seq, args.hidden], 'dtype': 'float32',
    'seed': 20261019, 'peak_before_bytes': peak_before,
    'peak_after_first_call_bytes': peak_after,
    'peak_growth_first_call_bytes': max(0, peak_after-peak_before),
    'median_seconds': statistics.median(durations), 'durations_seconds': durations,
    'allocations': allocs,
    'output_sha256': hashlib.sha256(result.numpy().tobytes()).hexdigest()}))
