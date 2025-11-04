import json, random

def gen_resources(n_cpu=2, n_gpu=2, n_qpu=1, out="resources.json"):
    resources = []
    r_id = 0

    for _ in range(n_cpu):
        resources.append({
            "res_id": r_id,
            "name": f"cpu_{r_id}",
            "res_type": "cpu",
            "cpu_cap": random.choice([1,2,4,8,16]),
            "ram_cap": random.choice([2,4,8,16,32,64,128]),
            "gpu_cap": random.choice([0,1]),
            "qpu_cap": 0,
            "parallel_capacity": random.choice([0,1,2,4]),
            "cost_per_sec": round(random.uniform(0.01, 0.05), 3),
            "queue_delay": round(random.uniform(0.1, 1), 2)
        })
        r_id += 1

    for _ in range(n_gpu):
        resources.append({
            "res_id": r_id,
            "name": f"gpu_{r_id}",
            "res_type": "gpu",
            "cpu_cap": random.choice([8, 16, 32, 64]),
            "ram_cap": random.choice([16, 32, 64, 128, 256]),
            "gpu_cap": random.choice([1,2,4]),
            "qpu_cap": random.choice([0,1]),
            "parallel_capacity": random.choice([2,4]),
            "cost_per_sec": round(random.uniform(0.5, 1.5), 3),
            "queue_delay": round(random.uniform(1.0, 5.5), 1)
        })
        r_id += 1

    for _ in range(n_qpu):
        resources.append({
            "res_id": r_id,
            "name": f"qpu_{r_id}",
            "res_type": "qpu",
            "cpu_cap": 0,
            "ram_cap": 0,
            "gpu_cap": 0,
            "qpu_cap": 1,
            "parallel_capacity": 1,
            "cost_per_sec": round(random.uniform(1.0, 2.0), 2),
            "queue_delay": round(random.uniform(5.5, 30.0), 1)
        })
        r_id += 1

    with open(out, "w") as f:
        json.dump({"resources": resources}, f, indent=2)

def gen_jobs(n=50, out="jobs.json"):
    jobs = []
    for jid in range(n):
        kind = random.choices(["cpu", "gpu", "qpu"], [0.6, 0.35, 0.05])[0]
        if kind == "cpu":
            cpu = random.choice([1,2,4,8,16])
            ram = random.choice([1,2,4,8,16,32,64])
            runt = {"cpu": round(random.uniform(5, 60), 1), "gpu": round(random.uniform(2, 40), 1)}
            jobs.append({
                "job_id": jid,
                "cpu_req": cpu,
                "ram_req": ram,
                "gpu_req": 0,
                "qpu_req": 0,
                "deadline": round(random.uniform(20, 200), 1),
                "priority": round(random.uniform(1.0, 3.0), 1),
                "runtime_profiler": runt
            })
        elif kind == "gpu":
            cpu = random.choice([4, 8, 16, 32, 64])
            ram = random.choice([8, 16, 32, 64, 128, 256])
            gpu = random.choice([1,2,4])
            qpu = random.choice([0,1])
            runt = {"cpu": round(random.uniform(40, 200), 1), "gpu": round(random.uniform(8, 60), 1), "qpu": round(random.uniform(0, 20), 1)}
            jobs.append({
                "job_id": jid,
                "cpu_req": cpu,
                "ram_req": ram,
                "gpu_req": gpu,
                "qpu_req": qpu,
                "deadline": round(random.uniform(45, 350), 1),
                "priority": round(random.uniform(1.0, 3.0), 1),
                "runtime_profiler": runt
            })
        else:
            runt = {"cpu": round(random.uniform(00, 450), 1), "qpu": round(random.uniform(5, 45), 1)}
            jobs.append({
                "job_id": jid,
                "cpu_req": 0,
                "ram_req": 0,
                "gpu_req": 0,
                "qpu_req": 1,
                "deadline": round(random.uniform(65, 450), 1),
                "priority": round(random.uniform(1.0, 3.0), 1),
                "runtime_profiler": runt
            })

    with open(out, "w") as f:
        json.dump({"jobs": jobs}, f, indent=2)