# Reverse Triangle Calculator (Triangle Hankel)

Triangle Hankel行列の最小正パーマネント探索ツール - Kräuter予想検証用

## 概要

reverse_triangle_calは、Triangle Hankel行列のパーマネント計算とKräuter予想の検証のための包括的なツールキットです。

**Triangle Hankel行列の定義:**
```
T[i,j] = h[i+j]  if i ≤ j  (上三角部分: Hankelインデックス使用)
T[i,j] = 1       if i > j  (下三角部分: 固定値1)
```

ここで、h[k] ∈ {±1} for k = 0, 1, 2, ..., 2n-2

**triangle_cal_ver2からの主な違い:**

| 特性 | triangle_cal_ver2 (Toeplitz) | reverse_triangle_cal (Hankel) |
|------|------------------------------|-------------------------------|
| 行列型 | Upper Triangular Toeplitz | Triangle Hankel |
| インデックス公式 | T[i,j] = f(j-i) | T[i,j] = h[i+j] (i≤j) |
| 定数パターン | 対角線方向 | 反対角線方向 |
| インデックス範囲 | {-(n-1), ..., n-1} | {0, ..., 2n-2} |
| 必須インデックス | {-(n-1), ..., -1} | なし (全て自由選択) |
| 探索空間 | 2^n | 2^(2n-1) |
| 対称性 | 非対称 | 非対称 (上三角のみHankel) |

## Triangle Hankel行列の数学的性質

### 定義と制約

Triangle Hankel行列 T は以下を満たす:

1. **上三角部分 (i ≤ j)**:
   - `T[i,j] = h[i+j]` where `h[k] ∈ {±1}`, `k ∈ {0, 1, ..., 2n-2}`
   - 反対角線上の要素が等しい (Hankel性質)

2. **下三角部分 (i > j)**:
   - `T[i,j] = 1` (固定)

### 探索空間

| n | インデックス数 (2n-1) | パターン数 (2^(2n-1)) | 計算量目安 |
|---|---------------------|---------------------|----------|
| 3 | 5                   | 32                  | 瞬時    |
| 4 | 7                   | 128                 | 瞬時    |
| 5 | 9                   | 512                 | < 1秒   |
| 6 | 11                  | 2,048               | 数秒    |
| 7 | 13                  | 8,192               | 数十秒  |
| 8 | 15                  | 32,768              | 数分    |

### 例: n=3

**Hankelインデックス範囲**: {0, 1, 2, 3, 4}

**行列構造**:
```
     j=0  j=1  j=2
i=0  h[0] h[1] h[2]
i=1   1   h[2] h[3]
i=2   1    1   h[4]
```

**具体例**: S = {0, 2, 4} → h[0]=1, h[1]=-1, h[2]=1, h[3]=-1, h[4]=1
```
 1  -1   1
 1   1  -1
 1   1   1
```

### 例: n=6 (h[k] = (-1)^k)

**S = {0, 2, 4, 6, 8, 10}** (偶数インデックス)

```
 1 -1  1 -1  1 -1
 1  1 -1  1 -1  1
 1  1  1 -1  1 -1
 1  1  1  1 -1  1
 1  1  1  1  1 -1
 1  1  1  1  1  1
```

## インストール

```bash
cd reverse_triangle_cal
pip install -r requirements.txt
```

## クイックスタート

### Python APIとして使用

```python
from reverse_triangle_cal import permanent, calculate_krauter_conjecture_value
import numpy as np

# パーマネント計算
matrix = np.array([[1, -1], [1, 1]])
perm = permanent(matrix)
print(f"Permanent: {perm}")

# Kräuter予想値
n = 10
expected = calculate_krauter_conjecture_value(n)
print(f"Expected minimum for n={n}: {expected}")

# 上三角行列生成
from reverse_triangle_cal import create_upper_triangular_matrix
matrix = create_upper_triangular_matrix(5, seed=42)
print(matrix)
```

### Triangle Hankel行列

```python
from reverse_triangle_cal import create_hankel_matrix_from_set, permanent

# H_{n,S} 形式のTriangle Hankel行列
n = 6
S = {0, 2, 4, 6, 8, 10}  # 偶数インデックス → h[k] = (-1)^k
matrix = create_hankel_matrix_from_set(n, S)
perm = permanent(matrix)
print(f"Permanent: {perm}")

# 期待される行列 (h[k] = (-1)^k):
#  1 -1  1 -1  1 -1
#  1  1 -1  1 -1  1
#  1  1  1 -1  1 -1
#  1  1  1  1 -1  1
#  1  1  1  1  1 -1
#  1  1  1  1  1  1
```

