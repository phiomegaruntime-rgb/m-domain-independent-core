"""Sequential, isolated-process comparison; no simultaneous benchmark jobs."""
import json
from pathlib import Path
import statistics
import subprocess
import sys
import torch
from pooling import load_pooling

ROOT = Path(__file__).resolve().parent
shapes = [(4,512,384),(8,2048,768),(16,4096,1024)]
runs=[]
for shape in shapes:
    for repeat in range(3):
        order = ['original','patched'] if repeat%2==0 else ['patched','original']
        for variant in order:
            command=[sys.executable,str(ROOT/'benchmark.py'),variant,
                     '--batch',str(shape[0]),'--seq',str(shape[1]),'--hidden',str(shape[2])]
            completed=subprocess.run(command,capture_output=True,text=True,check=True,cwd=ROOT)
            payloads=[line for line in completed.stdout.splitlines() if line.startswith('{"variant":')]
            assert len(payloads)==1
            row=json.loads(payloads[0]); row['repeat']=repeat
            row['profiler_stdout_logs']='\n'.join(line for line in completed.stdout.splitlines() if line != payloads[0])
            row['stderr']=completed.stderr
            runs.append(row)
summary=[]
for shape in shapes:
    groups={v:[r for r in runs if r['shape']==list(shape) and r['variant']==v]
            for v in ['original','patched']}
    med={v:statistics.median(r['median_seconds'] for r in rows) for v,rows in groups.items()}
    memory={v:statistics.median(r['peak_growth_first_call_bytes'] for r in rows) for v,rows in groups.items()}
    torch.manual_seed(20261019); torch.set_num_threads(1)
    h=torch.randn(*shape); mask=(torch.rand(shape[0],shape[1])>.2).long()
    with torch.inference_mode():
        a=load_pooling('original')(h,mask); b=load_pooling('patched')(h,mask)
    torch.testing.assert_close(a,b,rtol=2e-5,atol=1e-6)
    summary.append({'shape':shape,'median_seconds':med,
                    'median_component_speedup':med['original']/med['patched'],
                    'median_first_call_peak_growth_bytes':memory,
                    'max_absolute_output_difference':float((a-b).abs().max()),
                    'rtol':2e-5,'atol':1e-6})
result={'source_commit':'b80a0292fee27c25da7fd606776a5e24cdac3aac',
        'protocol':'CPU float32, one torch thread, seed20261019, 3 independent processes per variant per shape, 9 timed calls per process, alternate order',
        'summary':summary,'runs':runs,
        'limits':['Pooling component only; no model forward/server or GPU benchmark',
                  'Floating point reduction order changes; no bitwise-equivalence claim',
                  'No production quality/cost/energy guarantee',
                  'Process high-water RSS includes allocator and runtime effects; inspect profiler allocations separately']}
(ROOT/'comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'summary':summary},indent=2))
