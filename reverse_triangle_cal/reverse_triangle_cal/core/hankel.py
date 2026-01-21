"""
Hankel行列モジュール

Triangle Hankel形式の(+1,-1)行列の生成とパーマネント計算

Triangle Hankel行列の定義:
    T[i,j] = h[i+j]  if i ≤ j  (上三角部分: Hankel構造)
    T[i,j] = 1       if i > j  (下三角部分: 固定値1)

where h[k] ∈ {±1} for k = 0, 1, 2, ..., 2n-2
"""

import numpy as np
import time
import re

from .permanent import permanent


def create_hankel_matrix_from_set(n, S):
    """
    Triangle Hankel形式の(+1,-1)行列を作成

    定義:
    - 上三角部分 (i ≤ j): T[i,j] = h[i+j]
      - (i+j) ∈ S のとき +1
      - (i+j) ∉ S のとき -1
    - 下三角部分 (i > j): T[i,j] = 1 (固定)

    Args:
        n: 行列のサイズ
        S: Hankelインデックス集合 (0 ≤ k ≤ 2n-2)

    Returns:
        np.ndarray: nxn Triangle Hankel行列

    Raises:
        ValueError: Sに無効なインデックスが含まれる場合

    Examples:
        >>> # n=3, S={0,2,4} → h[0]=1, h[1]=-1, h[2]=1, h[3]=-1, h[4]=1
        >>> matrix = create_hankel_matrix_from_set(3, {0, 2, 4})
        >>> # T[0,0]=h[0]=1, T[0,1]=h[1]=-1, T[0,2]=h[2]=1
        >>> # T[1,0]=1 (lower), T[1,1]=h[2]=1, T[1,2]=h[3]=-1
        >>> # T[2,0]=1 (lower), T[2,1]=1 (lower), T[2,2]=h[4]=1
        >>> print(matrix)
        [[ 1 -1  1]
         [ 1  1 -1]
         [ 1  1  1]]
    """
    # インデックス範囲の検証
    max_valid_index = 2*n - 2
    invalid_indices = [k for k in S if k < 0 or k > max_valid_index]
    if invalid_indices:
        raise ValueError(
            f"Hankelインデックスは 0 ≤ k ≤ {max_valid_index} の範囲です。"
            f"無効なインデックス: {invalid_indices}"
        )

    # デフォルトを1に初期化（下三角部分用）
    matrix = np.ones((n, n), dtype=int)

    # 上三角部分 (i ≤ j) のみHankel定義を適用
    for i in range(n):
        for j in range(i, n):  # j >= i (upper triangle including diagonal)
            if (i + j) in S:
                matrix[i, j] = 1
            else:
                matrix[i, j] = -1

    # 下三角部分 (i > j) はすでに1なのでそのまま

    return matrix


def calculate_hankel_permanent_from_set(n, S, verbose=False):
    """
    Triangle Hankel形式の行列のパーマネントを計算

    Args:
        n: 行列のサイズ
        S: Hankelインデックス集合 (0 ≤ k ≤ 2n-2)
        verbose: 詳細出力フラグ

    Returns:
        tuple: (パーマネント値, 計算時間)
    """
    start_time = time.time()

    matrix = create_hankel_matrix_from_set(n, S)

    if verbose:
        print(f"Triangle Hankel行列 (n={n}):")
        print(f"S = {sorted(S)}")
        print(f"行列:\n{matrix}")

    perm_calculation_start = time.time()
    perm_value = permanent(matrix, method='ryser', verbose=verbose)
    perm_calculation_time = time.time() - perm_calculation_start

    total_time = time.time() - start_time

    if verbose:
        print(f"パーマネント値: {perm_value}")
        print(f"パーマネント計算時間: {perm_calculation_time:.6f}秒")
        print(f"総計算時間: {total_time:.6f}秒")

    return perm_value, total_time


def parse_hankel_set_notation(notation):
    """
    H_{n,S} 形式の記法を解析する

    Args:
        notation: "H_6{0,2,4..10}" のような記法文字列

    Returns:
        tuple: (n, S) - nは行列サイズ、Sは集合 (0 ≤ k ≤ 2n-2)

    Raises:
        ValueError: 記法が無効な場合

    Examples:
        >>> parse_hankel_set_notation("H_6{0,2,4..10}")
        (6, {0, 2, 4, 5, 6, 7, 8, 9, 10})
        >>> parse_hankel_set_notation("H_3{0,2,4}")
        (3, {0, 2, 4})
    """
    # H_{n}{...} または H_n{...} の形式をパース
    match = re.match(r'H_\{?(\d+)\}?\{([^}]+)\}', notation)
    if not match:
        raise ValueError(f"無効なHankel記法です: {notation}")

    n = int(match.group(1))
    set_content = match.group(2).strip()

    S = set()

    # カンマで分割して各要素を処理
    elements = [elem.strip() for elem in set_content.split(',')]

    for elem in elements:
        # 範囲記法 (例: 0..10, 2..5)
        range_match = re.match(r'(\d+)\.\.(\d+)', elem)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if end < start:
                raise ValueError(f"範囲が無効です: {start}..{end}")
            # Hankelでは負の値は使わない (0 ≤ k ≤ 2n-2)
            max_valid = 2*n - 2
            if start < 0 or end > max_valid:
                raise ValueError(f"Hankelインデックスは 0 ≤ k ≤ {max_valid} の範囲です")
            S.update(range(start, end + 1))
        else:
            # 単一の数値
            try:
                val = int(elem)
                max_valid = 2*n - 2
                if val < 0 or val > max_valid:
                    raise ValueError(f"Hankelインデックスは 0 ≤ k ≤ {max_valid} の範囲です")
                S.add(val)
            except ValueError:
                raise ValueError(f"無効な集合要素です: {elem}")

    return n, S
