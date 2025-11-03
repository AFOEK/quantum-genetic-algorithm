from typing import List, Tuple
from simulator.cloud_env import sim_alloc
from simulator.job import Job
from simulator.resources import Resource
from optimizer.repair import repair_assignment

def evaluate_population(
        population: List[List[int]],
        jobs: List[Job],
        resources: List[Resource]
):
    scored: List[Tuple[List[int], float, dict]] = []
    for assign in population:
        fixed = repair_assignment(assign, jobs, resources)
        fit, metrics = sim_alloc(fixed, jobs, resources)
        scored.append((assign, fit, metrics))

    scored.sort(key=lambda x: x[1])
    return scored