from simulator.workload_test import demo_workload
from optimizer.run_qga import run_qga_test

def run():
    jobs, resources = demo_workload()
    best, hist = run_qga_test(jobs, resources, generation=50, pop_size=50, elite_k=6, lr=0.01)

    print("Assignment (job->resource):", best[0])
    print("Fitness:", best[1])
    print("Metrics:", best[2])

    for h in hist:
        print(f"gen {h['generation']:02d} | fit {h['best_fit']:.3f} | assign {h['best_assign']}")

if __name__ == "__main__":
    run()