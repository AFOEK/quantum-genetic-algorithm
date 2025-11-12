import json, random

SEED = None
CPU_PCAP_CHOICES = [1, 2, 4, 8, 16]
CPU_RAM_CHOICES  = [2, 4, 8, 16, 32, 64, 128]
GPU_CPU_CHOICES  = [8, 16, 32, 64]
GPU_RAM_CHOICES  = [16, 32, 64, 128, 256]
GPU_CAP_CHOICES  = [1, 2, 4]

CPU_COST_RANGE   = (0.01, 0.05)
GPU_COST_RANGE   = (0.50, 1.50)
QPU_COST_RANGE   = (1.00, 2.00)

CPU_Q_DELAY      = (0.1, 1.0)
GPU_Q_DELAY      = (1.0, 5.5)
QPU_Q_DELAY      = (5.5, 30.0)

EMISSION_RANGE   = (0.03, 0.40)

DISK_TYPES       = ["ssd", "hdd"]
DISK_CAP_CHOICES = [64, 128, 256, 512, 1024, 2048]
SSD_COST_PER_GB_H  = (2.5e-5, 1.0e-4)
HDD_COST_PER_GB_H  = (1.0e-5, 4.0e-5)


JOB_STORAGE_REQ_GB = [0, 1, 2, 5, 10, 20, 50, 100]
JOB_IO_GB_RANGE    = (0.1, 50.0)   


def _rand_cost(lo_hi): 
    return round(random.uniform(*lo_hi), 3)

def _rand_delay(lo_hi): 
    return round(random.uniform(*lo_hi), 2)

def _rand_emission():   
    return round(random.uniform(*EMISSION_RANGE), 3)

def _disk_cost_range(disk_type):
    return SSD_COST_PER_GB_H if disk_type == "ssd" else HDD_COST_PER_GB_H

def _rand_disk_cost(disk_type):
    lo, hi = _disk_cost_range(disk_type)
    return float(f"{random.uniform(lo, hi):.8f}")

def gen_resources(n_cpu=2, n_gpu=2, n_qpu=1, out="resources.json"):
    if SEED is not None:
        random.seed(SEED)
    resources = []
    r_id = 0

    for _ in range(n_cpu):
        disk_type = random.choice(DISK_TYPES)
        resources.append({
            "res_id": r_id,
            "name": f"cpu_{r_id}",
            "res_type": "cpu",

            "cpu_cap": random.choice(CPU_PCAP_CHOICES),
            "ram_cap": random.choice(CPU_RAM_CHOICES),
            "gpu_cap": random.choice([0, 1]),
            "qpu_cap": 0,

            "parallel_capacity": random.choice([1, 2, 4]),
            "cost_per_sec": _rand_cost(CPU_COST_RANGE),
            "queue_delay": _rand_delay(CPU_Q_DELAY),

            "power_idle_w": round(random.uniform(30, 120), 1),
            "power_active_w": round(random.uniform(120, 300), 1),
            "emission_kg_per_kwh": _rand_emission(),

            "disk_type": disk_type,
            "disk_cap_gb": random.choice(DISK_CAP_CHOICES),
            "disk_cost_per_gb_hour": _rand_disk_cost(disk_type),
        })
        r_id += 1

    for _ in range(n_gpu):
        disk_type = random.choice(DISK_TYPES)
        resources.append({
            "res_id": r_id,
            "name": f"gpu_{r_id}",
            "res_type": "gpu",

            "cpu_cap": random.choice(GPU_CPU_CHOICES),
            "ram_cap": random.choice(GPU_RAM_CHOICES),
            "gpu_cap": random.choice(GPU_CAP_CHOICES),
            "qpu_cap": random.choice([0, 1]),

            "parallel_capacity": random.choice([1, 2, 4]),
            "cost_per_sec": _rand_cost(GPU_COST_RANGE),
            "queue_delay": _rand_delay(GPU_Q_DELAY),

            "power_idle_w": round(random.uniform(80, 200), 1),
            "power_active_w": round(random.uniform(250, 700), 1),
            "emission_kg_per_kwh": _rand_emission(),

            "disk_type": disk_type,
            "disk_cap_gb": random.choice(DISK_CAP_CHOICES),
            "disk_cost_per_gb_hour": _rand_disk_cost(disk_type),
        })
        r_id += 1

    for _ in range(n_qpu):
        disk_type = random.choice(DISK_TYPES)
        resources.append({
            "res_id": r_id,
            "name": f"qpu_{r_id}",
            "res_type": "qpu",

            "cpu_cap": 0,
            "ram_cap": 0,
            "gpu_cap": 0,
            "qpu_cap": 1,

            "parallel_capacity": 1,
            "cost_per_sec": _rand_cost(QPU_COST_RANGE),
            "queue_delay": _rand_delay(QPU_Q_DELAY),

            "power_idle_w": round(random.uniform(500, 1500), 1),
            "power_active_w": round(random.uniform(1200, 3000), 1),
            "emission_kg_per_kwh": _rand_emission(),

            "disk_type": disk_type,
            "disk_cap_gb": random.choice(DISK_CAP_CHOICES),
            "disk_cost_per_gb_hour": _rand_disk_cost(disk_type),
        })
        r_id += 1

    with open(out, "w") as f:
        json.dump({"resources": resources}, f, indent=2)

