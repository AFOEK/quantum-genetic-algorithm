from qiskit import QuantumCircuit, transpile
import numpy as np

class QJob:
    def __init__(self, num_qubits=2, theta=None):
        self.num_qubits = num_qubits
        if theta is None:
            self.theta = np.random.uniform(low=0.2, high=1.0, size=(3,))
        else:
            self.theta = np.array(theta, dtype=float)

        self._qc = None
        self._tqc = None

    def build_circuit(self):
        if self._qc is None:
            qc = QuantumCircuit(self.num_qubits)

            qc.ry(self.theta[0], 0)
            qc.ry(self.theta[1], 1)

            qc.cx(0, 1)
            qc.ry(self.theta[2], 1)
            qc.cx(0, 1)

            qc.measure_all()
            self._qc = qc
        return self._qc
    
    def transpiled(self, sim):
        if self._tqc is None:
            self._tqc = transpile(self.build_circuit(), sim, optimization_level=0)
        return self._tqc