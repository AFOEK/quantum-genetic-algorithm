from typing import Tuple, List, Dict, Any
from optimizer.eval_pop import evaluate_population
from quantum_backend.quantum_state import QGAState
import random

def run_qga(
        jobs,
        res,
        gen: int = 30,
        pop_size: int = 20,
        elite_k: int = 5,
        lr: float = 0.01
):
    qga = QGAState(num_jobs=len(jobs), num_res=len(res))
    best_overall: Tuple[List[int], float, Dict[str, Any]] = None
    hist: List[Dict[str, Any]] = []

    for gens in range(gen):
        pop = [qga.sample_assigment(jobs, res) for _ in range(pop_size)]
        scored = evaluate_population(pop, jobs, res)

        best_gen = scored[0]
        if best_overall is None or best_gen[1] < best_overall[1]:
            best_overall = best_gen

        hist.append({
            "generation": gens,
            "best_fit": best_gen[1],
            "best_metrics": best_gen[2],
            "best_assign": best_gen[0]
        })

        elites = scored[:elite_k]
        learn_from_assign = random.choice(elites)[0]
        qga.update_towards_elite(learn_from_assign, lr=lr)
    return best_overall, hist