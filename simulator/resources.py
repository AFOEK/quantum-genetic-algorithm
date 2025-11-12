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

    power_idle_w: float = 0.0
    power_active_w: float = 0.0
    emission_kg_per_kwh: float = 0.0

    disk_type: str = "ssd"
    disk_cap_gb: int = 0
    disk_cost_per_gb_hour: float = 0.0