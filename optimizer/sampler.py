def make_pop(qga_state, pop_size: int):
    return [qga_state.sample_assigment() for _ in range(pop_size)]