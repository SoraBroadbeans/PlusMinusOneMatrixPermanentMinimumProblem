"""
行列ユーティリティモジュール

上三角行列に関する共通ユーティリティ関数を提供します。
"""

import numpy as np
import random


def convert_to_positive_s(S_original):
    """
    Sを正の値に変換

    Args:
        S_original: 元のS（負の値を含む可能性がある）

    Returns:
        tuple: (正のS, オフセット値)
    """
    if not S_original:
        return set(), 0

    min_val = min(S_original)
    offset = 1 - min_val if min_val <= 0 else 0
    S_positive = {s + offset for s in S_original}
    return S_positive, offset


def invert_s(S, n):
    """
    Sを反転（全体集合からSを引いたもの）

    Args:
        S: 元の集合
        n: 行列サイズ

    Returns:
        set: 反転されたS
    """
    all_diffs = set(range(-(n-1), n))
    return all_diffs - S


def create_upper_triangular_matrix(n, seed=None):
    """
    上三角型(±1)行列を作成（論文の定義に基づく）
    - 上三角部分（対角線より上, i < j）: ランダムに-1か1
    - 対角線（i = j）: ランダムに-1か1
    - 下三角部分（対角線より下, i > j）: すべて1

    Args:
        n: 行列のサイズ
        seed: ランダムシード（再現性のため）

    Returns:
        np.ndarray: nxnの上三角型(±1)行列
    """
    if seed is not None:
        random.seed(seed)

    matrix = np.ones((n, n), dtype=int)  # デフォルトを1で初期化

    # 上三角部分（対角線含む）をランダムに-1か1で設定
    for i in range(n):
        for j in range(i, n):
            matrix[i, j] = random.choice([-1, 1])

    # 下三角部分（i > j）はすでに1なのでそのまま

    return matrix


def calculate_matrix_properties(matrix):
    """
    行列の性質を計算

    Args:
        matrix: 2次元のnumpy配列

    Returns:
        dict: 行列の性質
    """
    n = len(matrix)
    total_elements = n * n
    ones_count = np.sum(matrix == 1)
    minus_ones_count = np.sum(matrix == -1)
    zeros_count = np.sum(matrix == 0)

    # 上三角部分の要素数
    upper_triangle_count = n * (n + 1) // 2

    return {
        'size': n,
        'total_elements': total_elements,
        'ones_count': ones_count,
        'minus_ones_count': minus_ones_count,
        'zeros_count': zeros_count,
        'ones_ratio': ones_count / total_elements,
        'upper_triangle_elements': upper_triangle_count
    }


def is_upper_triangular(matrix):
    """
    行列が上三角行列かどうかをチェック

    Args:
        matrix: 2次元のnumpy配列

    Returns:
        bool: 上三角行列の場合True
    """
    n = len(matrix)
    for i in range(n):
        for j in range(i):
            if matrix[i][j] != 1:
                return False
    return True
