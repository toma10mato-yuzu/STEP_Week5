#!/usr/bin/env python3

import sys
import math
import random

from common import print_tour, read_input


def solve(cities):
    # Build a trivial solution.
    # Visit the cities in the order they appear in the input.
    dist = dist_calculator(cities)
    path = greedy(cities, 0, dist)
    path = two_opt(path, dist)
    return path

# 任意の2都市間の距離を計算する.
# 引数: cities
# 2重リストdistを返す.
# distの初期値はf"inf"とし、同じ都市を指す場所には0ではなくf"inf"のままにする.
def dist_calculator(cities):
    N = len(cities)
    dist = [[float('inf')]*N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            dist[i][j] = math.dist(cities[i], cities[j])
    return dist

def greedy(cities, curr_city, dist):
    N = len(cities)
    #未訪問の都市のインデックスを集合で持つ
    unvisited = set(range(0, N))
    unvisited.remove(curr_city)
    path = [curr_city]

    while unvisited:
        next_city = min(unvisited, key=lambda x: dist[curr_city][x])
        path.append(next_city)
        unvisited.remove(next_city)
        curr_city = next_city
    return path

def two_opt(path, dist):
    N = len(path)

    while True:
        count = 0
        for i in range(N-2):
            for j in range(i+2, N):
                # A-BとC-Dが交差しているとき、AB+CD > AD+CB
                l1 = dist[path[i]][path[i+1]]
                l2 = dist[path[j]][path[(j+1) % N]]
                l3 = dist[path[i]][path[j]]
                l4 = dist[path[i+1]][path[(j+1) % N]]
                if l1 + l2 > l3 + l4:
                    new_path = path[i+1: j+1]
                    path[i+1: j+1] = new_path[::-1]
                    count += 1
        if count == 0:
            break
    return path


    

if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print_tour(tour)
