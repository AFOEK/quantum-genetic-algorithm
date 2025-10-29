import numpy as np
from typing import List, Tuple

def update_qga_state(
        qga_state,
        elite: List[Tuple[List[int], float, dict]],
        lr: float = 0.1
    ):
    num_jobs = qga_state.num_job
    num_res = qga_state.num_res

    best_assign = elite[0][0]

    for j in range(num_jobs):
        target_r = best_assign[j]

        for r in range(num_res):
            if r == target_r:
                qga_state.probs[j,r] = qga_state.probs[j,r] + lr * (1.0 - qga_state.probs[j, r])
            else:
                qga_state.probs[j, r] = qga_state.probs[j, r] - lr * (qga_state.probs[j, r])

        row = qga_state.probs[j]
        row[row < 1e-9] = 1e-9
        qga_state.probs[j] = row / row.sum() 