#!/usr/bin/env python3
"""
上三角行列全探索 - Permanent頻度分析ツール

上三角部分（対角線含む）に全ての±1の組み合わせを試し、
下三角部分を1に固定した行列のパーマネントを全探索する。

出力オプション:
1. 集計出力（デフォルト: はい）
   - perm値の頻度分析をCSV形式で出力
   - フォーマット: perm,頻度
   - ファイル名: {n}_{MMDD}_{HH}_{MM}_summary.csv

2. 行列出力（デフォルト: いいえ）
   - 各パターンの詳細をCSV形式で出力
   - フォーマット: 行番号,permの値,+1と-1の割合,行列
   - ファイル名: {n}_{MMDD}_{HH}_{MM}.csv
"""

import sys
import os
import csv
import time
import numpy as np
from datetime import datetime
from itertools import combinations

# 必要なモジュールのパスを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'rn_calculator'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'toepliz_cal'))
from calc_permanent import permanent, determinant


def create_upper_triangular_matrix_from_positions(n, positions):
    """
    上三角要素のインデックスセットから行列を構築

    Args:
        n: 行列サイズ
        positions: +1にする上三角要素のインデックスセット

    Returns:
        np.ndarray: nxnの上三角(±1)行列
    """
    matrix = np.ones((n, n), dtype=int)  # 下三角は全て1で初期化

    # 上三角部分を構築
    idx = 0
    for i in range(n):
        for j in range(i, n):  # 対角線含む上三角
            if idx in positions:
                matrix[i, j] = 1
            else:
                matrix[i, j] = -1
            idx += 1

    return matrix


def calculate_ones_ratio(matrix):
    """
    行列全体での+1の比率を計算

    Args:
        matrix: 2次元のnumpy配列

    Returns:
        float: +1の比率（0.0〜1.0）
    """
    n = len(matrix)
    total_elements = n * n
    ones_count = np.sum(matrix == 1)
    return ones_count / total_elements


def create_csv_filepath(n, suffix=""):
    """
    CSV出力先パスを生成

    Args:
        n: 行列サイズ
        suffix: ファイル名のサフィックス（例: "_summary"）

    Returns:
        str: CSVファイルのパス
    """
    # resultディレクトリのパスを生成
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_dir = os.path.join(script_dir, 'result')

    # resultディレクトリが存在しない場合は作成
    os.makedirs(result_dir, exist_ok=True)

    # ファイル名を生成: {n}_{MMDD}_{HH}_{MM}{suffix}.csv
    timestamp = datetime.now().strftime("%m%d_%H_%M")
    filename = f"{n}_{timestamp}{suffix}.csv"

    return os.path.join(result_dir, filename)


def write_summary_csv(n, value_frequency, calculate_mode='perm'):
    """
    値の頻度分析をCSVに出力

    Args:
        n: 行列サイズ
        value_frequency: {値: 頻度}の辞書
        calculate_mode: 'perm' または 'det'（デフォルト: 'perm'）
    """
    csv_filepath = create_csv_filepath(n, suffix="_summary")

    with open(csv_filepath, 'w', encoding='utf-8', newline='') as f:
        csv_writer = csv.writer(f)

        # ヘッダー書き込み（計算モードに応じて変更）
        value_header = 'perm' if calculate_mode == 'perm' else 'det'
        csv_writer.writerow([value_header, '頻度'])

        # 値でソートして出力
        for value in sorted(value_frequency.keys()):
            csv_writer.writerow([value, value_frequency[value]])

    print(f"\n集計CSV出力先: {csv_filepath}")


