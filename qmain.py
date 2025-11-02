from simulator.workload_test import demo_workload
from quantum_backend.run_qga import run_qga

def main():
    jobs, res = demo_workload()

    best, hist = run_qga(
        jobs,
        res,
        gen=50,
        pop_size=25,
        elite_k=12,
        lr=0.01
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