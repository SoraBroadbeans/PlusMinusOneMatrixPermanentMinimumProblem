"""
Kräuter予想検証モジュール
最小正パーマネント値の探索と予想値との比較
"""

import numpy as np
import math
import sys
import os
from collections import defaultdict

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from calc_permanent import permanent
except ImportError:
    print("Error: calc_permanent module not found")
    sys.exit(1)

from toeplitz_generator import generate_all_toeplitz_matrices


def calculate_krauter_conjecture_value(n):
    """
    Kräuter予想値 2^{n - ⌊log₂(n + 1)⌋} を計算
    
    Args:
        n: 行列のサイズ
        
    Returns:
        int: 予想される最小正パーマネント値
    """
    if n <= 0:
        raise ValueError("n must be positive")
    
    exponent = n - math.floor(math.log2(n + 1))
    conjecture_value = 2 ** exponent
    
    return int(conjecture_value)


def search_minimum_positive_permanent(matrices_with_sets, target_value=None, verbose=True, early_termination=True):
    """
    テプリッツ行列の最小正パーマネント値を探索
    
    Args:
        matrices_with_sets: (matrix, S) のタプルのリストまたはジェネレータ
        target_value: 目標値（Kräuter予想値）
        verbose: 詳細出力フラグ
        early_termination: 目標値が見つかったら即座に終了するかどうか
        
    Returns:
        dict: 探索結果
            - min_positive_permanent: 最小正パーマネント値
            - min_matrices: 最小値を持つ行列とSのリスト
            - target_found: 目標値が見つかったかどうか
            - target_matrices: 目標値を持つ行列のリスト
            - permanent_distribution: パーマネント値の分布
            - statistics: 統計情報
            - early_terminated: 早期終了したかどうか
    """
    # ジェネレータかどうかをチェック
    is_generator = hasattr(matrices_with_sets, '__next__')
    
    if verbose:
        print(f"\n=== 最小正パーマネント探索 ===")
        if not is_generator:
            print(f"探索対象行列数: {len(matrices_with_sets):,}")
        else:
            print("ランダムサンプリングモード")
        if target_value:
            print(f"目標値 (Kräuter予想): {target_value}")
        if early_termination and target_value:
            print("早期終了モード: 目標値が見つかったら即座に終了")
    
    min_positive_permanent = float('inf')
    min_matrices = []
    target_matrices = []
    permanent_values = []
    positive_permanents = []
    early_terminated = False
    
    i = 0
    try:
        for matrix, S in matrices_with_sets:
            perm_val = permanent(matrix, method='ryser')
            permanent_values.append(perm_val)
            
            # 正のパーマネント値のみ考慮
            if perm_val > 0:
                positive_permanents.append(perm_val)
                
                # 最小正パーマネント値を更新
                if perm_val < min_positive_permanent:
                    min_positive_permanent = perm_val
                    min_matrices = [(matrix.copy(), S.copy() if hasattr(S, 'copy') else set(S))]
                elif perm_val == min_positive_permanent:
                    min_matrices.append((matrix.copy(), S.copy() if hasattr(S, 'copy') else set(S)))
                
                # 目標値と一致するかチェック
                if target_value and perm_val == target_value:
                    target_matrices.append((matrix.copy(), S.copy() if hasattr(S, 'copy') else set(S)))
                    
                    # 早期終了の条件をチェック
                    if early_termination:
                        early_terminated = True
                        if verbose:
                            print(f"\n🎉 目標値 {target_value} が見つかりました! (行列 #{i+1})")
                            print(f"S = {sorted(S) if S else '∅'}")
                            print("早期終了します。")
                        break
            
            i += 1
            if verbose and i % 100 == 0:
                positive_count = len(positive_permanents)
                current_min = min_positive_permanent if min_positive_permanent != float('inf') else "未発見"
                if is_generator:
                    print(f"進捗: {i:,} 行列処理済み, 正値: {positive_count}, 現在の最小: {current_min}")
                else:
                    total = len(matrices_with_sets)
                    print(f"進捗: {i:,}/{total:,}, 正値: {positive_count}, 現在の最小: {current_min}")
                    
    except StopIteration:
        # ジェネレータが終了
        pass
    except KeyboardInterrupt:
        print("\n処理が中断されました。")
        early_terminated = True
    
    # 統計情報を計算
    statistics = calculate_permanent_statistics(permanent_values, positive_permanents)
    
    # パーマネント値の分布
    permanent_distribution = defaultdict(int)
    for perm_val in permanent_values:
        permanent_distribution[perm_val] += 1
    
    results = {
        'min_positive_permanent': int(min_positive_permanent) if min_positive_permanent != float('inf') else None,
        'min_matrices': min_matrices,
        'target_found': len(target_matrices) > 0,
        'target_matrices': target_matrices,
        'permanent_distribution': dict(permanent_distribution),
        'statistics': statistics,
        'early_terminated': early_terminated
    }
    
    if verbose:
        display_search_results(results, target_value)
    
    return results


