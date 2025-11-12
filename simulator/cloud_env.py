from typing import List, Dict
from .job import Job
from .resources import Resource

def sim_alloc(
        assigment: List[int],
        jobs: List[Job],
        resources: List[Resource],
        w_cost: float = 1.0,
        w_makespan: float = 1.0,
        w_sla: float = 10.0,
        w_penalty: float = 10.0,
        w_violation: float = 10000.0,
        w_storage: float = 1.0,
        w_carbon: float = 1.0
):
    DISK_IO_GBPS = {
        "ssd": 0.50,
        "hdd": 0.15,
    }
    PREF_MISMATCH_IO_MULT = 1.20
    PREF_MISMATCH_COST_MULT = 1.10

    res_to_job: Dict[int, List[Job]] = {r.res_id: [] for r in resources}
    for j in jobs:
        res_idx = assigment[j.job_id]
        res_to_job[res_idx].append(j)

    total_cost = 0.0
    total_penalty = 0.0
    total_sla_pen = 0.0
    storage_cost_total = 0.0
    energy_kwh_total = 0.0
    carbon_kg_total = 0.0
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
            if getattr(j, "storage_req_gb", 0) > getattr(r, "disk_cap_gb", 0):
                cap_violation += 1

        current_time = r.queue_delay
        idx = 0
        n = len(q)

        while idx < n:
            batch = q[idx : idx + r.parallel_capacity]

            batch_storage = sum(getattr(j, "storage_req_gb", 0) for j in batch)
            if batch_storage > getattr(r, "disk_cap_gb", 0):
                cap_violation += 1

            runtimes = []
            per_job_runtime = []

            for j in batch:
                rt = j.runtime_profiler.get(r.res_type, None)
                if rt is None:
                    rt = 1e6
                    cap_violation += 1
                
                io_gb = float(getattr(j, "io_gb", 0.0))
                disk_type = getattr(r, "disk_type", "ssd").lower()
                gbps = DISK_IO_GBPS.get(disk_type, 0.20)

                io_time = io_gb / max(gbps, 1e-9)

                pref = getattr(j, "pref_disk_type", "").lower()
                mismatch = (pref in ("ssd", "hdd")) and (pref != disk_type)
                if mismatch:
                    io_time *= PREF_MISMATCH_IO_MULT

                rt_eff = rt + io_time
                runtimes.append(rt_eff)
                per_job_runtime.append((j, rt, io_time, mismatch))
            
            batch_runtime =  max(runtimes)

            for (j, rt, io_time, mismatch), rt_eff in zip(per_job_runtime, runtimes):
                finish_t = current_time + batch_runtime
                job_finish_times[j.job_id] = finish_t

                total_cost += runtimes * r.cost_per_sec

                hr_eff = rt_eff / 3600.0
                storage_cost = getattr(j, "storage_req_gb", 0) * getattr(r, "disk_cost_per_gb_hour", 0.0) * hr_eff
                if mismatch:
                    storage_cost *= PREF_MISMATCH_COST_MULT
                    pref_mismatch_count += 1
                storage_cost_total += storage_cost

                lateness = max(0.0, finish_t - j.deadline)
                total_penalty += lateness * j.priority
                if lateness > 0:
                    total_sla_pen += 1

                avg_power_w = (getattr(r, "power_idle_w", 0.0) + getattr(r, "power_active_w", 0.0)) / 2.0
                e_kwh = avg_power_w * rt_eff / 3_600_000.0
                energy_kwh_total += e_kwh
                carbon_kg_total += e_kwh * getattr(r, "emission_kg_per_kwh", 0.0)

                io_time_total += io_time

            current_time += batch_runtime
            idx += max(1, r.parallel_capacity)

    makespan = max(job_finish_times.values()) if job_finish_times else 0.0

    fitness = (
        w_cost * total_cost +
        w_makespan * makespan +
        w_sla * total_sla_pen +
        w_penalty * total_penalty +
        w_violation * cap_violation +
        w_storage * storage_cost_total +
        w_carbon * carbon_kg_total
    )

    metrics = {
        "total_cost": total_cost,
        "makespan": makespan,
        "sla_penalty": total_penalty,
        "sla_violations": total_sla_pen,
        "capacity_violations": cap_violation,
        "storage_cost_total": storage_cost_total,
        "energy_kwh_total": energy_kwh_total,
        "carbon_kg_total": carbon_kg_total,
        "io_time_total_sec": io_time_total,
        "pref_mismatch_count": pref_mismatch_count,
        "fitness": fitness,  
    }

    return fitness, metrics