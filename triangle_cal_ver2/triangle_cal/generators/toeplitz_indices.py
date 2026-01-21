"""
Toeplitzインデックス生成モジュール

上三角制約を満たすToeplitz行列のインデックス集合を生成します。

【重要】この実装は ver1 で5箇所に重複していた関数の正規実装です:
- triangle_cal_ver1/main.py (285-308行)
- triangle_cal_ver1/management.py (41-64行)
- triangle_cal_ver1/multi.py (405-428行)
- triangle_cal_ver1/multi_rate.py (410-433行)

約96行のコード重複を排除します。
"""

from itertools import combinations


def generate_upper_triangular_toeplitz_indices(n):
    """
    上三角制約を満たすToeplitz行列のインデックス集合Sを効率的に生成

    上三角行列の条件:
    - 下三角部分 (i > j) が1 → j-i < 0 → 負のインデックスがSに必須
    - 上三角+対角部分 (i ≤ j) は±1 → j-i ≥ 0 → 非負インデックスは自由選択

    Args:
        n: 行列のサイズ

    Yields:
        set: 各集合S（上三角制約を満たす）

    Examples:
        >>> list(generate_upper_triangular_toeplitz_indices(3))
        # 2^3 = 8パターンを生成
        # base_set = {-2, -1} (必須)
        # 各パターン: base_set | {0,1,2の部分集合}

    Notes:
        - 総パターン数は 2^n
        - ver1では以下のファイルに重複実装されていました:
            * main.py:285-308
            * management.py:41-64
            * multi.py:405-428
            * multi_rate.py:410-433
    """
    # 負のインデックスは必須（下三角を1にするため）
    base_set = set(range(-(n-1), 0))  # {-(n-1), -(n-2), ..., -1}

    # 非負インデックスの全ての部分集合を生成 {0, 1, 2, ..., n-1}
    non_negative_indices = list(range(0, n))

    # 2^n パターンを生成
    for r in range(len(non_negative_indices) + 1):
        for subset in combinations(non_negative_indices, r):
            yield base_set | set(subset)
