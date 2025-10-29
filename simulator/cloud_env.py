from typing import List, Dict
from .job import Job
from .resources import Resource

def sim_alloc(
        assigment: List[int],
        jobs: List[Job],
        resources: List[Resource],
        w_cost: float = 1.0,
        w_makespan: float = 1.0,
        w_penalty: float = 10.0,
        w_violation: float = 1000.0
):
    res_to_job: Dict[int, List[Job]] = {r.res_id: [] for r in resources}
    for j in jobs:
        res_idx = assigment[j.job_id]
        res_to_job[res_idx].append(j)

    total_cost = 0.0
    total_penalty = 0.0
    job_finish_times = {}

    cap_violation = 0

    for r in resources:
        q = res_to_job[r.res_id]

        if not q:
            continue


        #Capacity check
        for j in q:
            if(j.cpu_req > r.cpu_cap or 
               j.ram_req > r.ram_cap or 
               j.gpu_req > r.gpu_cap or 
               j.qpu_req > r.qpu_cap):
                cap_violation += 1

        current_time = r.queue_delay
        idx = 0
        n = len(q)

        while idx < n:
            batch = q[idx : idx + r.parallel_capacity]
            runtimes = []
            for j in batch:
                runtime_here = j.runtime_profiler.get(r.res_type, None)
                if runtime_here is None:
                    runtime_here = 1e6
                    cap_violation += 1
                runtimes.append(runtime_here)

            batch_runtime = max(runtimes)

            for j, rt in zip(batch, runtimes):
                finish_t = current_time + batch_runtime
                job_finish_times[j.job_id] = finish_t
                #Total cost
                total_cost += rt * r.cost_per_sec
                #SLA Penalty if too long
                lateness = max(0.0, finish_t - j.deadline)
                total_penalty += lateness * j.priority
            
            current_time += batch_runtime
            idx += r.parallel_capacity

    makespan = max(job_finish_times.values()) if job_finish_times else 0.0

    fitness = (
        w_cost * total_cost +
        w_makespan * makespan +
        w_penalty * total_penalty +
        w_violation * cap_violation
    )

    metrics = {
        "total_cost": total_cost,
        "makespan": makespan,
        "sla_penalty": total_penalty,
        "capacity_violations":cap_violation,
        "fitness":fitness,        
    }

    return fitness, metrics