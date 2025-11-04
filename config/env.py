from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class QGAConf:
    job_path: str = "jobs.json"
    resources_path: str = "resources.json"
    generation: int = 50
    pop_size: int = 25
    elite_k: int = 12
    lr_start: float = 0.08
    lr_decay: float = 0.95
    eps_start: float = 0.10
    eps_decay: float = 0.90
    mutation_prob: float = 0.20
    mutation_sigma: float = 0.03
    num_qubits: Optional[int] = None
    shots: int = 512

def parse_bool(v: str) -> bool:
    return v.strip().lower() in {"1", "true", "yes", "on"}

def load_env_config(path: str = ".qga.env") -> QGAConf:
    conf = QGAConf()
    if not os.path.exists(path):
        return conf
    
    def set_if(k: str, cast, attr: str):
        if k in kv:
            try:
                setattr(conf, attr, cast(kv[k]))
            except Exception:
                pass

    kv = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                line = line.split("#", 1)[0].strip()
            if "=" not in line:
                continue

            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
    
    set_if("JOBS_PATH", str, "jobs_path")
    set_if("RESOURCES_PATH", str, "resources_path")
    set_if("GENERATIONS", str, "generations")
    set_if("POP_SIZE", str, "pop_size")
    set_if("ELITE_K", int, "elite_k")
    set_if("LR_START", float, "lr_start")
    set_if("LR_DECAY", float, "lr_decay")
    set_if("EPS_START", float, "eps_start")
    set_if("EPS_DECAY", float, "eps_decay")
    set_if("MUTATION_PROB", float, "mutation_prob")
    set_if("MUTATION_SIGMA", float, "mutation_sigma")

    if "NUM_QUBITS" in kv:
        v = kv["NUM_QUBITS"].strip().upper()
        if v == "AUTO":
            conf.num_qubits = None
        else:
            try:
                conf.num_qubits = int(v)
            except Exception:
                conf.num_qubits = None

    set_if("SHOTS", int, "shots")
    return conf