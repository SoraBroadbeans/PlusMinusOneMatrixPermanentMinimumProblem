#!/usr/bin/env python3
"""
テプリッツ行列パーマネント最小値探索プログラム
Kräuter予想の検証を行う
"""

import sys
import os
import time
import math

# 親ディレクトリのsrcを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from krauter_conjecture import (
    verify_krauter_conjecture, 
    calculate_krauter_conjecture_value,
    display_target_matrices
)
from toeplitz_generator import get_toeplitz_info


def get_random_sampling_params():
    """ランダムサンプリングのサンプル数を取得"""
    print("\nランダムサンプリング設定:")
    while True:
        try:
            num_str = input("サンプル数を入力 (デフォルト: 100000, 無制限: 0): ") or "100000"
            num_samples = int(num_str)
            if num_samples == 0:
                return None  # 無制限
            elif num_samples > 0:
                return num_samples
            else:
                print("正の整数または0を入力してください。")
        except ValueError:
            print("有効な数字を入力してください。")


def get_max_time_params():
    """最大実行時間を取得"""
    while True:
        try:
            time_str = input("最大実行時間（秒）を入力 (デフォルト: 3600, 無制限: 0): ") or "3600"
            max_time = int(time_str)
            if max_time == 0:
                return None  # 無制限
            elif max_time > 0:
                return max_time
            else:
                print("正の整数または0を入力してください。")
        except ValueError:
            print("有効な数字を入力してください。")


def get_user_input():
    """ユーザーから行列サイズnと生成戦略を取得"""
    print("テプリッツ行列パーマネント最小値探索")
    print("=" * 40)
    
    # 行列サイズの入力
    while True:
        try:
            n = int(input("行列サイズ n を入力してください (2以上): "))
            if n >= 2:
                break
            else:
                print("2以上の整数を入力してください。")
        except ValueError:
            print("有効な整数を入力してください。")
    
    # 予想値を表示
    conjecture_value = calculate_krauter_conjecture_value(n)
    print(f"\nKräuter予想値: 2^{{{n} - ⌊log₂({n} + 1)⌋}} = {conjecture_value}")
    
    # 生成戦略の選択
    print("\n生成戦略を選択してください:")
    print("1. sparse   - |S| ≤ n の小さい集合のみ (推奨: n ≤ 6)")
    print("2. symmetric - 対称集合 S = -S のみ")
    print("3. continuous - 連続区間の集合のみ")
    print("4. random   - ランダムサンプリング (推奨: 大きなn)")
    print("5. all       - すべての集合 (警告: n ≤ 4 推奨)")
    
    while True:
        try:
            choice = int(input("選択 (1-5): "))
            strategy_map = {
                1: "sparse",
                2: "symmetric", 
                3: "continuous",
                4: "random",
                5: "all"
            }
            if choice in strategy_map:
                strategy = strategy_map[choice]
                break
            else:
                print("1-5の数字を入力してください。")
        except ValueError:
            print("有効な数字を入力してください。")
    
    # ランダムサンプリングの場合は追加パラメータを取得
    num_samples = None
    max_time = None
    if strategy == "random":
        num_samples = get_random_sampling_params()
        max_time = get_max_time_params()
    
    return n, strategy, num_samples, max_time


def show_estimation(n, strategy, num_samples=None):
    """計算時間と行列数の推定を表示"""
    matrix_count = get_toeplitz_info(n, strategy, num_samples)
    
    print(f"\n=== 計算量推定 ===")
    print(f"生成される行列数: {matrix_count:,}")
    print(f"各パーマネント計算: O(2^{n} × {n}) = O({2**n * n:,})")
    
    # 簡易的な時間推定（経験的な値）
    estimated_time_per_matrix = (2**n * n) / 1000000  # 経験的な係数
    total_estimated_time = estimated_time_per_matrix * matrix_count
    
    if total_estimated_time < 60:
        time_str = f"{total_estimated_time:.1f}秒"
    elif total_estimated_time < 3600:
        time_str = f"{total_estimated_time/60:.1f}分"
    else:
        time_str = f"{total_estimated_time/3600:.1f}時間"
    
    print(f"推定計算時間: {time_str}")
    
    # 警告表示
    if strategy == "random":
        print("ランダムサンプリングでは設定された条件まで実行されます")
        return True
    elif strategy == "all" and n >= 5:
        print("\n⚠️  警告: 'all' 戦略でn≥5は非常に時間がかかります")
        return False
    elif matrix_count > 1000000:
        print(f"\n⚠️  警告: 100万行列以上の処理になります")
        return False
    
    return True


def main():
    """メイン処理"""
    n, strategy, num_samples, max_time = get_user_input()
    
    # 計算量推定
    if not show_estimation(n, strategy, num_samples):
        response = input("\n続行しますか？ (y/N): ")
        if response.lower() != 'y':
            print("処理をキャンセルしました。")
            return
    
    print(f"\n{'='*50}")
    print(f"Kräuter予想検証開始 (n={n}, strategy={strategy})")
    print(f"{'='*50}")
    
    start_time = time.time()
    
    try:
        # Kräuter予想を検証
        results = verify_krauter_conjecture(n, strategy, num_samples, max_time, verbose=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 最終結果の表示
        print(f"\n{'='*50}")
        print(f"最終結果")
        print(f"{'='*50}")
        print(f"総計算時間: {total_time:.2f}秒")
        
        conjecture_value = calculate_krauter_conjecture_value(n)
        min_val = results.get('min_positive_permanent')
        
        if min_val is not None:
            if results['target_found']:
                print(f"✅ 成功: Kräuter予想値 {conjecture_value} を達成する行列が見つかりました")
                print(f"達成行列数: {len(results['target_matrices'])}")
                
                if min_val == conjecture_value:
                    print("🎉 Kräuter予想が正しい可能性が高いです")
                elif min_val < conjecture_value:
                    print(f"⚠️  予想より小さい最小値 {min_val} が見つかりました")
            else:
                print(f"❌ Kräuter予想値 {conjecture_value} を達成する行列は見つかりませんでした")
                print(f"実際の最小正パーマネント値: {min_val}")
                
                if min_val > conjecture_value:
                    print("予想値は過小評価の可能性があります")
        else:
            print("❌ 正のパーマネント値を持つ行列が見つかりませんでした")
        
        # 詳細分析の選択
        if results.get('target_found'):
            response = input("\n目標値を達成した行列を詳細表示しますか？ (y/N): ")
            if response.lower() == 'y':
                display_target_matrices(results['target_matrices'], max_display=5)
    
    except KeyboardInterrupt:
        print("\n\n処理が中断されました。")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


def show_examples():
    """予想値の例を表示"""
    print("\nKräuter予想値の例:")
    for n in range(2, 8):
        conjecture_value = calculate_krauter_conjecture_value(n)
        exponent = n - math.floor(math.log2(n + 1))
        print(f"  n={n}: 2^{{{n} - ⌊log₂({n} + 1)⌋}} = 2^{exponent} = {conjecture_value}")


if __name__ == "__main__":
    # コマンドライン引数で例を表示
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        show_examples()
    else:
        main()