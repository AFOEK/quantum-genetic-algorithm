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

    bitstrings = list(counts.key())
    freqs = np.array([counts[b] for b in bitstrings], dtype=float)

    probs = freqs / freqs.sum()

    chosen = np.random.choice(bitstrings, p=probs)
    res_idx = bitstring_to_res(chosen, num_res)
    return res_idx, probs, bitstrings

def sample_job_res_masked(job, job_circ, res, shots = 512):
    num_res = len(res)
    qc = job_circ.build_circuit()
    tqc = transpile(qc, sim)
    result = sim.run(tqc, shots=shots).result()
    counts = result.get_counts()

    allowed = []
    freqs = []
    for bs, freq in counts.items():
        ridx = int(bs, 2)
        if ridx < num_res  and job_can_run_on(job, res[ridx]):
            allowed.append(bs)
            freqs.append(freq)

    if allowed:
        probs = np.array(freqs, float)
        probs /= probs.sum()
        chosen_bs = np.random.choice(allowed, p=probs)
        return int(chosen_bs, 2)
    
    feasible = [r.res_id for r in res if job_can_run_on(job, r)]
    return feasible[0] if feasible else 0