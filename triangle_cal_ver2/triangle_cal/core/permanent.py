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
    Ryserの公式を使ってパーマネントを計算する（最適化版）
    計算量: O(2^n * n)
    Gray codeを使って行和を効率的に更新
    """
    if not isinstance(matrix, np.ndarray):
        matrix = np.array(matrix, dtype=np.int64)
    else:
        matrix = matrix.astype(np.int64)
    n = matrix.shape[0]
    if matrix.shape[1] != n:
        raise ValueError("行列は正方行列である必要があります")

    if verbose:
        print("\n=== パーマネント計算 (Ryserの公式) ===")
        print(f"行列サイズ: {n}×{n}")
        print(f"行列:\n{matrix}")

    # Gray codeを使った高速実装
    # row_sums[i] = i行目の選択された列の和
    row_sums = np.zeros(n, dtype=np.int64)
    total = 0
    sign = (-1) ** n  # 空集合の符号から開始

    for k in range(1, 2 ** n):
        # Gray codeで変化するビット位置を求める
        j = (k ^ (k - 1)).bit_length() - 1
        # k番目のGray codeでjビット目が1かどうか
        gray_k = k ^ (k >> 1)
        if gray_k & (1 << j):
            # j列を追加
            row_sums += matrix[:, j]
        else:
            # j列を削除
            row_sums -= matrix[:, j]

        # 行和の積を計算
        prod = np.prod(row_sums)
        # 符号を反転（列を1つ追加/削除するたびに符号が変わる）
        sign = -sign
        total += sign * prod

    if verbose:
        print(f"\nパーマネント = {total}")
    return int(total)


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
