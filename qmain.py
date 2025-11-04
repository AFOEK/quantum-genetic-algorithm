from quantum_backend.run_qga import run_qga
from simulator.io import load_workload
from config.env import load_env_config
import math

def main():
    conf = load_env_config(".qga.env")
    jobs, res = load_workload(conf.jobs_path, conf.resources_path)

    if conf.num_qubits is None:
        n_res = len(res)
        num_qubits = max(1, math.ceil(math.log2(max(1, n_res))))

    best, hist = run_qga(
        jobs,
        res,
        gen=conf.generation,
        pop_size=conf.pop_size,
        elite_k=conf.elite_k,
        lr_start= conf.lr_start,
        lr_decay= conf.lr_decay,
        mutation_prob= conf.mutation_prob,
        mutation_sigma= conf.mutation_sigma,
        epsilon_start= conf.eps_start,
        epsilon_decay= conf.eps_decay,
        num_qubits=num_qubits,
        shots=conf.shots
    )

    print("assignment (job -> resource): ", best[0])
    print("fitness: ", best[1])
    print("metrics: ", best[2])

    for h in hist:
        print(f"gen {h['generation']:02d} | "
              f"fit {h['best_fit']:.3f} | "
              f"assign {h['best_assign']}"
            )
    
if __name__ == "__main__":
    main()