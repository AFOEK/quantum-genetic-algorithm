from typing import List, Tuple, Dict
from concurrent.futures import ProcessPoolExecutor
from simulator.cloud_env import sim_alloc
from optimizer.repair import repair_assignment

def eval_one(args):
    assign, jobs, resources, weights = args

    fixed = repair_assignment(assign, jobs, resources)
    fit, metrics = sim_alloc(
        fixed,
        jobs,
        resources,
        w_cost=weights["w_cost"],
        w_makespan=weights["w_makespan"],
        w_sla=weights["w_sla"],
        w_penalty=weights["w_penalty"],
        w_violation=weights["w_violation"],
        w_storage=weights["w_storage"],
        w_carbon=weights["w_carbon"],
    )
    return assign, fit, metrics

def evaluate_population(
    population: List[List[int]],
    jobs,
    resources,
    weights: Dict[str, float],
    parallel: bool = True,
    max_workers: int | None = None,
) -> Tuple[List[Tuple[List[int], float, dict]], List[float], List[dict]]:
    
    scored: List[Tuple[List[int], float, dict]] = []

    if parallel and len(population) > 1:
        args_iter = ((assign, jobs, resources, weights) for assign in population)
        with ProcessPoolExecutor(max_workers=max_workers) as ex:
            for assign, fit, metrics in ex.map(eval_one, args_iter):
                scored.append((assign, fit, metrics))
    else:
        for assign in population:
            assign2, fit, metrics = eval_one((assign, jobs, resources, weights))
            scored.append((assign2, fit, metrics))

    scored.sort(key=lambda x: x[1])

    fits = [fit for _, fit, _ in scored]
    mets = [metrics for _, _, metrics in scored]
    return scored, fits, mets