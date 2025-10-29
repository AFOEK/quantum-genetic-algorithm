from qiskit_aer import AerSimulator
from qiskit import transpile
import numpy as np

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