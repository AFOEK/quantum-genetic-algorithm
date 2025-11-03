from simulator.feasibility import job_can_run_on

def repair_assignment(assign, jobs, res):
    fixed = list(assign)
    for j, ridx in enumerate(assign):
        if not job_can_run_on(jobs[j], res[ridx]):
            feasibility = [r.res_id for r in res if job_can_run_on(jobs[j], r)]
            if feasibility:
                fixed[j] = min(feasibility, key=lambda r: jobs[j].runtime_profiler[res[r].res_type] * res[r].cost_pre_sec)
    return fixed 