from typing import List
from .job import Job
from .resources import Resource

def demo_workload():
    resources: List[Resource] = [
        Resource(
            res_id=0,
            name="cpu_sm_test",
            res_type="cpu",
            cpu_cap=2,
            ram_cap=1,
            gpu_cap=0,
            qpu_cap=0,
            parallel_capacity=2,
            cost_per_sec=0.01,
            queue_delay=0.0
        ), 
        Resource(
            res_id=1,
            name="gpu_dummy_test",
            res_type="gpu",
            cpu_cap=8,
            ram_cap=16,
            gpu_cap=2,
            qpu_cap=0,
            parallel_capacity=1,
            cost_per_sec=0.75,
            queue_delay=2.0
        ),
        Resource(
            res_id=2,
            name="qpu_dummy_test",
            res_type="qpu",
            cpu_cap=0,
            ram_cap=0,
            gpu_cap=0,
            qpu_cap=1,
            parallel_capacity=1,
            cost_per_sec=0.1,
            queue_delay=10.0
        )
    ]

    jobs: List[Job] = [
        Job(
            job_id=0,
            cpu_req=1,
            ram_req=1,
            gpu_req=0,
            qpu_req=0,
            deadline=15.0,
            priority=1.0,
            runtime_profiler={"cpu":10.0, "gpu":5.0}
        ),
        Job(
            job_id=1,
            cpu_req=8,
            ram_req=16,
            gpu_req=2,
            qpu_req=0,
            deadline=25.0,
            priority=1.5,
            runtime_profiler={"cpu":40.0, "gpu":15.0}
        ),
        Job(
            job_id=2,
            cpu_req=1,
            ram_req=2,
            gpu_req=0,
            qpu_req=1,
            deadline=50.0,
            priority=2.0,
            runtime_profiler={"cpu":100.0, "qpu":0.0}
        ),
        Job(
            job_id=3,
            cpu_req=2,
            ram_req=4,
            gpu_req=4,
            qpu_req=1,
            deadline=75.0,
            priority=2.5,
            runtime_profiler={"cpu":25.0,"gpu":75.0,"qpu":0.0}
        ),
        Job(
            job_id=4,
            cpu_req=4,
            ram_req=16,
            gpu_req=0,
            qpu_req=0,
            deadline=45.0,
            priority=2.0,
            runtime_profiler={"cpu":10.0,"gpu":35.0}
        )
    ]

    return jobs, resources