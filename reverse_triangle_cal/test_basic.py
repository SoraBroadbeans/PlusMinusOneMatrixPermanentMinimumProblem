#!/usr/bin/env python3
"""
reverse_triangle_cal 基本機能テスト
"""

from reverse_triangle_cal import (
    permanent,
    calculate_krauter_conjecture_value,
    create_upper_triangular_matrix,
    calculate_matrix_properties,
    create_hankel_matrix_from_set,
)
from reverse_triangle_cal.generators.hankel_indices import generate_upper_triangular_hankel_indices
import numpy as np

print("=" * 60)
print("reverse_triangle_cal 基本機能テスト")
print("=" * 60)

# Test 1: パーマネント計算
print("\n[Test 1] パーマネント計算")
matrix = np.array([[1, 1], [1, 1]])
perm = permanent(matrix)
print(f"Matrix:\n{matrix}")
print(f"Permanent: {perm}")
# Permanent = 1*1 + 1*1 = 2
assert perm == 2, f"Expected 2, got {perm}"
print("✓ Test 1 passed")

# Test 2: Kräuter予想値
print("\n[Test 2] Kräuter予想値")
expected_values = {
    3: 2,
    4: 4,
    5: 8,
    6: 16,
    7: 32,
    8: 64,
    9: 128,
    10: 128,
}
for n in range(3, 11):
    value = calculate_krauter_conjecture_value(n)
    expected = expected_values[n]
    assert value == expected, f"n={n}: expected {expected}, got {value}"
    print(f"n={n}: {value} (expected {expected}) ✓")
print("✓ Test 2 passed")

# Test 3: 上三角行列生成
print("\n[Test 3] 上三角行列生成")
matrix = create_upper_triangular_matrix(4, seed=123)
print(f"Matrix (n=4, seed=123):\n{matrix}")
props = calculate_matrix_properties(matrix)
print(f"Ones count: {props['ones_count']}, Ratio: {props['ones_ratio']:.2f}")

# 下三角部分が全て1であることを確認
for i in range(4):
    for j in range(i):
        assert matrix[i, j] == 1, f"Lower triangle violation at [{i},{j}]"
print("Lower triangle check: all 1s ✓")

perm = permanent(matrix)
print(f"Permanent: {perm}")
print("✓ Test 3 passed")

# Test 4: Triangle Hankel行列
print("\n[Test 4] Triangle Hankel行列")
n = 4
S = {0, 2, 4, 6}  # h[0]=1, h[1]=-1, h[2]=1, h[3]=-1, h[4]=1, h[5]=-1, h[6]=1
matrix = create_hankel_matrix_from_set(n, S)
print(f"H_{{{n},S}} with S={sorted(S)}:")
print(f"Hankel vector: h[k] = 1 if k∈S, -1 otherwise (k=0..{2*n-2})")
print(matrix)

# 検証: 下三角部分が全て1
for i in range(n):
    for j in range(i):
        assert matrix[i, j] == 1, f"Lower triangle violation at [{i},{j}]"
print("Lower triangle check: all 1s ✓")

# 検証: 上三角部分がHankel構造に従う
for k in range(2*n - 1):
    expected = 1 if k in S else -1
    for i in range(n):
        j = k - i
        if 0 <= j < n and i <= j:  # Upper triangle only
            actual = matrix[i, j]
            assert actual == expected, f"Hankel violation at [{i},{j}]: expected h[{k}]={expected}, got {actual}"
print("Upper triangle Hankel property check ✓")

# 具体的な要素の検証
print(f"\n検証: T[0,0] = h[0+0=0] = {'1 (0∈S)' if 0 in S else '-1 (0∉S)'}")
print(f"検証: T[0,1] = h[0+1=1] = {'1 (1∈S)' if 1 in S else '-1 (1∉S)'}")
print(f"検証: T[1,0] = 1 (下三角は固定)")
assert matrix[0, 0] == (1 if 0 in S else -1)
assert matrix[0, 1] == (1 if 1 in S else -1)
assert matrix[1, 0] == 1

perm = permanent(matrix)
print(f"Permanent: {perm}")
print("✓ Test 4 passed")

# Test 5: Hankelインデックス生成
print("\n[Test 5] Hankelインデックス生成")
n = 3
patterns = list(generate_upper_triangular_hankel_indices(n))
expected_count = 2 ** (2*n - 1)
print(f"n={n}, 総パターン数: {len(patterns)} (2^{2*n-1}={expected_count})")
assert len(patterns) == expected_count, f"Expected {expected_count}, got {len(patterns)}"
print(f"インデックス範囲: 0 to {2*n-2}")
print("最初の5パターン:")
for i, S in enumerate(patterns[:5]):
    matrix = create_hankel_matrix_from_set(n, S)
    perm = permanent(matrix)
    print(f"  {i+1}. S={str(sorted(S)):30s} → Permanent={perm}")
print("✓ Test 5 passed")

# Test 6: 具体例 - n=6の場合 (h[i+j] = (-1)^(i+j))
print("\n[Test 6] 具体例: n=6, h[k]=(-1)^k (偶数インデックスのみ)")
n = 6
S = {k for k in range(2*n-1) if k % 2 == 0}  # {0, 2, 4, 6, 8, 10}
matrix = create_hankel_matrix_from_set(n, S)
print(f"S = {sorted(S)} (偶数インデックス)")
print("\n期待される行列:")
print(" 1 -1  1 -1  1 -1")
print(" 1  1 -1  1 -1  1")
print(" 1  1  1 -1  1 -1")
print(" 1  1  1  1 -1  1")
print(" 1  1  1  1  1 -1")
print(" 1  1  1  1  1  1")
print("\n実際の行列:")
print(matrix)

expected = np.array([
    [ 1, -1,  1, -1,  1, -1],
    [ 1,  1, -1,  1, -1,  1],
    [ 1,  1,  1, -1,  1, -1],
    [ 1,  1,  1,  1, -1,  1],
    [ 1,  1,  1,  1,  1, -1],
    [ 1,  1,  1,  1,  1,  1]
])

assert np.array_equal(matrix, expected), "Matrix does not match expected"
print("✓ Matrix matches expected")

perm = permanent(matrix)
print(f"Permanent: {perm}")
print("✓ Test 6 passed")

# Test 7: パターン数検証 (n=4の場合)
print("\n[Test 7] パターン数検証 (n=4)")
n = 4
patterns = list(generate_upper_triangular_hankel_indices(n))
expected_count = 2 ** (2*n - 1)
actual_count = len(patterns)
print(f"n={n}, 期待パターン数: 2^{2*n-1} = {expected_count}")
print(f"実際のパターン数: {actual_count}")
assert actual_count == expected_count, f"Expected {expected_count}, got {actual_count}"
print("✓ Test 7 passed")

print("\n" + "=" * 60)
print("すべてのテストが完了しました！")
print("=" * 60)
