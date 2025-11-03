from typing import Tuple, List, Dict, Any
from optimizer.eval_pop import evaluate_population
from quantum_backend.quantum_state import QGAState
import numpy as np
import random

def run_qga(
        jobs,
        res,
        gen: int = 30,
        pop_size: int = 20,
        elite_k: int = 5,
        lr_start: float = 0.08,
        lr_decay: float = 0.95,
        mutation_prob: float = 0.20,
        mutation_sigma: float = 0.03,
        epsilon_start: float = 0.10,
        epsilon_decay: float = 0.90
):
    qga = QGAState(num_jobs=len(jobs), num_res=len(res))
    best_overall: Tuple[List[int], float, Dict[str, Any]] = None
    hist: List[Dict[str, Any]] = []
    lr = lr_start
    epsilon = epsilon_start

    for gens in range(gen):
        pop = []
        for _ in range(pop_size):
            assign = qga.sample_assignment(jobs, res, epsilon)
            pop.append(assign)

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

        mean_dtheta = qga.update_towards_elite(learn_from_assign, lr= lr)
        print(f"[GEN {gens:02d}] best_fit={best_gen[1]:.3f}  mean Δθ={mean_dtheta:.4f}  lr={lr:.4f}  eps={epsilon:.3f}")
        
        for jc in qga.job_circuits:
            if np.random.rand() < mutation_prob:
                jc.theta += np.random.normal(0, mutation_sigma, size=jc.theta.shape)
                jc.theta = np.clip(jc.theta, 0.0, np.pi)
        
        lr *= lr_decay
        epsilon *= epsilon_decay

        lr = max(lr, 0.01)
        epsilon = max(epsilon, 0.02)

    return best_overall, hist