from typing import List, Tuple, Dict
import numpy as np
from simulator.cloud_env import sim_alloc
from optimizer.repair import repair_assignment

def evaluate_population(population: List[List[int]],
             jobs,
             resources,
             weights: Dict[str, float]) -> Tuple[np.ndarray, List[dict]]:
    
    scored: List[Tuple[List[int], float, dict]] = []
    fits: List[float] = []
    mets: List[dict] = []

    for assign in population:
        fixed = repair_assignment(assign, jobs, resources)
        fit, metrics = sim_alloc(fixed, jobs, resources,
            w_cost=weights["w_cost"],
            w_makespan=weights["w_makespan"],
            w_sla=weights["w_sla"],
            w_penalty=weights["w_penalty"],
            w_violation=weights["w_violation"],
            w_storage=weights["w_storage"],
            w_carbon=weights["w_carbon"])
        scored.append((assign, fit, metrics))
        fits.append(fit)
        mets.append(metrics)  

    scored.sort(key=lambda x: x[1])
    return scored, np.array(fits, dtype=float), mets