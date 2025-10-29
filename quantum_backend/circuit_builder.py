from qiskit import QuantumCircuit
import numpy as np

class QJob:
    def __init__(self, num_qubits=2, theta=None):
        self.num_qubits = num_qubits
        if theta is None:
            self.theta = np.random.uniform(low=0.2, high=1.0, size=(3,))
        else:
            self.theta = np.array(theta, dtype=float)

    def build_circuit(self):
        qc = QuantumCircuit(self.num_qubits)

        qc.ry(self.theta[0], 0)
        qc.ry(self.theta[1], 1)

        qc.cx(0, 1)
        qc.ry(self.theta[2], 1)
        qc.cx(0, 1)

        qc.measure_all()
        return qc