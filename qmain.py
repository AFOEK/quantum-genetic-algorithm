from quantum_backend.run_qga import run_qga
from simulator.io import load_workload
from config.env import load_env_config
from simulator.precompute import precompute_allowed, find_trivial_jobs
import math

def short_assign(vectors, head=10, tail=3):
    n = len(vectors)
    if n <= head + tail:
        return "[" + ", ".join(map(str, vectors)) + "]"
    return "[" + ", ".join(map(str, vectors[:head])) + ", ...," + ", ".join(map(str, vectors[-tail:])) + "]"

def print_best(best_tuple):
    assign, fit, m = best_tuple
    print("\n=== BEST SOLUTION ===")
    print(f"fitness   : {fit:,.3f}")
    print(f"cost      : {m.get('total_cost', 0.0):,.3f}")
    print(f"makespan  : {m.get('makespan', 0.0):,.3f}")
    print(f"penalty   : {m.get('sla_penalty', 0.0):,.3f}")
    print(f"violations: {m.get('capacity_violations', 0)}")
    print(f"assign    : {short_assign(assign)}")
    print("======================\n")

def print_history(history):
    print("=== TRAINING HISTORY (one line per generation) ===")
    print("gen |      fit |   cost | makespan | penalty | viol | assign")
    print("----+----------+--------+----------+---------+------+---------------------------")
    for h in history:
        print(f"{h['generation']:3d} | {h['best_fit']:8.3f} |"
              f"{h.get('cost', 0.0):7.1f} | {h.get('makespan', 0.0):8.1f} |"
              f"{h.get('penalty', 0.0):7.1f} | {h.get('viol', 0):4d} | {short_assign(h['best_assign'])}")

def main():
    conf = load_env_config(".qga.env")
    jobs, res = load_workload(conf.jobs_path, conf.resources_path)

    allowed = precompute_allowed(jobs, res)
    fixed, hard = find_trivial_jobs(jobs, res, allowed, dominance_ratio=0.60)

    batch_size = min(64, max(32, int(0.25 * max(1, len(hard)))))
    
    if conf.num_qubits is None:
        n_res = len(res)
        num_qubits = max(1, math.ceil(math.log2(max(1, n_res))))

    print("=== RUN CONFIG ===")
    print(f"jobs={len(jobs)}  resources={len(res)}  hard_jobs={len(hard)}  fixed={len(fixed)}")
    print(f"batch_size={batch_size}  num_qubits={num_qubits}  shots={conf.shots}")
    print(f"gen={conf.generation}  pop={conf.pop_size}  elite={conf.elite_k}")
    print(f"lr_start={conf.lr_start}  lr_decay={conf.lr_decay}  "
          f"eps_start={conf.eps_start}  eps_decay={conf.eps_decay}  "
          f"mut_p={conf.mutation_prob}  mut_sigma={conf.mutation_sigma}")
    print("===================\n")

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
        shots=conf.shots,
        allowed=allowed,
        fixed_assign=fixed,
        hard_job=hard,
        batch_size=batch_size
    )

    print_best(best)
    print_history(hist)
    
if __name__ == "__main__":
    main()