from dataclasses import dataclass
from typing import Dict

@dataclass
class Job:
    job_id: int
    cpu_req: int
    ram_req: int
    gpu_req: int
    qpu_req: int

    deadline: float
    priority: float

    runtime_profiler: Dict[str, float]

    storage_req_gb: int = 0
    pref_disk_type: str = "ssd"
    io_gb: float = 0.0