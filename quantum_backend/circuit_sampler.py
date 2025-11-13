from qiskit_aer import AerSimulator
from qiskit import transpile
import numpy as np
import os
from simulator.feasibility import job_can_run_on

n = os.cpu_count() or 4
sim = AerSimulator()

sim.set_options(
    max_parallel_threads=n,
    max_parallel_experiments=n,
    max_parallel_shots=n
)

os.environ.setdefault("OMP_NUM_THREADS", str(n))
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"

def bitstring_to_res(bitstring: str, num_res: int):
    val = int(bitstring, 2)
    if val >= num_res:
        val = num_res - 1
    return val

def sample_to_res(job_circ, num_res: int, shots: int = 512):
    qc = job_circ.build_circuit()

    tqc = transpile(qc, sim)
    result = sim.run(tqc, shots=shots).result()
    counts = result.get_counts()

    bitstrings = list(counts.keys())
    freqs = np.array([counts[b] for b in bitstrings], dtype=float)

    probs = freqs / freqs.sum()

    chosen = np.random.choice(bitstrings, p=probs)
    res_idx = bitstring_to_res(chosen, num_res)
    return res_idx, probs, bitstrings

def sample_jobs_res_masked_batch(jobs, job_circs, res, shots=512, allowed_map=None):
    num_res = len(res)

    qcs = [jc.build_circuit() for jc in job_circs]
    tqcs = transpile(qcs, sim)

    result = sim.run(tqcs, shots=shots).result()
    counts_list = result.get_counts()

    assignments= []
    for job, counts in zip(jobs, counts_list):
        if allowed_map is not None:
            allowed = allowed_map.get(job.job_id, None)
            allowed_set = set(int(a) for a in allowed) if allowed is not None else None
        else:
            allowed_set = None

        acc = np.zeros(num_res, dtype=float)

        for bs, freq in counts.items():
            ridx = bitstring_to_res(bs, num_res)
            if ridx >= num_res:
                continue

            if allowed_set is not None and ridx not in allowed_set:
                continue

            if not job_can_run_on(job, res[ridx]):
                continue

            acc[ridx] += float(freq)

        total = acc.sum()
        if total > 0:
            probs = acc / total
            ridx = int(np.random.choice(num_res, p=probs))
        else:
            feasible = [r.res_id for r in res if job_can_run_on(job, r)]
            if allowed_set is not None and feasible:
                cand = [rid for rid in feasible if rid in allowed_set]
                if cand:
                    ridx = int(np.random.choice(cand))
                elif feasible:
                    ridx = int(np.random.choice(feasible))
                else:
                    ridx = 0
            elif feasible:
                ridx = int(np.random.choice(feasible))
            else:
                ridx = 0

        assignments.append(ridx)

    return assignments