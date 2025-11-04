from typing import List, Tuple
import json
import os

from .job import Job
from .resources import Resource

def load_resources(path: str) -> List[Resource]:
    with open(path, "r") as f:
        data = json.load(f)

    res = []
    seen_ids = set()

    for r in data.get("resources", []):
        rid = int(r["res_id"])
        if rid in seen_ids:
            raise ValueError(f"Duplicate res_id {rid} in {path}")
        seen_ids.add(rid)
        res.append(
            Resource(
                res_id=rid,
                name=str(r.get("name", f"res_{rid}")),
                res_type=str(r.get("res_type", "cpu")),
                cpu_cap=int(r.get("cpu_cap", 0)),
                ram_cap=int(r.get("ram_cap", 0)),
                gpu_cap=int(r.get("gpu_cap", 0)),
                qpu_cap=int(r.get("qpu_cap", 0)),
                parallel_capacity=int(r.get("parallel_cap", 1)),
                cost_per_sec=float(r.get("cost_per_sec", 0.0)),
                queue_delay=float(r.get("queue_delay", 0.0))
            )
        )
    ids_sorted = sorted([r.res_id for r in res])
    if ids_sorted != list(range(len(res))):
        raise ValueError(f"res_id must be 0..{len(res)-1}, got {ids_sorted}")
    return res

def load_jobs(path: str) -> List[Job]:
    with open(path, "r") as f:
        data = json.load(f)

    jobs = []
    seen_ids = set()

    for j in data.get("jobs", []):
        jid = int(j["job_id"])
        if jid in seen_ids:
            raise ValueError(f"Duplicate job_id {jid} in {path}")
        seen_ids.add(jid)
        runtime = j.get("runtime_profiler", {})
        runtime_profiler = {str(k).lower(): float(v) for k, v in runtime.items()}
        jobs.append(
            Job(
                job_id=jid,
                cpu_req=int(j.get("cpu_req", 0)),
                ram_req=int(j.get("ram_req", 0)),
                gpu_req=int(j.get("gpu_req", 0)),
                qpu_req=int(j.get("qpu_req", 0)),
                deadline=float(j.get("deadline", 0.0)),
                priority=float(j.get("priority", 0.0)),
                runtime_profiler=runtime_profiler
            )
        )
    ids_sorted = sorted([j.job_id for j in jobs])
    if ids_sorted != list(range(len(jobs))):
        raise ValueError(f"job_id must be 0..{len(jobs)-1}, got {ids_sorted}")
    return jobs

def load_workload(jobs_path: str, resource_path: str) -> Tuple[List[Job], List[Resource]]:
    if not os.path.exists(jobs_path):
        raise FileNotFoundError(jobs_path)
    if not os.path.exists(resource_path):
        raise FileNotFoundError(resource_path)
    
    resources = load_resources(resource_path)
    jobs = load_jobs(jobs_path)
    return jobs, resources