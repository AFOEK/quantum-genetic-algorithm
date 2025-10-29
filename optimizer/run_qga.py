from .qga_state import QGA_State
from .sampler import make_pop
from .eval_pop import evaluate_population
from .update_rules import update_qga_state

def run_qga_test(jobs,
                resources,
                generation=30,
                pop_size=30,
                elite_k=5,
                lr=0.1):
    
    qga = QGA_State(num_job=len(jobs), num_res=len(resources))
    
    best_overall = None

    hist = []

    for gen in range(generation):
        pop = make_pop(qga, pop_size)

        scored = evaluate_population(pop, jobs, resources)

        best_gen = scored[0]
        if best_overall is None or best_gen[1] < best_overall[1]:
            best_overall = best_gen

        hist.append({
            "generation": gen,
            "best_fit": best_gen[1],
            "best_metrics": best_gen[2],
            "best_assign": best_gen[0]
        })

        elites = scored[:elite_k]

        update_qga_state(qga, elites, lr)

    return best_overall, hist