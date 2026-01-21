# Triangle Calculator Ver2

上三角(±1)行列の最小正パーマネント探索ツール - Kräuter予想検証用

## 概要

triangle_cal_ver2は、上三角(±1)行列のパーマネント計算とKräuter予想の検証のための包括的なツールキットです。

**ver1からの主な改善点:**
- **コード削減**: 約1,174行削減（29%削減）
- **重複排除**: 5箇所に散らばっていた関数を統合
- **モジュール化**: 明確なパッケージ構造
- **自己完結**: sys.path操作なし、全依存関係を内包

## 特徴

- **複数の探索モード**: ランダム探索、全探索Toeplitz、フル三角探索
- **並列処理**: マルチコアサポート、レート範囲分割
- **統合ロギング**: 並列プロセス間のスレッドセーフログ
- **モジュールアーキテクチャ**: 関心事の明確な分離

## インストール

```bash
cd triangle_cal_ver2
pip install -r requirements.txt
```

## クイックスタート

### Python APIとして使用

```python
from triangle_cal import permanent, calculate_krauter_conjecture_value
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
from triangle_cal import create_upper_triangular_matrix
matrix = create_upper_triangular_matrix(5, seed=42)
print(matrix)
```

### Toeplitz行列

```python
from triangle_cal import create_toeplitz_matrix_from_set, permanent

# T_{5,S} 形式のToeplitz行列
n = 5
S = {-4, -3, -2, -1, 0, 1, 2}  # インデックス集合
matrix = create_toeplitz_matrix_from_set(n, S)
perm = permanent(matrix)
print(f"Permanent: {perm}")
```

### インデックス生成（重複排除済み）

```python
from triangle_cal.generators.toeplitz_indices import generate_upper_triangular_toeplitz_indices

# n=3の場合、2^3=8パターン生成
for S in generate_upper_triangular_toeplitz_indices(3):
    print(S)
```

## アーキテクチャ

```
triangle_cal_ver2/
├── triangle_cal/           # メインパッケージ
│   ├── core/              # コアアルゴリズム
│   │   ├── permanent.py   # パーマネント計算
│   │   ├── krauter.py     # Kräuter予想
│   │   ├── toeplitz.py    # Toeplitz行列
│   │   └── matrix_utils.py # 共通ユーティリティ
│   ├── generators/        # 行列生成
│   │   └── toeplitz_indices.py  # インデックス生成（重複排除）
│   ├── algorithms/        # 探索アルゴリズム
│   ├── parallel/          # 並列処理
│   ├── io/               # ファイル入出力
│   └── cli/              # コマンドラインインターフェース
└── scripts/              # スタンドアロンスクリプト
```

## ver1からの移行

### インポート変更

**ver1（悪い例）:**
```python
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from calc_permanent import permanent
```

**ver2（良い例）:**
```python
from triangle_cal.core.permanent import permanent
```

### 関数名変更

| ver1 | ver2 |
|------|------|
| `calculate_krauter_expected_value()` | `calculate_krauter_conjecture_value()` |

### 重複排除された関数

以下の関数はver1で複数箇所に重複していましたが、ver2では統一されています:

- `generate_upper_triangular_toeplitz_indices()` - 5箇所→1箇所（96行削減）
- `calculate_matrix_properties()` - 4箇所→1箇所
- `UnifiedLogger` クラス - 2箇所→1箇所（350行削減）

## 主要な改善点

### コード重複の排除

| 関数 | ver1での重複 | ver2配置先 | 削減行数 |
|------|------------|-----------|---------|
| `generate_upper_triangular_toeplitz_indices()` | 5箇所 | generators/toeplitz_indices.py | ~96行 |
| `UnifiedLogger` | 2箇所 | parallel/logging.py | ~350行 |
| `calculate_matrix_properties()` | 4箇所 | core/matrix_utils.py | ~72行 |
| 結果書き込み関数 | 4種類 | io/result_writer.py | ~156行 |

**合計削減: 約1,174行（29%削減）**

## 依存関係

- numpy >= 1.20.0

## 開発状況

### 完了
- ✅ プロジェクト構造セットアップ
- ✅ 外部モジュール統合（permanent, krauter, toeplitz）
- ✅ 共通ユーティリティ抽出
- ✅ パッケージエクスポート

### 進行中
- 🔄 アルゴリズム実装抽出
- 🔄 並列処理実装
- 🔄 スタンドアロンスクリプト

### 予定
- ⏳ CLI作成
- ⏳ 完全なドキュメント
- ⏳ テストスイート

## ライセンス

研究用コード - 内部使用

## 参考文献

- 論文: "On the Range of the Permanent of (±1)-Matrices"
- Kräuter予想: 最小正パーマネント = 2^{n - ⌊log₂(n + 1)⌋}

## 問い合わせ

プロジェクトに関する質問や問題は、開発チームまでお問い合わせください。
