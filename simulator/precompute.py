from typing import List, Dict, Tuple
from .feasibility import job_can_run_on

def precompute_allowed(jobs, res) -> Dict[int, List[int]]:
    allowed = {}
    for j, job in enumerate(jobs):
        allowed[j] = [r.res_id for r in res if job_can_run_on(job, r)]
    return allowed

def find_trivial_jobs(jobs, resources, allowed, dominance_ratio: float = 0.0) -> Tuple[Dict[int, int], List[int]]:
    fixed = {}
    hard = []
    
    for j, job in enumerate(jobs):
        feasibility = allowed[j]
        if not feasibility:
            hard.append(j)
            continue
        if len(feasibility) == 1:
            fixed[j] = feasibility[0]
            continue

        runtime = getattr(job, "runtime_profiler", {})
        pairs = [(r, runtime.get(resources[r].res_type, float('inf'))) for r in feasibility]
        pairs = [(r, t) for r,t in pairs if t < float('inf')]
        if len(pairs) >= 2:
            best_r, best_t = min(pairs, key=lambda x: x[1])
            second_t = sorted([t for _, t in pairs])[1]
            if best_t <= dominance_ratio * second_t:
                fixed[j] = best_r
                continue
        hard.append(j)
    return fixed, hard