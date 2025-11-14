from typing import Tuple, List, Dict, Any, Optional
from optimizer.eval_pop import evaluate_population
from quantum_backend.quantum_state import QGAState
import numpy as np
import random
import time

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
        epsilon_decay: float = 0.90,
        num_qubits: int = 2,
        shots: int = 512,
        allowed: Optional[Dict[int, List[int]]] = None,
        fixed_assign: Optional[Dict[int, int]] = None,
        hard_job: Optional[List[int]] = None,
        batch_size: int = 64,
        w_cost: float = 1.0,
        w_makespan: float = 1.0,
        w_sla: float = 10.0,
        w_penalty: float = 10.0,
        w_violation: float = 10000.0,
        w_storage: float = 1.0,
        w_carbon: float = 1.0

):
    qga = QGAState(num_jobs=len(jobs), num_res=len(res), num_qubits=num_qubits, shots=shots)
    best_overall: Tuple[List[int], float, Dict[str, Any]] = None
    hist: List[Dict[str, Any]] = []
    lr = lr_start
    epsilon = epsilon_start

    current_assign = [0] * len(jobs)
    if fixed_assign:
        for j, r in fixed_assign.items():
            current_assign[j] = r

    def make_batches(batch_idxs):
        current = current_assign.copy()
        samples = qga.sample_assignment(jobs, res, shots, epsilon, allowed)

        for j in batch_idxs:
            current[j] = samples[j]

        if fixed_assign:
            for j, r in fixed_assign.items():
                current[j] = r
        
        return current
    
    hard_idxs = hard_job if hard_job is not None else list(range(len(jobs)))
    
    weights = dict(
    w_cost=w_cost,
    w_makespan=w_makespan,
    w_sla=w_sla,
    w_penalty=w_penalty,
    w_violation=w_violation,
    w_storage=w_storage,
    w_carbon=w_carbon,
    )

    for gens in range(gen):
        t_start = time.time()
        batch = random.sample(hard_idxs, k=min(batch_size, len(hard_idxs))) if hard_idxs else []

        pop = [make_batches(batch) for _ in range(pop_size)]
        scored, fits, mets = evaluate_population(pop, jobs, res, weights=weights, parallel=True, max_workers=8)
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
        
        for jc in qga.job_circuits:
            if np.random.rand() < mutation_prob:
                jc.theta += np.random.normal(0, mutation_sigma, size=jc.theta.shape)
                jc.theta = np.clip(jc.theta, 0.0, np.pi)
        
        current_assign = best_gen[0].copy()

        lr *= lr_decay
        epsilon *= epsilon_decay

        lr = max(lr, 0.001)
        epsilon = max(epsilon, 0.001)
        t_stop = time.time()
        t_delta = t_stop - t_start
        print(f"{t_delta:.2f}s | [GEN {gens:02d}] | best_fit={best_gen[1]:.3f} | μΔθ={mean_dtheta:.4f} | lr={lr:.4f} | ε={epsilon:.3f}")
    return best_overall, hist