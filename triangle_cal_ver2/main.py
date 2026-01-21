#!/usr/bin/env python3
"""
triangle_cal_ver2 - メインプログラム

上三角 & Toeplitz制約下でのパーマネント全探索
"""

import os
import sys
from datetime import datetime

from triangle_cal import (
    permanent,
    calculate_krauter_conjecture_value,
    create_toeplitz_matrix_from_set,
    calculate_matrix_properties,
)
from triangle_cal.generators.toeplitz_indices import generate_upper_triangular_toeplitz_indices


def main():
    print("=" * 60)
    print("triangle_cal_ver2 - 上三角Toeplitz行列パーマネント探索")
    print("=" * 60)

    # Step 1: nを入力
    try:
        n = int(input("\n行列サイズ n を入力してください: "))
        if n <= 0:
            print("エラー: nは正の整数である必要があります")
            sys.exit(1)
    except ValueError:
        print("エラー: 整数を入力してください")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n中断されました")
        sys.exit(0)

    # Step 2: パターン数を出力
    total_patterns = 2 ** n
    krauter_expected = calculate_krauter_conjecture_value(n)

    print(f"\n=== 探索情報 ===")
    print(f"行列サイズ: n = {n}")
    print(f"制約条件: 上三角 & Toeplitz")
    print(f"総パターン数: {total_patterns:,} (2^{n})")
    print(f"Kräuter予想値: {krauter_expected}")

    # 結果ファイルの準備
    result_dir = os.path.join(os.path.dirname(__file__), 'result')
    os.makedirs(result_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    filename = f"n{n}-triangle-toeplitz-exhaustive-{timestamp}.txt"
    filepath = os.path.join(result_dir, filename)

    # ヘッダー書き込み
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Minimum Positive Permanent Search Results for n={n}\n")
        f.write(f"Method: exhaustive (triangle & toeplitz)\n")
        f.write(f"Constraint: Upper triangular & Toeplitz matrices\n")
        f.write(f"Total patterns: {total_patterns:,}\n")
        f.write(f"Krauter Conjecture Expected Value: {krauter_expected}\n")
        f.write(f"Search Mode: Positive values only (stop on +krauter_expected)\n")
        f.write(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
        f.write("Format: YY-MM-DD HH:MM:SS | S={...} | Permanent=... | Status=...\n")
        f.write("Notes:\n")
        f.write("  - Only positive permanents are tracked for minimum\n")
        f.write("  - Negative krauter (-krauter_expected) is logged if found\n")
        f.write("  - Search ends when permanent = +krauter_expected\n")
        f.write("=" * 60 + "\n\n")

    print(f"\n結果ファイル: {filename}")
    print(f"探索開始... (Ctrl+C で中断)\n")

    # Step 3 & 4: 全パターンを生成してパーマネント計算
    best_positive_permanent = float('inf')  # 最小正の値
    best_perm_value = None                  # その時の実際のパーマネント値
    iteration = 0
    found_krauter = False                   # 正のkrauterを見つけたかフラグ
    found_negative_krauter = False          # 負のkrauterを見つけたかフラグ

    try:
        for S in generate_upper_triangular_toeplitz_indices(n):
            iteration += 1

            # 行列生成（メモリ効率的）
            matrix = create_toeplitz_matrix_from_set(n, S)

            # パーマネント計算
            perm_value = permanent(matrix, method='ryser')

            # 行列性質
            matrix_props = calculate_matrix_properties(matrix)

            # Kräuter予想との比較（正の値のみで評価）
            matches_krauter = (perm_value == krauter_expected)  # 正の値で完全一致
            is_negative_krauter = (perm_value == -krauter_expected)  # 負の予想値

            # 改善判定とログ記録
            is_improvement = False
            should_log = False  # ログ記録フラグ

            # ケース1: 正の値で最小値が更新された場合
            if perm_value > 0 and perm_value < best_positive_permanent:
                best_positive_permanent = perm_value
                best_perm_value = perm_value
                is_improvement = True
                should_log = True

                # ステータス判定
                if matches_krauter:
                    krauter_status = "MATCHES_KRAUTER ✓"
                    found_krauter = True
                else:
                    krauter_status = "NEW_POSITIVE_MIN"

            # ケース2: -krauter_expected の場合（初回のみ記録）
            elif is_negative_krauter and not found_negative_krauter:
                found_negative_krauter = True
                should_log = True
                krauter_status = "NEGATIVE_KRAUTER_FOUND"

            # ログ出力
            if should_log:
                timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # コンソール出力
                print(f"{timestamp_str} | S={sorted(S)} | Permanent={perm_value} | Status={krauter_status}")

                # ファイル出力
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(f"{timestamp_str} | ")
                    f.write(f"Iteration={iteration}/{total_patterns} | ")
                    f.write(f"S={sorted(S)} | ")
                    f.write(f"Permanent={perm_value} | ")
                    f.write(f"Krauter_expected={krauter_expected} | ")
                    f.write(f"Status={krauter_status} | ")
                    f.write(f"Ones_ratio={matrix_props['ones_ratio']:.3f}\n")

            # Kräuter予想値（正の値）にマッチしたら終了
            if is_improvement and matches_krauter:
                print(f"\n✓ Kräuter予想値（正の値）にマッチしました！探索を終了します。")
                break

            # 進捗表示（1000回ごと）
            if iteration % 1000 == 0:
                progress = (iteration / total_patterns) * 100
                if best_perm_value is not None:
                    min_display = f"{best_perm_value}"
                else:
                    min_display = "未発見"
                print(f"[進捗] {iteration:,}/{total_patterns:,} ({progress:.1f}%) | "
                      f"現在の最小正の値: {min_display}")

        # 完了
        print(f"\n{'=' * 60}")
        if found_krauter:
            print("Kräuter予想値（正の値）にマッチして終了！")
        else:
            print("探索完了！")
        print(f"{'=' * 60}")
        print(f"処理済みパターン: {iteration:,}/{total_patterns:,}")
        if best_perm_value is not None:
            print(f"最小正の値パーマネント: {best_perm_value}")
        else:
            print(f"最小正の値パーマネント: 未発見")
        print(f"Kräuter予想値: {krauter_expected}")

        if found_krauter:
            print(f"✓ Kräuter予想値（正の値）と一致しました")

        if found_negative_krauter:
            print(f"⚠ 負のKräuter予想値（-{krauter_expected}）も発見されました")

        print(f"\n結果は {filename} に保存されました")

        # ファイルに最終サマリー
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"Search completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Processed patterns: {iteration:,}/{total_patterns:,}\n")
            if best_perm_value is not None:
                f.write(f"Minimum positive permanent: {best_perm_value}\n")
            else:
                f.write(f"Minimum positive permanent: Not found\n")
            f.write(f"Krauter expected: {krauter_expected}\n")
            if found_krauter:
                f.write(f"Status: MATCHES_KRAUTER (positive)\n")
            if found_negative_krauter:
                f.write(f"Negative Krauter: Found (-{krauter_expected})\n")
            f.write(f"{'=' * 60}\n")

    except KeyboardInterrupt:
        print(f"\n\n探索を中断しました")
        print(f"処理済み: {iteration:,}/{total_patterns:,} ({iteration/total_patterns*100:.1f}%)")
        if best_perm_value is not None:
            print(f"現在の最小正の値パーマネント: {best_perm_value}")
        else:
            print(f"現在の最小正の値パーマネント: 未発見")

        if found_negative_krauter:
            print(f"⚠ 負のKräuter予想値（-{krauter_expected}）も発見されました")

        print(f"結果は {filename} に保存されています")

        # 中断時もサマリー記録
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"Search interrupted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Processed: {iteration:,}/{total_patterns:,} ({iteration/total_patterns*100:.1f}%)\n")
            if best_perm_value is not None:
                f.write(f"Minimum positive permanent so far: {best_perm_value}\n")
            else:
                f.write(f"Minimum positive permanent so far: Not found\n")
            if found_negative_krauter:
                f.write(f"Negative Krauter: Found (-{krauter_expected})\n")
            f.write(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
