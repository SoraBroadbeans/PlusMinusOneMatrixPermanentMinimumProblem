#!/usr/bin/env python3
"""
triangle_cal_ver2 基本機能テスト
"""

from triangle_cal import (
    permanent,
    calculate_krauter_conjecture_value,
    create_upper_triangular_matrix,
    calculate_matrix_properties,
    create_toeplitz_matrix_from_set,
)
from triangle_cal.generators.toeplitz_indices import generate_upper_triangular_toeplitz_indices
import numpy as np

print("=" * 60)
print("triangle_cal_ver2 基本機能テスト")
print("=" * 60)

# Test 1: パーマネント計算
print("\n[Test 1] パーマネント計算")
matrix = np.array([[1, -1], [1, 1]])
perm = permanent(matrix)
print(f"Matrix:\n{matrix}")
print(f"Permanent: {perm}")

# Test 2: Kräuter予想値
print("\n[Test 2] Kräuter予想値")
for n in range(3, 11):
    value = calculate_krauter_conjecture_value(n)
    print(f"n={n}: {value}")

# Test 3: 上三角行列生成
print("\n[Test 3] 上三角行列生成")
matrix = create_upper_triangular_matrix(4, seed=123)
print(f"Matrix (n=4, seed=123):\n{matrix}")
props = calculate_matrix_properties(matrix)
print(f"Ones count: {props['ones_count']}, Ratio: {props['ones_ratio']:.2f}")
perm = permanent(matrix)
print(f"Permanent: {perm}")

# Test 4: Toeplitz行列
print("\n[Test 4] Toeplitz行列")
n = 4
S = {-3, -2, -1, 0, 1}
matrix = create_toeplitz_matrix_from_set(n, S)
print(f"T_{{{n},S}} with S={sorted(S)}:")
print(matrix)
perm = permanent(matrix)
print(f"Permanent: {perm}")

# Test 5: Toeplitzインデックス生成（重複排除済み！）
print("\n[Test 5] Toeplitzインデックス生成（ver1で5箇所に重複していた関数）")
n = 3
patterns = list(generate_upper_triangular_toeplitz_indices(n))
print(f"n={n}, 総パターン数: {len(patterns)} (2^{n}={2**n})")
print("最初の5パターン:")
for i, S in enumerate(patterns[:5]):
    matrix = create_toeplitz_matrix_from_set(n, S)
    perm = permanent(matrix)
    print(f"  {i+1}. S={str(sorted(S)):30s} → Permanent={perm}")

print("\n" + "=" * 60)
print("すべてのテストが完了しました！")
print("=" * 60)
