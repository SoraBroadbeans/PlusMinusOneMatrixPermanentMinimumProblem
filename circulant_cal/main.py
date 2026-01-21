#!/usr/bin/env python3
"""
巡回行列パーマネント総合計算ツール

C_n のすべてのパターンを生成し、ストリーミング処理で1つずつ計算する。
"""

import sys
import os
import time
from itertools import combinations

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from circulant_permanent import create_circulant_matrix_from_set, calculate_circulant_permanent_from_set
from circulant_permanent import calculate_krauter_theoretical_value


def generate_all_circulant_patterns(n):
    """
    C_n のすべての可能な集合Sパターンを生成（ジェネレータ）
    
    Args:
        n: 行列のサイズ
        
    Yields:
        set: 各集合S
    """
    # 可能なインデックス範囲: 0 から n-1
    possible_indices = list(range(n))
    
    # 空集合から全集合まで、すべての部分集合を生成
    for r in range(len(possible_indices) + 1):  # 0からlen(possible_indices)まで
        for subset in combinations(possible_indices, r):
            yield set(subset)


def process_single_pattern(n, S, pattern_num, total_patterns, rate=None):
    """
    単一のパターンを処理してパーマネントを計算
    
    Args:
        n: 行列のサイズ
        S: 集合
        pattern_num: パターン番号
        total_patterns: 総パターン数
        rate: 1の要素の比率閾値。単一値(上限のみ)またはタプル(下限, 上限)。None の場合は常に計算する
        
    Returns:
        dict: 計算結果
    """
    try:
        # C_{n,S} 行列を作成
        matrix = create_circulant_matrix_from_set(n, S)
        
        # 常に1の比率を計算
        ones_ratio = calculate_matrix_ones_ratio(matrix)
        
        # rate オプションが指定されている場合、比率をチェック
        if rate is not None:
            should_skip = False
            
            if isinstance(rate, tuple):
                # 範囲形式: 下限と上限の両方をチェック
                rate_lower, rate_upper = rate
                if ones_ratio <= rate_lower or ones_ratio >= rate_upper:
                    should_skip = True
            else:
                # 単一値形式: 上限のみチェック（従来の動作）
                if ones_ratio > rate:
                    should_skip = True
            
            if should_skip:
                return {
                    'pattern_num': pattern_num,
                    'S': sorted(S) if S else [],
                    'skipped': True,
                    'ones_ratio': ones_ratio,
                    'rate_threshold': rate,
                    'matrix': matrix,
                    'success': True
                }
        
        # パーマネント計算
        start_time = time.time()
        perm_value, calc_time = calculate_circulant_permanent_from_set(n, S, verbose=False)
        total_time = time.time() - start_time
        
        return {
            'pattern_num': pattern_num,
            'S': sorted(S) if S else [],
            'permanent': perm_value,
            'calc_time': calc_time,
            'total_time': total_time,
            'ones_ratio': ones_ratio,
            'matrix': matrix,
            'success': True
        }
    except Exception as e:
        return {
            'pattern_num': pattern_num,
            'S': sorted(S) if S else [],
            'error': str(e),
            'ones_ratio': 0.0,
            'success': False
        }


def display_result(result, verbose=True):
    """
    計算結果を表示
    """
    if result['success']:
        pattern = result['pattern_num']
        S = result['S']
        matrix = result['matrix']
        n = len(matrix)
        
        # C_n{S} 形式で表示
        c_display = f"C_{n}{{{S if S else '∅'}}}"
        
        # スキップされた場合の表示
        if 'skipped' in result:
            ratio = result['ones_ratio']
            threshold = result['rate_threshold']
            if verbose:
                if isinstance(threshold, tuple):
                    rate_lower, rate_upper = threshold
                    print(f"パターン {pattern:,}: {c_display} → スキップ (1の比率: {ratio:.3f} <= {rate_lower:.1f} または >= {rate_upper:.1f})")
                else:
                    print(f"パターン {pattern:,}: {c_display} → スキップ (1の比率: {ratio:.3f} > {threshold:.3f})")
            else:
                print(f"{pattern:,}: {c_display} → スキップ")
            return
        
        # 通常の計算結果表示
        perm = result['permanent']
        time_taken = result['calc_time']
        ones_ratio = result.get('ones_ratio', 0.0)
        
        if verbose:
            print(f"パターン {pattern:,}: {c_display} → パーマネント = {perm} (1の比率: {ones_ratio:.3f}, {time_taken:.6f}秒)")
        else:
            # 簡潔表示
            print(f"{pattern:,}: {c_display} → {perm} (r={ones_ratio:.3f})")
    else:
        print(f"パターン {result['pattern_num']:,}: エラー - {result['error']}")


