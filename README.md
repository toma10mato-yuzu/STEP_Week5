# STEP_Week5 - TSP Solver
## 概要
本プロジェクトでは、巡回セールスマン問題（TSP）に対する近似解法を実装した。ベースとなる初期解の構築から始め、徐々に解を改善していくアプローチをとっている。具体的には「貪欲法」「挿入法」で初期解を作り、「2-opt法」と「焼きなまし法 (Simulated Annealing)」を用いて局所最適解からの脱出と経路の最適化を図った。前提: 距離データの事前計算毎回の距離計算コストを省くため、最初に全都市間の距離を計算し、2次元配列（リスト）にキャッシュしておく。データ構造: `dist[i][j]` (都市 `i` から都市 `j` への距離を格納する2重リスト)工夫点: 自身への距離（ `i == j` ）は 0 ではなく `float('inf')` に設定し、探索時に同じ都市が選ばれるのを防ぐ。
```Python
def dist_calculator(cities):
    N = len(cities)
    dist = [[float('inf')]*N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            dist[i][j] = math.dist(cities[i], cities[j])
    return dist
```
1. 貪欲法 (Greedy)
### 概要
「今いる場所から一番近い未訪問の都市」をひたすら選び続ける、最もシンプルで高速なアルゴリズム。ただし、終盤に遠くの都市が残りやすく、経路が交差しやすい（局所最適解に陥りやすい）という弱点がある。
### データ構造と手順
- 未訪問リスト: 検索・削除を高速化するため `set` を使用（`unvisited = set(...)`）。
- 手順: 現在の都市から `unvisited` の中で `dist` が最小となる都市を探す。その都市を `path` に追加し、`unvisited` から削除。すべての都市を訪問するまで繰り返す。
```Python
def greedy(cities, curr_city, dist):
    N = len(cities)
    unvisited = set(range(0, N))
    unvisited.remove(curr_city)
    path = [curr_city]

    while unvisited:
        next_city = min(unvisited, key=lambda x: dist[curr_city][x])
        path.append(next_city)
        unvisited.remove(next_city)
        curr_city = next_city
    return path
```
2. 2-opt法 (Local Search)
### 概要
経路の「交差（クロス）」を見つけてほどくための局所探索法。貪欲法などで作った初期回路に対して適用し、無駄な大回りを取り除く。データ構造と手順条件式: 2つのエッジ $AB$、$CD$ について、$AB + CD > AD + CB$ となる場合、繋ぎ変えたほうが距離が短くなる。手順:経路内の考え得るすべての2辺のペアを調べる。交差条件（距離の合計が短くなるか）を満たしたら、リストのスライス `path[i+1: j+1] = new_path[::-1]` を使って区間を逆順に繋ぎ直す。繋ぎ変え（改善）が1度も起きなくなるまで `while True` でループを回す。
```Python
def two_opt(path, dist):
    N = len(path)
    while True:
        count = 0
        for i in range(N-2):
            for j in range(i+2, N):
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
```
3. 挿入法 (Insertion)
### 概要
部分的な巡回路（初期状態では1都市のみ）を用意し、未訪問の都市を1つずつ「最も全体距離の増加が少なくなる位置」に挿入していくアルゴリズム。どの都市から優先して挿入するかで精度が変わり、本実装では「最近挿入法」と「最遠挿入法」の2つを定義。より精度の高くなりやすい最遠挿入法をメインで採用している。
### データ構造と手順未訪問
- リスト: 順番を管理・抽出するため `list` を使用。
- 手順:選択: `unvisited` から次に挿入する都市を選ぶ（`select_farthest` により、現在の部分巡回路から最も遠い都市を選択）。挿入位置の探索: 選んだ都市を `curr_path` のすべての隣接ペア $(i, j)$ の間に挿入した場合のコスト増加量 $\Delta E = dist[i][x] + dist[x][j] - dist[i][j]$ を計算し、最小となるインデックスを探す。リストに `insert()` し、未訪問リストから削除。これを全ての都市を組み込むまで繰り返す。
```Python
def solve_by_insertion(cities, dist, start_city):
    unvisited = list(range(len(cities)))
    unvisited.remove(start_city)

    curr_path = [start_city]

    while unvisited:
        # 挿入する都市を選択する(最遠をデフォルト採用)
        best_city = select_farthest(dist, curr_path, unvisited)
        insert_city(dist, curr_path, best_city, unvisited)
        unvisited.remove(best_city)
    
    return curr_path

def insert_city(dist, curr_path, inserting_city, unvisited):
    if len(curr_path) == 1:
        curr_path.append(inserting_city)
        return
    
    best_insert_idx = -1
    min_cost_increase = float("inf")
    n = len(curr_path)

    for i in range(n):
        j = (i+1) % n
        city_i = curr_path[i]
        city_j = curr_path[j]

        # 距離の増加量
        cost_increase = dist[city_i][inserting_city] + dist[inserting_city][city_j] - dist[city_i][city_j]

        if min_cost_increase > cost_increase:
            min_cost_increase = cost_increase
            best_insert_idx = i + 1

    curr_path.insert(best_insert_idx, inserting_city)

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
```
4. 焼きなまし法 (Simulated Annealing)
   ### 概要
   貪欲法や2-opt法では抜け出せない「局所最適解（谷底）」から脱出するためのメタヒューリスティクス。温度パラメータ $T$ を用い、序盤は「改悪」となる経路変更も確率的に許容し、徐々に温度を下げて厳密な最適化へと移行する。
   ### データ構造と手順
   - 初期解の工夫: ランダムな経路から始めると収束に時間がかかるため、挿入法 -> 2-opt で十分に最適化された経路をスタート地点（初期解）とする。近傍生成 (ランダム2-opt): 探索コストを下げるため、全探索ではなく「ランダムに選んだ2点の区間を反転させる」処理（`random_two_opt`）を採用。
   - 手順:初期温度の自動計算: 初期解に対してランダム2-optを100回試行。悪化した場合の「差分の平均値」を計算し、目標とする初期改悪許容確率（ $p_0 = 0.5$ ）から $` T_0 = -\frac{\text{ave\_worse\_diff}}{\ln(p_0)} `$ として逆算する。
   - 遷移判定: ループ内で近傍を生成し、距離の差分 $\Delta E$ を計算。改善（$\Delta E < 0$）した場合は確定で遷移し、悪化した場合は確率 $P = \exp(-\frac{\Delta E}{T})$ で遷移を許可する。ベストな経路を記録しつつ、温度 $T$ に冷却率（cooling_rate）を掛けて冷やしながら、指定回数（n_iter）ループを回す。
 ```Python
 def calc_total_distance(path, dist):
  N = len(path)
  total = sum(dist[path[i]][path[(i+1)%N]] for i in range(N))
  return total

def random_two_opt(curr_path):
    n = len(curr_path)
    i, j = sorted(random.sample(range(n), 2))
    new_path = curr_path[:i] + curr_path[i:j+1][::-1] + curr_path[j+1:]
    return new_path

def calculate_initial_temperature(curr_path, dist, p0=0.5):
    worse_diffs = []
    curr_dist = calc_total_distance(curr_path, dist)
    
    for _ in range(100):
        new_path = random_two_opt(curr_path)
        new_dist = calc_total_distance(new_path, dist)
        diff = new_dist - curr_dist
        if diff > 0:
            worse_diffs.append(diff)
    
    ave_worse_diff = sum(worse_diffs) / len(worse_diffs)
    T0 = - ave_worse_diff / math.log(p0)
    return T0

def simulated_annealing(cities, dist, initial_path, n_iter=100000, cooling_rate=0.99):
    curr_path = initial_path
    curr_dist = calc_total_distance(curr_path, dist)
    best_path = curr_path
    best_dist = curr_dist
    T = calculate_initial_temperature(curr_path, dist)

    for i in range(n_iter):
        new_path = random_two_opt(curr_path)
        new_dist = calc_total_distance(new_path, dist)
        diff = new_dist - curr_dist

        if diff < 0 or random.random() < math.exp(-diff / T):
            curr_path = new_path
            curr_dist = new_dist
            if curr_dist < best_dist:
                best_path = curr_path
                best_dist = curr_dist
        T *= cooling_rate

    return best_path
  ```
### 結果:
```
Challenge 0
output_sa_greedy_2opt:    3291.62
output_sa_insertion_2opt:    3291.62
google-step-tsp/sample/sa:    3291.62

Challenge 1
output_sa_greedy_2opt:    3778.72
output_sa_insertion_2opt:    3778.72
google-step-tsp/sample/sa:    3778.72

Challenge 2
output_sa_greedy_2opt:    4927.64
output_sa_insertion_2opt:    4494.42
google-step-tsp/sample/sa:    4494.42

Challenge 3
output_sa_greedy_2opt:    8873.70
output_sa_insertion_2opt:    8485.97
google-step-tsp/sample/sa:    8150.91

Challenge 4
output_sa_greedy_2opt:   11489.79
output_sa_insertion_2opt:   11553.79
google-step-tsp/sample/sa:   10675.29

Challenge 5
output_sa_greedy_2opt:   21363.60
output_sa_insertion_2opt:   22283.20
google-step-tsp/sample/sa:   21119.55

Challenge 6
output_sa_greedy_2opt:   42712.37
output_sa_insertion_2opt:   44913.28
google-step-tsp/sample/sa:   44393.89
```
