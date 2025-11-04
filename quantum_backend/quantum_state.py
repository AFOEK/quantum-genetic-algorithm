from typing import List
from .circuit_builder import QJob
from .circuit_sampler import sample_job_res_masked
from simulator.feasibility import job_can_run_on
from .circuit_update import update_toward_res
import numpy as np

class QGAState:
    def __init__(self, num_jobs: int, num_res: int, num_qubits: int, shots: int):
        self.num_jobs = num_jobs
        self.num_res = num_res

        self.num_qubits = num_qubits
        self.shots = shots

        self.job_circuits: List[QJob] = [
            QJob(num_qubits=self.num_qubits)
            for _ in range(num_jobs)
        ]
    
    def sample_assignment(self, jobs, res, shots = 512 , eps: float = 0.0):
        assignment = []
        for j in range(self.num_jobs):
            if np.random.rand() < eps:
                feasible = [r.res_id for r in res if job_can_run_on(jobs[j], r)]
                ridx = np.random.choice(feasible) if feasible else 0
            else:
                ridx =  sample_job_res_masked(jobs[j], self.job_circuits[j], res, shots=shots)
            assignment.append(int(ridx))
        return assignment
    
    def update_towards_elite(self, elite_assign, lr: float = 0.01):
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