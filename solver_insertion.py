#!/usr/bin/env python3

import sys
import math

from common import print_tour, read_input

def solve(cities):
    # Build a trivial solution.
    # Visit the cities in the order they appear in the input.
    dist = dist_calculator(cities)
    path = solve_by_insertion(cities, dist, 0)
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

# 挿入法: 貪欲法の一種. 距離の合計が最短となる場所に挿入.
# どの都市を挿入するかについて最短、最遠、最廉の三種類ある.
def solve_by_insertion(cities, dist, start_city):
    unvisited = list(range(len(cities)))
    unvisited.remove(start_city)

    curr_path = [start_city]

    # 未訪問の都市がなくなるまで繰り返す
    while unvisited:
        # 挿入する都市を選択する(最近)
        # best_city = select_nearest(dist, curr_path, unvisited)
        # 挿入する都市を選択する(最遠)
        best_city = select_farthest(dist, curr_path, unvisited)
        # 選んだ都市を挿入する
        insert_city(dist, curr_path, best_city, unvisited)
        # 挿入した都市を未訪問リストから削除する
        unvisited.remove(best_city)
    
    return curr_path


# 選択された都市を部分巡回路に挿入する処理.
def insert_city(dist, curr_path, inserting_city, unvisited):
    if len(curr_path) == 1:
        curr_path.append(inserting_city)
        return
    
    best_insert_idx = -1
    min_cost_increase = float("inf")
    n = len(curr_path)

    # curr_path 内のすべての隣接する都市ペアを調べる
    for i in range(n):
        j = (i+1) % n

        city_i = curr_path[i]
        city_j = curr_path[j]

        # city_iとcity_jの間にinserting_cityを挿入した時の距離の増加量
        cost_increase = dist[city_i][inserting_city] + dist[inserting_city][city_j] - dist[city_i][city_j]

        if min_cost_increase > cost_increase:
            min_cost_increase = cost_increase
            best_insert_idx = i + 1

    curr_path.insert(best_insert_idx, inserting_city)
        

# 最近挿入法: 未訪問の都市のうち、部分巡回路に最も近い都市を選択する.
def select_nearest(dist, curr_path, unvisited):
    min_dist = float('inf')
    best_city = unvisited[0]
    for city1 in curr_path:
        for city2 in unvisited:
            curr_dist = dist[city1][city2]
            if min_dist > curr_dist:
                min_dist = curr_dist
                best_city = city2
    # best_cityが確定.
    # unvisited.remove(best_city)
    return best_city
    
# 最遠挿入法: 未訪問の都市のうち、部分巡回路に最も遠い都市を選択する.
def select_farthest(dist, curr_path, unvisited):
    max_dist = 0
    best_city = unvisited[0]
    for city1 in curr_path:
        for city2 in unvisited:
            curr_dist = dist[city1][city2]
            if max_dist < curr_dist:
                max_dist = curr_dist
                best_city = city2
    return best_city

if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print_tour(tour)

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