def gen_jobs(n=50, out="jobs.json"):
    if SEED is not None:
        random.seed(SEED)

    jobs = []
    for jid in range(n):
        kind = random.choices(["cpu", "gpu", "qpu"], [0.6, 0.35, 0.05])[0]

        if kind == "cpu":
            cpu = random.choice([1, 2, 4, 8, 16])
            ram = random.choice([1, 2, 4, 8, 16, 32, 64])
            runt = {
                "cpu": round(random.uniform(5, 60), 1),
                "gpu": round(random.uniform(2, 40), 1)
            }
            job = {
                "job_id": jid,
                "cpu_req": cpu,
                "ram_req": ram,
                "gpu_req": 0,
                "qpu_req": 0,
                "deadline": round(random.uniform(20, 200), 1),
                "priority": round(random.uniform(1.0, 3.0), 1),
                "runtime_profiler": runt,
            }

        elif kind == "gpu":
            cpu = random.choice([4, 8, 16, 32, 64])
            ram = random.choice([8, 16, 32, 64, 128, 256])
            gpu = random.choice([1, 2, 4])
            qpu = random.choice([0, 1])
            runt = {
                "cpu": round(random.uniform(40, 200), 1),
                "gpu": round(random.uniform(8, 60), 1),
                "qpu": round(random.uniform(0, 20), 1)
            }
            job = {
                "job_id": jid,
                "cpu_req": cpu,
                "ram_req": ram,
                "gpu_req": gpu,
                "qpu_req": qpu,
                "deadline": round(random.uniform(45, 350), 1),
                "priority": round(random.uniform(1.0, 3.0), 1),
                "runtime_profiler": runt,
            }

        else:
            runt = {
                "cpu": round(random.uniform(0, 450), 1),
                "qpu": round(random.uniform(5, 45), 1)
            }
            job = {
                "job_id": jid,
                "cpu_req": 0,
                "ram_req": 0,
                "gpu_req": 0,
                "qpu_req": 1,
                "deadline": round(random.uniform(65, 450), 1),
                "priority": round(random.uniform(1.0, 3.0), 1),
                "runtime_profiler": runt,
            }

        job["storage_req_gb"] = random.choice(JOB_STORAGE_REQ_GB)
        job["pref_disk_type"] = random.choice(DISK_TYPES)
        job["io_gb"] = round(random.uniform(*JOB_IO_GB_RANGE), 2)

        jobs.append(job)

    with open(out, "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)