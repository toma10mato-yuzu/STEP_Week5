# === 焼きなまし法 ===
# 局所的最適解から抜け出すため

# import numpy as np
import math
import random
import sys

from common import print_tour, read_input
from solver_greedy import dist_calculator, greedy, two_opt
from solver_insertion import solve_by_insertion

def solve(cities):
    # Build a trivial solution.
    # Visit the cities in the order they appear in the input.
    dist = dist_calculator(cities)
    # path = greedy(cities, 0, dist)
    path = solve_by_insertion(cities, dist, 0)
    path = two_opt(path, dist)
    simulated_annealing(cities, dist, path, n_iter=1000000, cooling_rate=0.9)
    return path


def calc_total_distance(path, dist):
    N = len(path)
    total = sum(dist[path[i]][path[(i+1)%N]] for i in range(N))
    return total

def random_two_opt(curr_path):
    # 現在の経路からランダムに二箇所選び、その区間を逆順にした新しいルートを作る
    n = len(curr_path)

    # 0,1,...,n-1から異なる2つのインデックスをランダムに選ぶ
    i, j = sorted(random.sample(range(n), 2))

    # i,jを入れ替える
    new_path = curr_path[:i] + curr_path[i:j+1][::-1] + curr_path[j+1:]

    return new_path


# 初期温度の計算
def calculate_initial_temperature(curr_path, dist, p0=0.5):
    # p0: 改悪を許容する確率. デフォルト0.5に設定.
    N=len(curr_path)
    # 距離が悪化した時の差分をメモするリスト.
    worse_diffs = []
    # curr_path の総距離
    curr_dist = calc_total_distance(curr_path, dist)
    # 100回繰り返す.
    for _ in range(100):
        # ランダムに選んだ二点をひっくり返して得られた近傍とその経路の総距離
        new_path = random_two_opt(curr_path)
        new_dist = calc_total_distance(new_path, dist)
        # 距離の差分
        diff = new_dist - curr_dist

        # 距離が伸びてたら悪化したときのリストに記録.
        if diff > 0:
            worse_diffs.append(diff)
    
    # メモした悪化幅の平均値を計算
    ave_worse_diff = sum(worse_diffs) / len(worse_diffs)

    # 数式から温度を逆算
    # T0 = - 解の悪化幅の平均 / ln(p0)
    T0 = - ave_worse_diff / math.log(p0)

    return T0

    
# 焼きなまし法
def simulated_annealing(cities, dist, initial_path, n_iter=100000, cooling_rate=0.99):
    curr_path = initial_path
    curr_dist = calc_total_distance(curr_path, dist)

    best_path = curr_path
    best_dist = curr_dist

    # 初期温度設定
    T = calculate_initial_temperature(curr_path, dist)

    for i in range(n_iter):
        # 近傍を作成
        new_path = random_two_opt(curr_path)
        new_dist = calc_total_distance(new_path, dist)

        diff = new_dist - curr_dist

        # 距離が改善したか確率を満たしたら変更
        if diff < 0 or random.random() < math.exp(-diff / T):
            curr_path = new_path
            curr_dist = new_dist

            if curr_dist < best_dist:
                best_path = curr_path
                best_dist = curr_dist
        T *= cooling_rate

    return best_path


if __name__ == '__main__':
    assert len(sys.argv) > 1
    tour = solve(read_input(sys.argv[1]))
    print_tour(tour)