from typing import List
from .circuit_builder import QJob
from .circuit_sampler import sample_job_res_masked
from .circuit_update import update_toward_res

class QGAState:
    def __init__(self, num_jobs: int, num_res: int):
        self.num_jobs = num_jobs
        self.num_res = num_res

        self.num_qubits = 2

        self.job_circuits: List[QJob] = [
            QJob(num_qubits=self.num_qubits)
            for _ in range(num_jobs)
        ]
    
    def sample_assigment(self, jobs, res):
        assignment = []
        for j in range(self.num_jobs):
            chosen_res = sample_job_res_masked(
                jobs[j], self.job_circuits[j], res, shots=512
            )
            assignment.append(chosen_res if chosen_res is not None else 0)
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
        delta = sum(float((a-b).mean()) for a,b in zip(after, before)) / self.num_jobs
        print(f"Debug mean d_theta per job, mean: {abs(delta):.4f}")