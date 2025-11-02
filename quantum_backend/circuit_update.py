import numpy as np

def int_to_bitstring(val: int, num_qubit: int) -> str:
    return format(val, f"0{num_qubit}b")

def update_toward_res(job_circ, target_res: int, num_res: int, lr: float =0.01):
    num_qubits = job_circ.num_qubits
    target_bits = int_to_bitstring(min(target_res, num_res - 1), num_qubits)

    theta = job_circ.theta.copy()

    if num_qubits >= 1:
        bit_q0 = target_bits[-1]
        theta[0] += (+1 if bit_q0 == '1' else -0.6) * lr
    if num_qubits >=2 :
        bit_q1 = target_bits[-2] if len(target_bits) >= 2 else '0'
        theta[1] += (+1 if bit_q1 == "1" else -0.6) * lr

    theta[2] += 0.8 * lr
    theta = np.clip(theta, 0.0, np.pi)
    job_circ.theta = theta