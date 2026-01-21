"""
パーマネント計算モジュール

行列のパーマネントを計算するための関数を提供します。
- permanent_naive: 愚直な定義による計算 O(n!)
- permanent_ryser: Ryserの公式による効率的な計算 O(2^n * n)
- permanent: メソッド選択可能なメイン関数
"""

import numpy as np
from itertools import permutations


def permanent_naive(matrix, verbose=False):
    """
    行列のパーマネントを愚直な定義で計算する
    計算量: O(n!)
    """
    if not isinstance(matrix, np.ndarray):
        matrix = np.array(matrix)

    n = matrix.shape[0]
    if matrix.shape[1] != n:
        raise ValueError("行列は正方行列である必要があります")

    if verbose:
        print("\n=== パーマネント計算 (愚直な方法) ===")
        print(f"行列サイズ: {n}×{n}")
        print(f"行列:\n{matrix}")
        print("\n各順列での計算:")

    perm_sum = 0
    for perm_idx, perm in enumerate(permutations(range(n))):
        product = 1
        terms = []
        for i in range(n):
            value = matrix[i, perm[i]]
            product *= value
            terms.append(f"M[{i},{perm[i]}]={value}")

        if verbose:
            print(f"順列 {perm_idx+1}: {perm} → {' × '.join(terms)} = {product}")

        perm_sum += product

    if verbose:
        print(f"\nパーマネント = {perm_sum}")

    return perm_sum


def permanent_ryser(matrix, verbose=False):
    """
    Ryserの公式を使ってパーマネントを計算する（正しい実装）
    計算量: O(2^n * n)
    """
    if not isinstance(matrix, np.ndarray):
        matrix = np.array(matrix)
    n = matrix.shape[0]
    if matrix.shape[1] != n:
        raise ValueError("行列は正方行列である必要があります")

    if verbose:
        print("\n=== パーマネント計算 (Ryserの公式) ===")
        print(f"行列サイズ: {n}×{n}")
        print(f"行列:\n{matrix}")

    total = 0
    for subset in range(1, 2 ** n):  # 空集合は除く
        S = [(subset >> j) & 1 for j in range(n)]
        subset_indices = [j for j in range(n) if S[j] == 1]
        prod = 1
        for i in range(n):
            row_sum = int(sum(int(matrix[i, j]) for j in subset_indices))
            prod *= row_sum
        sign = (-1) ** (n - len(subset_indices))
        total += sign * prod
    if verbose:
        print(f"\nパーマネント = {total}")
    return total


def permanent(matrix, method='ryser', verbose=False):
    """
    行列のパーマネントを計算する

    引数:
        matrix: 正方行列（リストのリストまたはnumpy配列）
        method: 'naive'または'ryser'（デフォルト: 'ryser'）
        verbose: 計算手順を出力するかどうか（デフォルト: False）

    戻り値:
        行列のパーマネント
    """
    if method == 'naive':
        return permanent_naive(matrix, verbose)
    elif method == 'ryser':
        return permanent_ryser(matrix, verbose)
    else:
        raise ValueError("メソッドは'naive'または'ryser'である必要があります")


def is_pm_one_matrix(matrix):
    """
    行列が+1と-1の値のみを含むかチェックする
    """
    if not isinstance(matrix, np.ndarray):
        matrix = np.array(matrix)

    unique_vals = np.unique(matrix)
    return set(unique_vals).issubset({-1, 1})