def exhaustive_search(n, csv_writer=None, output_matrix=False, output_summary=True,
                     calculate_mode='perm'):
    """
    全パターンを生成・計算・CSV書き込み

    Args:
        n: 行列サイズ
        csv_writer: CSVライター（行列出力する場合のみ）
        output_matrix: 行列をCSVに出力するか
        output_summary: 集計CSVを出力するか
        calculate_mode: 'perm' または 'det'（デフォルト: 'perm'）

    Returns:
        dict: 統計情報
    """
    upper_size = n * (n + 1) // 2  # 上三角要素数
    total_patterns = 2 ** upper_size

    print(f"\n上三角要素数: {upper_size}")
    print(f"総パターン数: {total_patterns:,}")
    print(f"\n探索を開始します...\n")

    # 統計情報
    row_number = 1
    checkpoint = max(1, total_patterns // 100)  # 1%ごとに進捗表示
    start_time = time.time()

    # 値の頻度をカウントする辞書
    value_frequency = {}

    # 全パターンを生成して処理
    try:
        for upper_ones in range(0, upper_size + 1):
            # upper_ones個の位置を選ぶ組み合わせを生成
            for positions in combinations(range(upper_size), upper_ones):
                # 行列構築
                matrix = create_upper_triangular_matrix_from_positions(n, positions)

                # permanent または determinant を計算
                if calculate_mode == 'perm':
                    value = permanent(matrix, method='ryser', verbose=False)
                else:  # 'det'
                    value = determinant(matrix, method='numpy', verbose=False)

                # 頻度をカウント
                if value in value_frequency:
                    value_frequency[value] += 1
                else:
                    value_frequency[value] = 1

                # 行列出力が有効な場合、CSVに書き込み
                if output_matrix and csv_writer is not None:
                    # +1の割合計算
                    ones_ratio = calculate_ones_ratio(matrix)

                    csv_writer.writerow([
                        row_number,
                        value,
                        f"{ones_ratio:.5f}",
                        str(matrix.tolist())
                    ])

                # 進捗表示
                if row_number % checkpoint == 0:
                    progress = row_number / total_patterns * 100
                    elapsed = time.time() - start_time
                    rate = row_number / elapsed if elapsed > 0 else 0
                    eta = (total_patterns - row_number) / rate if rate > 0 else 0
                    print(f"進捗: {progress:.1f}% ({row_number:,}/{total_patterns:,}) | "
                          f"速度: {rate:.0f} パターン/秒 | 残り時間: {eta:.0f}秒")

                row_number += 1

    except KeyboardInterrupt:
        print(f"\n\nCtrl+C により中断されました。")
        print(f"現在までの結果（{row_number-1:,}パターン）は保存されています。")
        elapsed_time = time.time() - start_time

        # 集計CSVを出力
        if output_summary and value_frequency:
            write_summary_csv(n, value_frequency, calculate_mode)

        return {
            'total_processed': row_number - 1,
            'total_patterns': total_patterns,
            'elapsed_time': elapsed_time,
            'interrupted': True
        }

    elapsed_time = time.time() - start_time

    # 集計CSVを出力
    if output_summary and value_frequency:
        write_summary_csv(n, value_frequency, calculate_mode)

    return {
        'total_processed': row_number - 1,
        'total_patterns': total_patterns,
        'elapsed_time': elapsed_time,
        'interrupted': False
    }


def main():
    """
    メイン関数
    """
    print("=== 上三角行列全探索 - Permanent頻度分析 ===")
    print("上三角部分（対角線含む）の全ての±1組み合わせを探索し、")
    print("各パターンのpermanent値をCSVに出力します。\n")

    # ユーザー入力
    try:
        n = int(input("行列サイズ n を入力してください: "))
        if n <= 0:
            print("エラー: nは正の整数である必要があります")
            sys.exit(1)
    except ValueError:
        print("エラー: 有効な整数を入力してください")
        sys.exit(1)

    # 探索規模の表示
    upper_size = n * (n + 1) // 2
    total_patterns = 2 ** upper_size

    print(f"\n行列サイズ: {n}x{n}")
    print(f"上三角要素数: {upper_size}")
    print(f"総パターン数: {total_patterns:,}")

    # 推定時間の表示（参考値）
    if n == 3:
        print(f"推定計算時間: 数秒以内")
    elif n == 4:
        print(f"推定計算時間: 数秒〜数十秒")
    elif n == 5:
        print(f"推定計算時間: 数分〜数十分")
    elif n == 6:
        print(f"推定計算時間: 数時間")
    else:
        print(f"推定計算時間: 非常に長時間（n≥7では実用的でない可能性があります）")

    # 出力オプションの確認
    print("\n=== 出力オプション ===")

    # 集計出力の確認（デフォルト: はい）
    summary_input = input("集計出力をしますか？ (y/n) [デフォルト: y]: ").strip().lower()
    output_summary = summary_input != 'n'  # 'n'以外はすべて有効

    # 行列出力の確認（デフォルト: いいえ）
    matrix_input = input("行列をCSVに出力しますか？ (y/n) [デフォルト: n]: ").strip().lower()
    output_matrix = matrix_input == 'y'  # 'y'のみ有効

    # 計算対象の選択
    print("\n=== 計算対象 ===")
    print("  perm: permanent")
    print("  det: determinant")
    mode_input = input("モード [perm/det] (デフォルト: perm): ").strip().lower()
    if mode_input == 'det':
        calculate_mode = 'det'
    else:
        calculate_mode = 'perm'

    print(f"\n計算モード: {calculate_mode}")

    # 確認
    confirm = input("\n探索を開始しますか？ (y/n): ")
    if confirm.lower() != 'y':
        print("中止しました。")
        return

    # 行列出力が有効な場合のみCSVファイルを開く
    csv_filepath = None
    csv_writer = None

    if output_matrix:
        csv_filepath = create_csv_filepath(n)
        print(f"\n行列CSV出力先: {csv_filepath}")

    # 探索開始
    start_time = time.time()

    if output_matrix:
        # CSV書き込み開始
        with open(csv_filepath, 'w', encoding='utf-8', newline='') as f:
            csv_writer = csv.writer(f)

            # ヘッダー書き込み（計算モードに応じて変更）
            value_header = 'permの値' if calculate_mode == 'perm' else 'detの値'
            csv_writer.writerow(['行番号', value_header, '+1と-1の割合', '行列'])

            stats = exhaustive_search(n, csv_writer, output_matrix, output_summary,
                                    calculate_mode)
    else:
        # 行列出力しない場合
        stats = exhaustive_search(n, None, output_matrix, output_summary,
                                 calculate_mode)

    # 結果表示
    print(f"\n{'='*60}")
    if stats['interrupted']:
        print("=== 探索中断 ===")
    else:
        print("=== 探索完了 ===")

    print(f"処理パターン数: {stats['total_processed']:,} / {stats['total_patterns']:,}")
    print(f"計算時間: {stats['elapsed_time']:.2f}秒")

    if stats['elapsed_time'] > 0:
        rate = stats['total_processed'] / stats['elapsed_time']
        print(f"処理速度: {rate:.2f} パターン/秒")

    if output_matrix and csv_filepath:
        print(f"行列CSV出力先: {csv_filepath}")

    print(f"{'='*60}")


if __name__ == "__main__":
    main()
