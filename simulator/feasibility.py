def job_can_run_on(job, res) -> bool:
    if job.cpu_req > res.cpu_cap: return False
    if job.ram_req > res.ram_cap: return False
    if job.gpu_req > res.gpu_cap: return False
    if job.qpu_req > res.qpu_cap: return False
    if res.res_type not in job.runtime_profiler: return False
    if job.storage_req_gb > 0 and job.storage_req_gb > res.disk_cap_gb: return False
    pref = (job.pref_disk_type or "any").lower()
    if pref not in ("", "any") and res.disk_type.lower() != pref:
        return False
    return True