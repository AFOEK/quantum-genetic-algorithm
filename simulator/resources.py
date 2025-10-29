from dataclasses import dataclass

@dataclass
class Resource:
    res_id: int
    name: str
    res_type: str

    cpu_cap: int
    ram_cap: int
    gpu_cap: int
    qpu_cap: int

    parallel_capacity: int
    cost_per_sec: float
    queue_delay: float