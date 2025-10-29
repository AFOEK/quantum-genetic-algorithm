from typing import List, Tuple
from simulator.cloud_env import sim_alloc
from simulator.job import Job
from simulator.resources import Resource

def evaluate_population(
        population: List[List[int]],
        jobs: List[Job],
        resources: List[Resource]
):
    scored: List[Tuple[List[int], float, dict]] = []
    for assign in population:
        fit, metrics = sim_alloc(assign, jobs, resources)
        scored.append((assign, fit, metrics))

    scored.sort(key=lambda x: x[1])
    return scored