### Hankelインデックス生成

```python
from reverse_triangle_cal.generators.hankel_indices import generate_upper_triangular_hankel_indices

# n=3の場合、2^5=32パターン生成
for S in generate_upper_triangular_hankel_indices(3):
    print(S)
    # 出力例: set(), {0}, {1}, {0, 1}, {2}, ...
```

### メインスクリプトの実行

```bash
cd reverse_triangle_cal
python main.py
```

入力例:
```
行列サイズ n を入力してください: 3
```

出力:
```
=== 探索情報 ===
行列サイズ: n = 3
制約条件: Triangle Hankel (上三角はHankel, 下三角は1)
総パターン数: 32 (2^5)
Hankelインデックス範囲: 0 ≤ k ≤ 4
Kräuter予想値: 2
```

### テストの実行

```bash
cd reverse_triangle_cal
python test_basic.py
```

## アーキテクチャ

```
reverse_triangle_cal/
├── reverse_triangle_cal/      # メインパッケージ
│   ├── core/                  # コアアルゴリズム
│   │   ├── permanent.py       # パーマネント計算 (共通)
│   │   ├── krauter.py         # Kräuter予想 (共通)
│   │   ├── hankel.py          # Triangle Hankel行列 (NEW)
│   │   └── matrix_utils.py    # 共通ユーティリティ (共通)
│   ├── generators/            # 行列生成
│   │   └── hankel_indices.py  # Hankelインデックス生成 (NEW)
│   ├── algorithms/            # 探索アルゴリズム
│   ├── parallel/              # 並列処理
│   ├── io/                    # ファイル入出力
│   └── cli/                   # コマンドラインインターフェース
├── main.py                    # メインスクリプト
├── test_basic.py              # 基本機能テスト
├── README.md                  # このファイル
├── requirements.txt           # 依存関係
└── result/                    # 結果出力ディレクトリ
```

## API リファレンス

### Core モジュール

#### `create_hankel_matrix_from_set(n, S)`
Triangle Hankel行列を生成します。

**引数:**
- `n` (int): 行列のサイズ
- `S` (set): Hankelインデックス集合 (0 ≤ k ≤ 2n-2)

**戻り値:**
- `np.ndarray`: nxn Triangle Hankel行列

**例:**
```python
matrix = create_hankel_matrix_from_set(3, {0, 2, 4})
```

#### `calculate_hankel_permanent_from_set(n, S, verbose=False)`
Triangle Hankel行列のパーマネントを計算します。

**引数:**
- `n` (int): 行列のサイズ
- `S` (set): Hankelインデックス集合
- `verbose` (bool): 詳細出力フラグ

**戻り値:**
- `tuple`: (パーマネント値, 計算時間)

#### `permanent(matrix, method='ryser', verbose=False)`
行列のパーマネントを計算します。

**引数:**
- `matrix` (np.ndarray): n×n行列
- `method` (str): 'naive' または 'ryser'（デフォルト: 'ryser'）
- `verbose` (bool): 詳細出力フラグ

**戻り値:**
- `int`: パーマネント値

#### `calculate_krauter_conjecture_value(n)`
Kräuter予想による理論値を計算します。

**公式:** `2^{n - ⌊log₂(n + 1)⌋}`

**引数:**
- `n` (int): 行列のサイズ

**戻り値:**
- `int`: Kräuter予想値

### Generators モジュール

#### `generate_upper_triangular_hankel_indices(n)`
Triangle Hankel行列の全インデックス集合を生成します。

**引数:**
- `n` (int): 行列のサイズ

**Yields:**
- `set`: Hankelインデックス集合 (総パターン数: 2^(2n-1))

**例:**
```python
for S in generate_upper_triangular_hankel_indices(3):
    matrix = create_hankel_matrix_from_set(3, S)
    perm = permanent(matrix)
```

## 依存関係

- numpy >= 1.20.0

## 開発状況

### 完了
- ✅ プロジェクト構造セットアップ
- ✅ Triangle Hankel行列実装
- ✅ Hankelインデックス生成
- ✅ パッケージエクスポート
- ✅ メインスクリプト
- ✅ テストスイート
- ✅ ドキュメント

## ライセンス

Research Project

## 作者

Research Team
