#!/usr/bin/env python3
"""
reverse_triangle_cal - メインプログラム

Triangle Hankel制約下でのパーマネント全探索
"""

import os
import sys
from datetime import datetime

from reverse_triangle_cal import (
    permanent,
    calculate_krauter_conjecture_value,
    create_hankel_matrix_from_set,
    calculate_matrix_properties,
)
from reverse_triangle_cal.generators.hankel_indices import generate_upper_triangular_hankel_indices


def main():
    print("=" * 60)
    print("reverse_triangle_cal - Triangle Hankel行列パーマネント探索")
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
    total_patterns = 2 ** (2*n - 1)
    krauter_expected = calculate_krauter_conjecture_value(n)

    print(f"\n=== 探索情報 ===")
    print(f"行列サイズ: n = {n}")
    print(f"制約条件: Triangle Hankel (上三角はHankel, 下三角は1)")
    print(f"総パターン数: {total_patterns:,} (2^{2*n-1})")
    print(f"Hankelインデックス範囲: 0 ≤ k ≤ {2*n-2}")
    print(f"Kräuter予想値: {krauter_expected}")

    # 大きな探索空間の警告
    if n >= 8:
        print(f"\n⚠️  警告: n={n} は大きいです！")
        print(f"   {total_patterns:,} パターンは数時間かかる可能性があります。")
        print(f"   より小さいnから始めることをお勧めします。")
        try:
            response = input("\n続行しますか? (y/N): ")
            if response.lower() != 'y':
                print("中断されました")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n中断されました")
            sys.exit(0)

    # 結果ファイルの準備
    result_dir = os.path.join(os.path.dirname(__file__), 'result')
    os.makedirs(result_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
    filename = f"n{n}-triangle-hankel-exhaustive-{timestamp}.txt"
    filepath = os.path.join(result_dir, filename)

    # ヘッダー書き込み
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Minimum Positive Permanent Search Results for n={n}\n")
        f.write(f"Method: exhaustive (triangle hankel)\n")
        f.write(f"Constraint: Triangle Hankel (upper=Hankel, lower=1)\n")
        f.write(f"Hankel index range: 0 to {2*n-2}\n")
        f.write(f"Total patterns: {total_patterns:,}\n")
        f.write(f"Krauter Conjecture Expected Value: {krauter_expected}\n")
        f.write(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")
        f.write("Format: YY-MM-DD HH:MM:SS | S={...} | Permanent=... | Status=...\n")
        f.write("=" * 60 + "\n\n")

    print(f"\n結果ファイル: {filename}")
    print(f"探索開始... (Ctrl+C で中断)\n")

    # Step 3 & 4: 全パターンを生成してパーマネント計算
    best_abs_permanent = float('inf')  # 最小絶対値
    best_perm_value = None              # その時の実際のパーマネント値（符号付き）
    iteration = 0
    found_krauter = False

    try:
        for S in generate_upper_triangular_hankel_indices(n):
            iteration += 1

            # 行列生成（メモリ効率的）
            matrix = create_hankel_matrix_from_set(n, S)

            # パーマネント計算
            perm_value = permanent(matrix, method='ryser')

            # 行列性質
            matrix_props = calculate_matrix_properties(matrix)

            # Kräuter予想との比較（絶対値で評価、ただしperm=0は除外）
            abs_perm = abs(perm_value)
            matches_krauter = (perm_value != 0) and (abs_perm == krauter_expected)
            better_than_krauter = (perm_value != 0) and (abs_perm < krauter_expected)

            # 改善された場合のみログに記録（絶対値で判定、ただしperm=0は除外）
            is_improvement = False
            if perm_value != 0 and abs_perm < best_abs_permanent:
                best_abs_permanent = abs_perm
                best_perm_value = perm_value  # 元の符号付き値を保存
                is_improvement = True

                # ログ出力
                timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # Kräuterステータス
                if matches_krauter:
                    krauter_status = "MATCHES_KRAUTER ✓"
                    found_krauter = True
                elif better_than_krauter:
                    krauter_status = "BETTER_THAN_KRAUTER !!"
                else:
                    krauter_status = "NEW_MIN"

                # コンソール出力（パーマネント値を符号付きで表示、絶対値も併記）
                print(f"{timestamp_str} | S={sorted(S)} | Permanent={perm_value} (|perm|={abs_perm}) | Status={krauter_status}")

                # Kräuter予想値にマッチした場合は行列も出力
                if matches_krauter:
                    print(f"\n{'='*60}")
                    print(f"✓ Kräuter予想値にマッチしました（絶対値で）！")
                    print(f"{'='*60}")
                    print(f"S = {sorted(S)}")
                    print(f"Matrix (n={n}):")
                    print(matrix)
                    print(f"Permanent = {perm_value} (|perm|={abs_perm})")
                    print(f"{'='*60}\n")

                # ファイル出力
                with open(filepath, 'a', encoding='utf-8') as f:
                    f.write(f"{timestamp_str} | ")
                    f.write(f"Iteration={iteration}/{total_patterns} | ")
                    f.write(f"S={sorted(S)} | ")
                    f.write(f"Permanent={perm_value} | ")
                    f.write(f"Abs_permanent={abs_perm} | ")
                    f.write(f"Krauter_expected={krauter_expected} | ")
                    f.write(f"Status={krauter_status} | ")
                    f.write(f"Ones_ratio={matrix_props['ones_ratio']:.3f}\n")

                    # Kräuter値と一致した場合は行列も記録
                    if matches_krauter:
                        f.write(f"\n{'='*60}\n")
                        f.write(f"KRAUTER MATCH FOUND!\n")
                        f.write(f"S = {sorted(S)}\n")
                        f.write(f"Matrix:\n")
                        f.write(str(matrix) + "\n")
                        f.write(f"Permanent = {perm_value}\n")
                        f.write(f"{'='*60}\n\n")

                # Kräuter予想値にマッチしたら終了
                if matches_krauter:
                    print(f"探索を終了します。")
                    break

            # 進捗表示（1000回ごと）
            if iteration % 1000 == 0:
                progress = (iteration / total_patterns) * 100
                if best_perm_value is not None:
                    min_display = f"{best_perm_value} (|perm|={best_abs_permanent})"
                else:
                    min_display = "未発見"
                print(f"[進捗] {iteration:,}/{total_patterns:,} ({progress:.1f}%) | "
                      f"現在の最小絶対値: {min_display}")

        # 完了
        print(f"\n{'=' * 60}")
        if found_krauter:
            print("Kräuter予想値にマッチして終了！")
        else:
            print("探索完了！")
        print(f"{'=' * 60}")
        print(f"処理済みパターン: {iteration:,}/{total_patterns:,}")
        if best_perm_value is not None:
            print(f"最小絶対値パーマネント: {best_perm_value} (|perm|={best_abs_permanent})")
        else:
            print(f"最小絶対値パーマネント: 未発見")
        print(f"Kräuter予想値: {krauter_expected}")

        if found_krauter:
            print(f"✓ Kräuter予想値と一致しました（絶対値で）")
        elif best_abs_permanent < krauter_expected:
            print(f"!! Kräuter予想値より小さい値が見つかりました（予想に反する！）")

        print(f"\n結果は {filename} に保存されました")

        # ファイルに最終サマリー
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"Search completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Processed patterns: {iteration:,}/{total_patterns:,}\n")
            if best_perm_value is not None:
                f.write(f"Minimum absolute permanent: {best_perm_value} (|perm|={best_abs_permanent})\n")
            else:
                f.write(f"Minimum absolute permanent: Not found\n")
            f.write(f"Krauter expected: {krauter_expected}\n")
            if found_krauter:
                f.write(f"Status: MATCHES_KRAUTER\n")
            elif best_abs_permanent < krauter_expected:
                f.write(f"Status: BETTER_THAN_KRAUTER (!)\n")
            f.write(f"{'=' * 60}\n")

    except KeyboardInterrupt:
        print(f"\n\n探索を中断しました")
        print(f"処理済み: {iteration:,}/{total_patterns:,} ({iteration/total_patterns*100:.1f}%)")
        if best_perm_value is not None:
            print(f"現在の最小絶対値パーマネント: {best_perm_value} (|perm|={best_abs_permanent})")
        else:
            print(f"現在の最小絶対値パーマネント: 未発見")
        print(f"結果は {filename} に保存されています")

        # 中断時もサマリー記録
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(f"\n{'=' * 60}\n")
            f.write(f"Search interrupted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Processed: {iteration:,}/{total_patterns:,} ({iteration/total_patterns*100:.1f}%)\n")
            if best_perm_value is not None:
                f.write(f"Minimum absolute permanent so far: {best_perm_value} (|perm|={best_abs_permanent})\n")
            else:
                f.write(f"Minimum absolute permanent so far: Not found\n")
            f.write(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
