"""
Hankelインデックス生成モジュール

Triangle Hankel行列のインデックス集合を生成します。

Triangle Hankel行列の定義:
    T[i,j] = h[i+j]  if i ≤ j  (上三角部分: Hankel構造)
    T[i,j] = 1       if i > j  (下三角部分: 固定値1)

上三角部分 (i ≤ j) でのインデックス i+j の範囲は 0 ≤ i+j ≤ 2n-2 なので、
h[k] (k=0,1,...,2n-2) の各値を独立に ±1 から選択できます。

したがって、総パターン数は 2^(2n-1) です。
"""

from itertools import combinations


def generate_upper_triangular_hankel_indices(n):
    """
    Triangle Hankel行列のインデックス集合Sを効率的に生成

    Triangle Hankel の条件:
    - 下三角部分 (i > j): T[i,j] = 1 (固定) → インデックスに依存しない
    - 上三角部分 (i ≤ j): T[i,j] = h[i+j] ∈ {±1} → 自由選択
      - i+j の範囲: 0 ≤ i+j ≤ 2n-2 (i,j ∈ [0,n-1], i≤j)

    Args:
        n: 行列のサイズ

    Yields:
        set: 各Hankelインデックス集合S (k ∈ S → h[k]=1, k ∉ S → h[k]=-1)

    Examples:
        >>> list(generate_upper_triangular_hankel_indices(3))
        # 2^5 = 32パターンを生成
        # インデックス範囲: {0, 1, 2, 3, 4}
        # 各パターン: {0..4の任意の部分集合}

        >>> patterns = list(generate_upper_triangular_hankel_indices(3))
        >>> len(patterns)
        32

        >>> # Pattern 0: 空集合 (全てのh[k]=-1)
        >>> patterns[0]
        set()

        >>> # Pattern 1: {0} のみ
        >>> patterns[1]
        {0}

        >>> # 最後のパターン: 全インデックス
        >>> patterns[-1]
        {0, 1, 2, 3, 4}

    Notes:
        - 総パターン数は 2^(2n-1)
        - Toeplitzと異なり必須インデックスは無い（全て自由選択）
        - n=3: 2^5=32, n=4: 2^7=128, n=5: 2^9=512, n=6: 2^11=2048
    """
    # Hankelインデックスの範囲: 0 ≤ k ≤ 2n-2
    hankel_indices = list(range(0, 2*n - 1))

    # 全ての部分集合を生成: 2^(2n-1) パターン
    for r in range(len(hankel_indices) + 1):
        for subset in combinations(hankel_indices, r):
            yield set(subset)
