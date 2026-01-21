"""
テプリッツ行列生成専用モジュール
Kräuter予想の検証のためのテプリッツ行列生成機能
"""

import numpy as np
from itertools import combinations, chain
import sys
import os
import random
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from calc_permanent import permanent
except ImportError:
    print("Error: calc_permanent module not found")
    sys.exit(1)


def generate_toeplitz_matrix(n, S):
    """
    テプリッツ行列 T_{n,S} を生成
    
    Args:
        n: 行列のサイズ
        S: 差分集合 (j-i ∈ S なら +1、そうでなければ -1)
        
    Returns:
        numpy.ndarray: n×n テプリッツ行列
    """
    matrix = -np.ones((n, n), dtype=int)  # デフォルトを-1に変更
    
    for i in range(n):
        for j in range(n):
            if (j - i) in S:
                matrix[i, j] = 1  # S内の要素では+1に変更
    
    return matrix

def generate_all_toeplitz_matrices(n, strategy="all", num_samples=None, max_time=None):
    """
    指定された戦略でテプリッツ行列を生成
    
    Args:
        n: 行列のサイズ
        strategy: 生成戦略
            - "all": すべての集合Sを試す
            - "symmetric": S = -S の対称集合のみ
            - "sparse": |S| ≤ n の小さい集合のみ
            - "continuous": 連続区間のみ
            - "random": ランダムサンプリング
        num_samples: random戦略での生成する行列数
        max_time: random戦略での最大実行時間（秒）
    
    Returns:
        list: (matrix, S) のタプルのリスト
    """
    # 可能な差分の範囲: -(n-1) から (n-1)
    possible_diffs = list(range(-(n-1), n))
    matrices = []
    
    if strategy == "all":
        # 全ての部分集合を生成 (2^(2n-1) 個)
        total_subsets = 2 ** len(possible_diffs)
        print(f"全テプリッツ行列パターン数: {total_subsets:,}")
        
        for i in range(total_subsets):
            S = set()
            for j, diff in enumerate(possible_diffs):
                if (i >> j) & 1:
                    S.add(diff)
            
            matrix = generate_toeplitz_matrix(n, S)
            matrices.append((matrix, S))
            
            if len(matrices) % 10000 == 0:
                print(f"生成済み: {len(matrices):,}/{total_subsets:,}")
    
    elif strategy == "symmetric":
        # 対称集合のみ生成
        symmetric_sets = generate_symmetric_sets(possible_diffs)
        print(f"対称テプリッツ行列パターン数: {len(symmetric_sets):,}")
        
        for S in symmetric_sets:
            matrix = generate_toeplitz_matrix(n, S)
            matrices.append((matrix, S))
    
    elif strategy == "sparse":
        # |S| ≤ n の小さい集合のみ
        for size in range(n + 1):
            for S in combinations(possible_diffs, size):
                S_set = set(S)
                matrix = generate_toeplitz_matrix(n, S_set)
                matrices.append((matrix, S_set))
        
        print(f"スパーステプリッツ行列数: {len(matrices):,}")
    
    elif strategy == "continuous":
        # 連続区間の集合のみ
        for start in range(-(n-1), n):
            for end in range(start, n):
                S = set(range(start, end + 1))
                matrix = generate_toeplitz_matrix(n, S)
                matrices.append((matrix, S))
        
        print(f"連続テプリッツ行列数: {len(matrices):,}")
    
    elif strategy == "random":
        # ランダムサンプリング
        return generate_random_toeplitz_matrices(n, num_samples, max_time)
    
    return matrices


