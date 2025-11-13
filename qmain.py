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
    io_sec = float(m.get('io_time_total_sec', 0.0))
    io_hr  = io_sec / 3600.0

    print("\n=== BEST SOLUTION ===")
    print(f"fitness     : {fit:,.3f}")
    print(f"cost        : {m.get('total_cost', 0.0):,.3f}")
    print(f"makespan    : {m.get('makespan', 0.0):,.3f}")
    print(f"SLA penalty : {m.get('sla_penalty', 0.0):,.3f}")
    print(f"SLA missed  : {m.get('sla_violations', 0)}")
    print(f"violations  : {m.get('capacity_violations', 0)}")
    print(f"storage $   : {m.get('storage_cost_total', 0.0):,.6f}")
    print(f"energy kWh  : {m.get('energy_kwh_total', 0.0):,.6f}")
    print(f"CO₂ (kg)    : {m.get('carbon_kg_total', 0.0):,.6f}")
    print(f"disk I/O    : {io_sec:,.1f} s  ({io_hr:.3f} h)")
    print(f"pref mismatch: {m.get('pref_mismatch_count', 0)}")
    print(f"assign      : {short_assign(assign)}")
    print("==============================================\n")


def print_history(history):
    print("=== TRAINING HISTORY (one line per generation) ===")
    print("gen |     fit |   cost | makespan |  SLApen | viol |  CO₂kg |  IO(s) | assign")
    print("----+---------+--------+----------+---------+------+--------+--------+---------------------")
    for h in history:
        m = h.get('best_metrics', {})
        io_s = float(m.get('io_time_total_sec', 0.0))
        print(f"{h['generation']:3d} | {h['best_fit']:8.1f} |"
              f"{m.get('total_cost', 0.0):7.1f} | {m.get('makespan', 0.0):8.1f} |"
              f"{m.get('sla_penalty', 0.0):7.1f} | {m.get('capacity_violations', 0):4d} |"
              f"{m.get('carbon_kg_total', 0.0):6.3f} | {io_s:6.1f} | {short_assign(h['best_assign'])}")

def main():
    conf = load_env_config(".qga.env")
    jobs, res = load_workload(conf.jobs_path, conf.resources_path)

    allowed = precompute_allowed(jobs, res)
    fixed, hard = find_trivial_jobs(jobs, res, allowed, dominance_ratio=0.60)
    impossible = [j for j, feas in allowed.items() if len(feas) == 0]
    easy_jobs = list(fixed.keys())

    batch_size = min(64, max(32, int(0.25 * max(1, len(hard)))))
    
    if conf.num_qubits is None:
        n_res = len(res)
        num_qubits = max(1, math.ceil(math.log2(max(1, n_res))))

    print("=== RUN CONFIG ===")
    print(f"jobs={len(jobs)}  resources={len(res)}")
    print(f"easy_jobs={len(easy_jobs)}  hard_jobs={len(hard)}  impossible_jobs={len(impossible)}")
    print(f"batch_size={batch_size}  num_qubits={num_qubits}  shots={conf.shots}")
    print(f"gen={conf.generation}  pop={conf.pop_size}  elite={conf.elite_k}")
    print(
        f"lr_start={conf.lr_start}  lr_decay={conf.lr_decay}  "
        f"eps_start={conf.eps_start}  eps_decay={conf.eps_decay}  "
        f"mut_p={conf.mutation_prob}  mut_sigma={conf.mutation_sigma}"
    )
    print("---- weights ----")
    print(
        f"cost={conf.w_cost}  makespan={conf.w_makespan}  sla={conf.w_sla}  "
        f"penalty={conf.w_penalty}  violation={conf.w_violation}  "
        f"storage={conf.w_storage}  carbon={conf.w_carbon}"
    )
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
        batch_size=batch_size,
        w_cost=conf.w_cost,
        w_makespan=conf.w_makespan,
        w_sla=conf.w_sla,
        w_penalty=conf.w_penalty,
        w_violation=conf.w_violation,
        w_storage=conf.w_storage,
        w_carbon=conf.w_carbon
    )

    print_best(best)
    print_history(hist)
    
if __name__ == "__main__":
    main()