import numpy as np

def int_to_bitstring(val: int, num_qubit: int) -> str:
    return format(val, f"0{num_qubit}b")

def update_toward_res(job_circ, target_res: int, num_res: int, lr: float =0.01):
    num_qubits = job_circ.num_qubits
    target_bits = int_to_bitstring(min(target_res, num_res - 1), num_qubits)

    theta = job_circ.theta.copy()

    for q in range(num_qubits):
        bit = target_bits[num_qubits - 1 - q]

        if q == 0:
            idx = 0
        elif q == 1:
            idx = 1
        else:
            continue

        if bit == "1":
            theta[idx] += lr
        else:
            theta[idx] -= lr

    theta[2] += 0.5 * lr

    theta = np.clip(theta, 0.0, np.pi)
    job_circ.theta = theta