def calculate_permanent_statistics(all_permanents, positive_permanents):
    """
    パーマネント値の統計情報を計算
    """
    stats = {
        'total_matrices': len(all_permanents),
        'positive_count': len(positive_permanents),
        'zero_count': all_permanents.count(0),
        'negative_count': len([p for p in all_permanents if p < 0]),
    }
    
    if all_permanents:
        stats['all_min'] = min(all_permanents)
        stats['all_max'] = max(all_permanents)
        stats['all_mean'] = np.mean(all_permanents)
        stats['unique_values'] = len(set(all_permanents))
    
    if positive_permanents:
        stats['positive_min'] = min(positive_permanents)
        stats['positive_max'] = max(positive_permanents)
        stats['positive_mean'] = np.mean(positive_permanents)
        stats['positive_unique'] = len(set(positive_permanents))
    
    return stats


def display_search_results(results, target_value=None):
    """
    探索結果を表示
    """
    stats = results['statistics']
    
    print(f"\n=== 探索結果 ===")
    print(f"総行列数: {stats['total_matrices']:,}")
    if results.get('early_terminated'):
        print("⚡ 早期終了により探索を中断しました")
    print(f"正のパーマネント: {stats['positive_count']:,} ({stats['positive_count']/stats['total_matrices']*100:.1f}%)")
    print(f"ゼロのパーマネント: {stats['zero_count']:,}")
    print(f"負のパーマネント: {stats['negative_count']:,}")
    print(f"ユニークな値の数: {stats['unique_values']}")
    
    if results['min_positive_permanent']:
        min_val = results['min_positive_permanent']
        min_count = len(results['min_matrices'])
        print(f"\n最小正パーマネント値: {min_val}")
        print(f"最小値を持つ行列数: {min_count}")
        
        if target_value:
            if results['target_found']:
                target_count = len(results['target_matrices'])
                print(f"\n🎉 目標値 {target_value} が見つかりました!")
                print(f"目標値を持つ行列数: {target_count}")
                
                if min_val == target_value:
                    print("✅ Kräuter予想が正しい可能性があります")
                elif min_val < target_value:
                    print("❌ Kräuter予想より小さい値が見つかりました（予想に反する結果）")
            else:
                print(f"\n❌ 目標値 {target_value} は見つかりませんでした")
                print(f"実際の最小値 {min_val} は予想値と異なります")
    
    # パーマネント値の分布（上位10個）
    print(f"\nパーマネント値の分布（出現回数順）:")
    sorted_dist = sorted(results['permanent_distribution'].items(), 
                        key=lambda x: x[1], reverse=True)
    for i, (value, count) in enumerate(sorted_dist[:10]):
        percentage = count / stats['total_matrices'] * 100
        print(f"  値 {value}: {count:,} 回 ({percentage:.1f}%)")
        if i == 9 and len(sorted_dist) > 10:
            print(f"  ... (他 {len(sorted_dist) - 10} 種類)")


def display_target_matrices(target_matrices, max_display=3):
    """
    目標値を持つ行列を表示
    """
    if not target_matrices:
        return
    
    print(f"\n目標値を持つ行列 (最大 {max_display} 個表示):")
    
    for i, (matrix, S) in enumerate(target_matrices[:max_display]):
        print(f"\n{i+1}. S = {sorted(S) if S else '∅'}")
        print(matrix)
    
    if len(target_matrices) > max_display:
        print(f"\n... (他 {len(target_matrices) - max_display} 個)")


def verify_krauter_conjecture(n, strategy="sparse", num_samples=None, max_time=None, verbose=True):
    """
    Kräuter予想を検証
    
    Args:
        n: 行列のサイズ
        strategy: テプリッツ行列生成戦略
        num_samples: ランダムサンプリングの場合のサンプル数
        max_time: ランダムサンプリングの場合の最大実行時間（秒）
        verbose: 詳細出力フラグ
        
    Returns:
        dict: 検証結果
    """
    if verbose:
        print(f"\n{'='*50}")
        print(f"Kräuter予想検証 (n={n})")
        print(f"生成戦略: {strategy}")
        if strategy == "random":
            if num_samples:
                print(f"サンプル数: {num_samples:,}")
            if max_time:
                print(f"最大実行時間: {max_time}秒")
        print(f"{'='*50}")
    
    # 予想値を計算
    conjecture_value = calculate_krauter_conjecture_value(n)
    if verbose:
        print(f"予想される最小正パーマネント値: {conjecture_value}")
    
    # テプリッツ行列を生成
    if strategy == "random":
        matrices_with_sets = generate_all_toeplitz_matrices(n, strategy, num_samples, max_time)
    else:
        matrices_with_sets = generate_all_toeplitz_matrices(n, strategy)
    
    # 最小正パーマネントを探索
    results = search_minimum_positive_permanent(
        matrices_with_sets, conjecture_value, verbose, early_termination=True
    )
    
    # 目標値を持つ行列があれば表示
    if results['target_found'] and verbose:
        display_target_matrices(results['target_matrices'])
    
    return results