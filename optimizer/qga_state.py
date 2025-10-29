import numpy as np

class QGA_State:
    def __init__(self, num_job: int, num_res: int):
        self.num_job = num_job
        self.num_res = num_res

        self.probs = np.ones((num_job, num_res), dtype=float)
        self.probs /= self.probs.sum(axis=1, keepdims=True)
        
    def sample_assigment(self):
        assign = []
        for j in range(self.num_job):
            assign.append(
                np.random.choice(self.num_res, p=self.probs[j])
            )
        return assign