def generate_random_toeplitz_matrices(n, num_samples=10000, max_time=None):
    """
    ランダムサンプリングでテプリッツ行列を生成
    
    Args:
        n: 行列のサイズ
        num_samples: 生成する行列数の上限（Noneで無制限）
        max_time: 最大実行時間（秒、Noneで無制限）
        
    Returns:
        generator: (matrix, S) のタプルを返すジェネレータ
    """
    possible_diffs = list(range(-(n-1), n))
    generated_sets = set()
    
    start_time = time.time()
    count = 0
    
    print(f"ランダムサンプリング開始 (n={n})")
    if num_samples:
        print(f"目標サンプル数: {num_samples:,}")
    if max_time:
        print(f"最大実行時間: {max_time}秒")
    
    while True:
        # 時間制限のチェック
        if max_time and (time.time() - start_time) > max_time:
            print(f"時間制限に達しました。生成数: {count:,}")
            break
            
        # サンプル数制限のチェック  
        if num_samples and count >= num_samples:
            print(f"目標サンプル数に達しました。生成数: {count:,}")
            break
        
        # ランダムに集合Sを生成
        S = set()
        for diff in possible_diffs:
            if random.random() < 0.5:  # 各差分を50%の確率で含める
                S.add(diff)
        
        # 重複チェック（メモリ効率のため一定数で制限）
        S_tuple = tuple(sorted(S))
        if len(generated_sets) < 100000:  # メモリ制限
            if S_tuple in generated_sets:
                continue
            generated_sets.add(S_tuple)
        
        # 行列生成
        matrix = generate_toeplitz_matrix(n, S)
        
        count += 1
        if count % 1000 == 0:
            elapsed = time.time() - start_time
            print(f"生成済み: {count:,}, 経過時間: {elapsed:.1f}秒")
            
        yield (matrix, S)


def generate_symmetric_sets(possible_diffs):
    """
    対称集合 S = -S を生成
    """
    # 0を含むかどうかで場合分け
    symmetric_sets = []
    
    # 正の差分のみ考慮
    positive_diffs = [d for d in possible_diffs if d > 0]
    
    # 0を含まない対称集合
    for size in range(len(positive_diffs) + 1):
        for pos_subset in combinations(positive_diffs, size):
            S = set(pos_subset) | set(-d for d in pos_subset)
            symmetric_sets.append(S)
    
    # 0を含む対称集合
    for size in range(len(positive_diffs) + 1):
        for pos_subset in combinations(positive_diffs, size):
            S = {0} | set(pos_subset) | set(-d for d in pos_subset)
            symmetric_sets.append(S)
    
    return symmetric_sets


def analyze_toeplitz_patterns(matrices_with_sets):
    """
    テプリッツ行列のパターンを分析
    """
    print(f"\n=== テプリッツ行列パターン分析 ===")
    print(f"総行列数: {len(matrices_with_sets):,}")
    
    # 集合サイズの分布
    size_distribution = {}
    for matrix, S in matrices_with_sets:
        size = len(S)
        size_distribution[size] = size_distribution.get(size, 0) + 1
    
    print(f"\n集合サイズの分布:")
    for size in sorted(size_distribution.keys()):
        count = size_distribution[size]
        print(f"  |S| = {size}: {count:,} 個")
    
    # サンプル行列の表示
    print(f"\nサンプル行列 (最初の5個):")
    for i, (matrix, S) in enumerate(matrices_with_sets[:5]):
        print(f"\n{i+1}. S = {sorted(S) if S else '∅'}")
        print(matrix)


def get_toeplitz_info(n, strategy="all", num_samples=None):
    """
    指定された戦略でのテプリッツ行列数を計算
    """
    possible_diffs_count = 2 * n - 1
    
    if strategy == "all":
        return 2 ** possible_diffs_count
    elif strategy == "symmetric":
        # 概算: 2^n (正の差分の選び方) × 2 (0の有無)
        positive_count = n - 1
        return 2 ** (positive_count + 1)
    elif strategy == "sparse":
        # |S| ≤ n の組み合わせ数
        from math import comb
        return sum(comb(possible_diffs_count, k) for k in range(n + 1))
    elif strategy == "continuous":
        # 連続区間の数: 区間の始点と終点の組み合わせ
        return possible_diffs_count * (possible_diffs_count + 1) // 2
    elif strategy == "random":
        # ランダムサンプリングでは指定されたサンプル数を返す
        return num_samples if num_samples else 10000
    
    return 0