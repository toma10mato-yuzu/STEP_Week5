#!/usr/bin/env python3

from common import format_tour, read_input

# 書き換え！(1/2)
import solver_insertion
import solver_annealing

CHALLENGES = 7


def generate_output():
    for i in range(CHALLENGES):
        cities = read_input(f'input_{i}.csv')
        # 書き換え！(2/2)
        for solver, name in [(solver_annealing, 'sa_insertion_2opt')]:
            tour = solver.solve(cities)
            with open(f'output_{name}_{i}.csv', 'w') as f:
                f.write(format_tour(tour) + '\n')
            

if __name__ == '__main__':
    generate_output()