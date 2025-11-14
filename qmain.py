from quantum_backend.run_qga import run_qga
from simulator.io import load_workload
from configs.env import load_env_config
from simulator.precompute import precompute_allowed, find_trivial_jobs
import math
import json
from statistics import mean

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

def summarize_metrics(best, hist, out_path: str = "qga_report.json"):
    best_assign, best_fit, best_metrics = best
    best_gen_idx = min(range(len(hist)), key=lambda i: hist[i]["best_fit"])
    best_gen = hist[best_gen_idx]["generation"]
    costs      = [h["best_metrics"].get("total_cost", 0.0)        for h in hist]
    makespans  = [h["best_metrics"].get("makespan", 0.0)          for h in hist]
    sla_pen    = [h["best_metrics"].get("sla_penalty", 0.0)       for h in hist]
    sla_miss   = [h["best_metrics"].get("sla_violations", 0)      for h in hist]
    cap_viol   = [h["best_metrics"].get("capacity_violations", 0) for h in hist]
    storage    = [h["best_metrics"].get("storage_cost_total", 0.0) for h in hist]
    energy     = [h["best_metrics"].get("energy_kwh_total", 0.0)   for h in hist]
    carbon     = [h["best_metrics"].get("carbon_kg_total", 0.0)    for h in hist]
    io_time    = [h["best_metrics"].get("io_time_total_sec", 0.0)  for h in hist]
    pref_miss  = [h["best_metrics"].get("pref_mismatch_count", 0)  for h in hist]

    start_fit = hist[0]["best_fit"]
    end_fit   = hist[-1]["best_fit"]

    abs_improve = start_fit - best_fit
    rel_improve = (abs_improve / start_fit * 100.0) if start_fit > 0 else 0.0

    summary = {
        "best_generation":        best_gen,
        "best_fitness":           best_fit,
        "best_metrics":           best_metrics,

        "start_fitness":          start_fit,
        "end_fitness":            end_fit,
        "absolute_improvement":   abs_improve,
        "relative_improvement_%": rel_improve,

        "avg_cost":               mean(costs),
        "avg_makespan":           mean(makespans),
        "avg_sla_penalty":        mean(sla_pen),
        "avg_sla_violations":     mean(sla_miss),
        "avg_capacity_violations":mean(cap_viol),
        "avg_storage_cost":       mean(storage),
        "avg_energy_kwh":         mean(energy),
        "avg_carbon_kg":          mean(carbon),
        "avg_io_time_sec":        mean(io_time),
        "avg_pref_mismatch_count":mean(pref_miss),
    }
    history_flat = []
    for h in hist:
        g = h["generation"]
        m = h["best_metrics"]
        row = {
            "generation": g,
            "best_fit": h["best_fit"],
            "total_cost":        m.get("total_cost", 0.0),
            "makespan":          m.get("makespan", 0.0),
            "sla_penalty":       m.get("sla_penalty", 0.0),
            "sla_violations":    m.get("sla_violations", 0),
            "capacity_violations": m.get("capacity_violations", 0),
            "storage_cost_total":  m.get("storage_cost_total", 0.0),
            "energy_kwh_total":    m.get("energy_kwh_total", 0.0),
            "carbon_kg_total":     m.get("carbon_kg_total", 0.0),
            "io_time_total_sec":   m.get("io_time_total_sec", 0.0),
            "pref_mismatch_count": m.get("pref_mismatch_count", 0),
        }
        history_flat.append(row)

    report = {
        "summary": summary,
        "best_assignment": best_assign,
        "history": history_flat,
    }

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print("\n=== QGA RUN SUMMARY ===")
    print(f"best generation      : {best_gen}")
    print(f"best fitness         : {best_fit:,.3f}")
    print(f"start fitness        : {start_fit:,.3f}")
    print(f"end fitness          : {end_fit:,.3f}")
    print(f"absolute improvement : {abs_improve:,.3f}")
    print(f"relative improvement : {rel_improve:.2f}%")
    print(f"avg cost             : {summary['avg_cost']:,.3f}")
    print(f"avg makespan         : {summary['avg_makespan']:,.3f}")
    print(f"avg SLA penalty      : {summary['avg_sla_penalty']:,.3f}")
    print(f"avg SLA violations   : {summary['avg_sla_violations']:.2f}")
    print(f"avg capacity viol.   : {summary['avg_capacity_violations']:.2f}")
    print(f"avg carbon (kg)      : {summary['avg_carbon_kg']:,.6f}")
    print("report written to    :", out_path)
    print("========================\n")

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
        f"lr_start={conf.lr_start}  lr_decay={conf.lr_decay}\n"
        f"eps_start={conf.eps_start}  eps_decay={conf.eps_decay}\n"
        f"mut_p={conf.mutation_prob}  mut_sigma={conf.mutation_sigma}"
    )
    print("---- weights ----")
    print(
        f"cost={conf.w_cost}  makespan={conf.w_makespan}  sla={conf.w_sla}\n"
        f"penalty={conf.w_penalty}  violation={conf.w_violation}\n"
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
    summarize_metrics(best, hist, out_path="qga_report.json")
    
if __name__ == "__main__":
    main()