def calculate_total_patterns(n):
    """
    総パターン数を計算
    C_n の場合、可能なインデックス範囲は 0 から n-1 まで
    つまり n 個のインデックスがある
    各インデックスを含むか含まないかで 2^n 通りの集合S
    """
    return 2 ** n


def calculate_matrix_ones_ratio(matrix):
    """
    行列の1の要素数/全体の要素数の比率を計算
    
    Args:
        matrix: 2次元のnumpy配列またはリスト
        
    Returns:
        float: 1の要素の比率 (0.0 ~ 1.0)
    """
    import numpy as np
    matrix = np.array(matrix)
    total_elements = matrix.size
    ones_count = np.sum(matrix == 1)
    return ones_count / total_elements if total_elements > 0 else 0.0


def main():
    """
    メイン関数
    """
    print("=== 巡回行列パーマネント総合計算ツール ===")
    print("C_n のすべてのパターンを生成し、ストリーミング処理で計算します。\n")
    
    # ユーザーから n を受け取る
    try:
        n = int(input("行列サイズ n を入力してください: "))
        if n <= 0:
            print("エラー: nは正の整数である必要があります")
            sys.exit(1)
    except ValueError:
        print("エラー: 有効な整数を入力してください")
        sys.exit(1)
    
    # rateオプションを受け取る
    rate = None
    rate_input = input("rate オプション (下限-上限, 例: 0.3-0.7, 空白でスキップ): ").strip()
    if rate_input:
        try:
            if '-' in rate_input:
                # 範囲形式 (下限-上限)
                lower_str, upper_str = rate_input.split('-', 1)
                rate_lower = float(lower_str.strip())
                rate_upper = float(upper_str.strip())
                if not (0.0 <= rate_lower <= 1.0 and 0.0 <= rate_upper <= 1.0):
                    print("エラー: rateの下限・上限は0から1の間の値である必要があります")
                    sys.exit(1)
                if rate_lower > rate_upper:
                    print("エラー: rateの下限は上限以下である必要があります")
                    sys.exit(1)
                rate = (rate_lower, rate_upper)
                print(f"rate オプション設定: {rate_lower}-{rate_upper} (1の比率が{rate_lower*100:.1f}%より大きく{rate_upper*100:.1f}%未満の場合のみ計算)")
            else:
                # 従来の単一値形式 (上限のみ)
                rate_value = float(rate_input)
                if not (0.0 <= rate_value <= 1.0):
                    print("エラー: rateは0から1の間の値である必要があります")
                    sys.exit(1)
                rate = rate_value
                print(f"rate オプション設定: {rate_value} (1の比率が{rate_value*100:.1f}%以下の場合のみ計算)")
        except ValueError:
            print("エラー: rateには有効な数値を入力してください")
            sys.exit(1)
    
    # 総パターン数を計算・表示
    total_patterns = calculate_total_patterns(n)
    print(f"\n行列サイズ: {n}×{n}")
    print(f"総パターン数: {total_patterns:,}")
    
    # 理論値を計算・表示
    theoretical_value = calculate_krauter_theoretical_value(n)
    print(f"Kräuter理論値: {theoretical_value}")
    
    # 表示オプション
    verbose = True
    if total_patterns > 100:
        response = input("\n詳細表示モードを使用しますか？ (Y/n): ")
        if response.lower() == 'n':
            verbose = False
    
    # 統計情報
    stats = {
        'positive_count': 0,
        'negative_count': 0,
        'zero_count': 0,
        'min_positive': float('inf'),
        'max_positive': float('-inf'),
        'min_negative': float('inf'),
        'max_negative': float('-inf'),
        'total_time': 0,
        'processed_count': 0
    }
    
    print(f"\n{'='*60}")
    print("計算開始...")
    start_time = time.time()
    
    try:
        pattern_num = 1
        skipped_count = 0
        for S in generate_all_circulant_patterns(n):
            # 単一パターンを処理
            result = process_single_pattern(n, S, pattern_num, total_patterns, rate)
            
            # 結果表示
            display_result(result, verbose)
            
            # 統計情報更新
            if result['success']:
                # スキップされた場合は統計から除外
                if 'skipped' in result:
                    skipped_count += 1
                else:
                    perm = result['permanent']
                    stats['processed_count'] += 1
                    stats['total_time'] += result['calc_time']
                    
                    # 理論値との一致判定
                    if abs(perm) == theoretical_value:
                        print(f"\n★★★ 理論値と一致しました！ ★★★")
                        print(f"S = {result['S']}")
                        print(f"パーマネント = {perm} (絶対値: {abs(perm)})")
                        print(f"理論値 = {theoretical_value}")
                        print(f"計算時間: {result['calc_time']:.6f}秒")
                        print("\n処理を終了します。")
                        break
                    
                    if perm > 0:
                        stats['positive_count'] += 1
                        stats['min_positive'] = min(stats['min_positive'], perm)
                        stats['max_positive'] = max(stats['max_positive'], perm)
                    elif perm < 0:
                        stats['negative_count'] += 1
                        stats['min_negative'] = min(stats['min_negative'], abs(perm))
                        stats['max_negative'] = max(stats['max_negative'], abs(perm))
                    else:
                        stats['zero_count'] += 1
            
            pattern_num += 1
            
            # 進捗表示（100パターンごと）
            if pattern_num % 100 == 0:
                elapsed = time.time() - start_time
                print(f"進捗: {pattern_num:,}/{total_patterns:,} ({pattern_num/total_patterns*100:.1f}%)")
    
    except KeyboardInterrupt:
        print("\n\n計算が中断されました。")
    
    finally:
        # 最終統計表示
        total_elapsed = time.time() - start_time
        processed = stats['processed_count']
        
        print(f"\n{'='*60}")
        print("=== 計算結果統計 ===")
        print(f"処理されたパターン数: {processed:,}/{total_patterns:,}")
        if rate is not None:
            if isinstance(rate, tuple):
                rate_lower, rate_upper = rate
                print(f"スキップされたパターン数: {skipped_count:,} (1の比率が{rate_lower*100:.1f}%以下または{rate_upper*100:.1f}%以上)")
            else:
                print(f"スキップされたパターン数: {skipped_count:,} (1の比率が{rate*100:.1f}%を超過)")
            print(f"実際に計算されたパターン数: {processed:,}")
        print(f"総実行時間: {total_elapsed:.2f}秒")
        print(f"平均計算時間: {stats['total_time']/processed:.6f}秒/パターン" if processed > 0 else "N/A")
        
        print(f"\n正のパーマネント: {stats['positive_count']:,}")
        if stats['positive_count'] > 0:
            print(f"  最小正値: {stats['min_positive']}")
            print(f"  最大正値: {stats['max_positive']}")
        
        print(f"負のパーマネント: {stats['negative_count']:,}")
        if stats['negative_count'] > 0:
            print(f"  最小負値(絶対値): {stats['min_negative']}")
            print(f"  最大負値(絶対値): {stats['max_negative']}")
        
        print(f"ゼロのパーマネント: {stats['zero_count']:,}")
        
        if rate is not None:
            efficiency = (processed / (processed + skipped_count)) * 100 if (processed + skipped_count) > 0 else 0
            print(f"計算効率: {efficiency:.1f}% (計算実行 / 総パターン)")


if __name__ == "__main__":
    main()