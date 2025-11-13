from typing import List, Optional
from .circuit_builder import QJob
from .circuit_sampler import sample_jobs_res_masked_batch
from simulator.feasibility import job_can_run_on
from .circuit_update import update_toward_res
import numpy as np
import math

class QGAState:
    def __init__(self, num_jobs: int, num_res: int, num_qubits: int, shots: int):
        self.num_jobs = num_jobs
        self.num_res = num_res

        if num_qubits is None:
            num_qubits = max(1, math.ceil(math.log2(max(1, self.num_res))))
        elif self.num_res > (1 << num_qubits):
            num_qubits = math.ciel(math.log2(self.num_res))

        self.num_qubits = num_qubits
        self.shots = shots

        assert self.num_res <= (1 << self.num_qubits), (
            f"num_res={self.num_res} requires at least num_qubits={math.ceil(math.log2(self.num_res))}"
        )

        self.job_circuits: List[QJob] = [
            QJob(num_qubits=self.num_qubits)
            for _ in range(num_jobs)
        ]
    
    def sample_assignment(self, jobs, res, shots: Optional[int] = None , eps: float = 0.0, allowed: Optional[dict] = None) -> List[int]:
        use_shots = int(self.shots if shots is None else shots)
        assignment = [None] * self.num_jobs

        q_jobs = []
        q_circs = []
        q_indices = []

        for j in range(self.num_jobs):
            job = jobs[j]
            if np.random.rand() < eps:
                feasible = [r.res_id for r in res if job_can_run_on(job, r)]
                if feasible:
                    ridx = int(np.random.choice(feasible))
                else:
                    rp = getattr(job, "runtime_profiler", {})
                    cands = [r for r in res if r.res_type in rp]
                    if cands:
                        ridx = min(cands, key=lambda r: rp[r.res_type]).res_id
                    else:
                        ridx = 0
                assignment[j] = ridx
            else:
                q_jobs.append(job)
                q_circs.append(self.job_circuits[j])
                q_indices.append(j)

        if q_jobs:
            if allowed is not None:
                allowed_map = {job.job_id: allowed.get(job.job_id, None) for job in q_jobs}
            else:
                allowed_map = None

            q_assigns = sample_jobs_res_masked_batch(
                q_jobs,
                q_circs,
                res,
                shots=use_shots,
                allowed_map=allowed_map
            )

            for idx, ridx in zip(q_indices, q_assigns):
                assignment[idx] = int(ridx)

        assignment = [0 if a is None else a for a in assignment]
        return assignment
        
    
    def update_towards_elite(self, elite_assign: List[int], lr: float = 0.01) -> float:
        before = [jc.theta.copy() for jc in self.job_circuits]
        for j in range(self.num_jobs):
            update_toward_res(
                self.job_circuits[j],
                target_res=elite_assign[j],
                num_res=self.num_res,
                lr=lr
            )
        after = [jc.theta for jc in self.job_circuits]
        mean_delta = float(np.mean([np.mean(np.abs(a - b)) for a, b in zip(after, before)]))
        return mean_delta