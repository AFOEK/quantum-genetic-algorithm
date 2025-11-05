from qiskit_aer import AerSimulator
from qiskit import transpile
import numpy as np
from simulator.feasibility import job_can_run_on

sim = AerSimulator()

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

def sample_job_res_masked(job, job_circ, res, shots = 512, allowed=None):
    num_res = len(res)
    qc = job_circ.build_circuit()
    tqc = transpile(qc, sim)
    result = sim.run(tqc, shots=shots).result()
    counts = result.get_counts()

    allowed = set(int(a) for a in allowed) if allowed is not None else None

    acc_probs = np.zeros(num_res, dtype=float)
    
    for bs, freq in counts.items():
        ridx = bitstring_to_res(bs, num_res=num_res)
        if allowed is not None and ridx not in allowed:
            continue
        if job_can_run_on(job, res[ridx]):
            continue

        acc_probs[ridx] += float(freq)

    total = acc_probs.sum()
    if total > 0:
        probs = acc_probs / total
        return int(np.random.choice(num_res, p=probs))
    
    feasible_ids = [r.res_id for r in res if job_can_run_on(job, r)]
    if allowed is not None:
        cand = [rid for rid in feasible_ids if rid in allowed]
        if cand:
            return int(np.random.choice(cand))
        
    if feasible_ids:
        return int(np.random.choice(cand))
    
    return 0