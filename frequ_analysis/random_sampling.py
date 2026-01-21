#!/usr/bin/env python3
"""
ランダム行列のperm/det計算スクリプト（対話形式）

ランダムな±1行列を生成し、permanentまたはdeterminantを計算する。

使用法:
    python random_sampling.py

対話形式で以下を入力:
    - 行列サイズ n
    - 試行回数 N
    - 行列タイプ: full, upper, toeplitz
    - 計算モード: perm, det
"""

import numpy as np
import sys
import os
from datetime import datetime
from collections import Counter

# src/calc_permanent.py をインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from calc_permanent import permanent, determinant


def generate_full_random(n):
    """
    全要素ランダムな±1行列を生成
    """
    return np.random.choice([1, -1], size=(n, n))


def generate_upper_random(n):
    """
    下三角は+1固定、上三角（対角含む）をランダムに±1で生成
    """
    matrix = np.ones((n, n), dtype=int)
    for i in range(n):
        for j in range(i, n):  # 対角含む上三角
            matrix[i, j] = np.random.choice([1, -1])
    return matrix


def generate_toeplitz_upper(n):
    """
    下三角は+1固定、上三角はToeplitz構造
    （同一対角線上は同じ値、各対角線の値をランダム決定）
    """
    matrix = np.ones((n, n), dtype=int)
    # 対角線は n 本（k=0が主対角、k=1,2,...,n-1が上方対角）
    diag_values = [np.random.choice([1, -1]) for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            k = j - i  # 対角線番号
            matrix[i, j] = diag_values[k]
    return matrix


def get_matrix_generator(matrix_type):
    """
    matrix_type に応じた行列生成関数を返す
    """
    generators = {
        'full': generate_full_random,
        'upper': generate_upper_random,
        'toeplitz': generate_toeplitz_upper,
    }
    if matrix_type not in generators:
        raise ValueError(f"matrix_type は 'full', 'upper', 'toeplitz' のいずれかである必要があります: {matrix_type}")
    return generators[matrix_type]


def calculate_ones_ratio(matrix):
    """
    行列内の+1の割合を計算
    """
    return np.sum(matrix == 1) / matrix.size


def create_output_filepaths(n, N, matrix_type, calc_mode):
    """
    出力ファイルのパスを生成（.md と .csv の両方）
    result/{n}/ フォルダに保存

    Returns
    -------
    tuple
        (md_path, csv_path)
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_dir = os.path.join(script_dir, 'result', str(n))
    os.makedirs(result_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%m%d_%H_%M")
    base_name = f"random_{matrix_type}_{n}_{N}_{timestamp}"
    md_path = os.path.join(result_dir, f"{base_name}.md")
    csv_path = os.path.join(result_dir, f"{base_name}_freq.csv")
    return md_path, csv_path


def run_sampling(n, N, calc_mode, matrix_type):
    """
    N回のランダムサンプリングを実行し、結果をMarkdownとCSVに保存
    """
    generator = get_matrix_generator(matrix_type)
    md_path, csv_path = create_output_filepaths(n, N, matrix_type, calc_mode)

    print(f"=== ランダムサンプリング開始 ===")
    print(f"行列サイズ: {n}×{n}")
    print(f"試行回数: {N}")
    print(f"計算モード: {calc_mode}")
    print(f"行列タイプ: {matrix_type}")
    print(f"出力先 (MD) : {md_path}")
    print(f"出力先 (CSV): {csv_path}")
    print()

    # 開始時刻を記録
    start_time = datetime.now()

    # 頻度カウント用
    value_counts = Counter()

    # プログレス表示の間隔
    progress_interval = max(1, N // 10)

    for i in range(N):
        matrix = generator(n)

        if calc_mode == 'perm':
            value = permanent(matrix, method='ryser')
        else:
            value = determinant(matrix)

        # 頻度をカウント
        value_counts[value] += 1

        # プログレス表示
        if (i + 1) % progress_interval == 0 or i == 0:
            progress = (i + 1) / N * 100
            print(f"進捗: {i + 1}/{N} ({progress:.1f}%)")

    # 終了時刻を記録
    end_time = datetime.now()
    elapsed_seconds = (end_time - start_time).total_seconds()

    print()
    print(f"完了!")

    # 結果をMarkdownに出力
    write_result_md(md_path, n, N, matrix_type, calc_mode, value_counts,
                    start_time, end_time, elapsed_seconds)

    # 結果をCSVに出力
    write_result_csv(csv_path, calc_mode, value_counts)

    return md_path, csv_path


def write_result_md(filepath, n, N, matrix_type, calc_mode, value_counts,
                    start_time, end_time, elapsed_seconds):
    """
    結果をMarkdownファイルに出力
    """
    value_col_name = "perm" if calc_mode == 'perm' else "det"

    # 頻度の多い順にソート
    sorted_counts = value_counts.most_common()

    with open(filepath, 'w', encoding='utf-8') as f:
        # タイトル
        f.write("# ランダムサンプリング結果\n\n")

        # 設定情報セクション
        f.write("## 1. 設定情報\n")
        f.write("| 項目 | 値 |\n")
        f.write("|------|-----|\n")
        f.write(f"| 行列サイズ (n) | {n} |\n")
        f.write(f"| 試行回数 (N) | {N} |\n")
        f.write(f"| 行列タイプ | {matrix_type} |\n")
        f.write(f"| 計算モード | {calc_mode} |\n")
        f.write(f"| パターン数 | {len(value_counts)} |\n\n")

        # 計算時間セクション
        f.write("## 2. 計算時間\n")
        f.write("| 項目 | 値 |\n")
        f.write("|------|-----|\n")
        f.write(f"| 開始時刻 | {start_time.strftime('%Y-%m-%d %H:%M:%S')} |\n")
        f.write(f"| 終了時刻 | {end_time.strftime('%Y-%m-%d %H:%M:%S')} |\n")
        f.write(f"| 経過時間 | {elapsed_seconds:.1f} 秒 |\n\n")

        # 結果セクション（CSV形式）
        f.write("## 3. 結果\n")
        f.write(f"{value_col_name},頻度\n")
        for value, count in sorted_counts:
            f.write(f"{value},{count}\n")

    print(f"結果Markdown: {filepath}")
    print(f"  ユニークな値の数: {len(value_counts)}")
    print(f"  上位5件:")
    for value, count in sorted_counts[:5]:
        print(f"    {value}: {count}")


def write_result_csv(filepath, calc_mode, value_counts):
    """
    結果をCSVファイルに出力（頻度分析用）
    """
    value_col_name = "permの値" if calc_mode == 'perm' else "detの値"

    # 値でソート（昇順）
    sorted_counts = sorted(value_counts.items(), key=lambda x: x[0])

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{value_col_name},頻度\n")
        for value, count in sorted_counts:
            f.write(f"{value},{count}\n")

    print(f"結果CSV: {filepath}")


def main():
    """
    メイン関数（対話形式）
    """
    print("=== ランダム行列のperm/det計算 ===")
    print("ランダムな±1行列を生成し、perm/detを計算します。\n")

    # 行列サイズ入力
    try:
        n = int(input("行列サイズ n を入力してください: "))
        if n < 1:
            print("エラー: nは1以上の整数である必要があります")
            sys.exit(1)
    except ValueError:
        print("エラー: 有効な整数を入力してください")
        sys.exit(1)

    # パターン数を表示
    full_patterns = 2 ** (n * n)
    upper_patterns = 2 ** (n * (n + 1) // 2)
    toeplitz_patterns = 2 ** n
    print(f"\n=== n={n} でのパターン数 ===")
    print(f"  full    : 2^{n*n} = {full_patterns:,}")
    print(f"  upper   : 2^{n*(n+1)//2} = {upper_patterns:,}")
    print(f"  toeplitz: 2^{n} = {toeplitz_patterns:,}")

    # ベンチマーク実行
    import time
    print(f"\n=== ベンチマーク (1回の計算時間) ===")
    test_matrix = generate_full_random(n)
    start = time.time()
    _ = permanent(test_matrix, method='ryser')
    elapsed = time.time() - start
    print(f"  1回あたり: {elapsed:.4f} 秒")
    print(f"  参考: N=100  → 約 {elapsed * 100:.1f} 秒")
    print(f"  参考: N=1000 → 約 {elapsed * 1000:.1f} 秒")
    print(f"  参考: N=10000 → 約 {elapsed * 10000:.1f} 秒")

    # 試行回数入力
    try:
        N = int(input("試行回数 N を入力してください: "))
        if N < 1:
            print("エラー: Nは1以上の整数である必要があります")
            sys.exit(1)
    except ValueError:
        print("エラー: 有効な整数を入力してください")
        sys.exit(1)

    # 行列タイプ選択
    print("\n=== 行列タイプ ===")
    print("  full    : 全要素ランダム")
    print("  upper   : 下三角は+1固定、上三角ランダム")
    print("  toeplitz: 下三角は+1固定、上三角はToeplitz構造")
    matrix_type = input("タイプ [full/upper/toeplitz] (デフォルト: full): ").strip().lower()
    if matrix_type not in ('full', 'upper', 'toeplitz'):
        matrix_type = 'full'

    # 計算モード選択
    print("\n=== 計算モード ===")
    print("  perm: permanent")
    print("  det : determinant")
    calc_mode = input("モード [perm/det] (デフォルト: perm): ").strip().lower()
    if calc_mode not in ('perm', 'det'):
        calc_mode = 'perm'

    # 設定確認
    print(f"\n=== 設定確認 ===")
    print(f"行列サイズ: {n}x{n}")
    print(f"試行回数: {N:,}")
    print(f"行列タイプ: {matrix_type}")
    print(f"計算モード: {calc_mode}")

    confirm = input("\n実行しますか？ (y/n): ")
    if confirm.lower() != 'y':
        print("中止しました。")
        return

    run_sampling(n, N, calc_mode, matrix_type)


if __name__ == '__main__':
    main()
