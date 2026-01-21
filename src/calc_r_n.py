import numpy as np
from itertools import product
try:
    from .calc_permanent import permanent, is_pm_one_matrix
except ImportError:
    from calc_permanent import permanent, is_pm_one_matrix
import time


def estimate_computation_time(n, sample_size=100):
    """
    nサイズの行列での計算時間を推定する
    小さなサンプルでパーマネント計算の平均時間を測定し、全体の見込み時間を計算
    """
    total_matrices = 2 ** (n * n)
    
    if n <= 2:
        return 0.1, total_matrices
    
    sample_matrices = []
    for i, entries in enumerate(product([-1, 1], repeat=n*n)):
        if i >= sample_size:
            break
        matrix = np.array(entries).reshape(n, n)
        sample_matrices.append(matrix)
    
    start_time = time.time()
    for matrix in sample_matrices:
        permanent(matrix, method='ryser')
    end_time = time.time()
    
    avg_time_per_matrix = (end_time - start_time) / len(sample_matrices)
    estimated_total_time = avg_time_per_matrix * total_matrices
    
    return estimated_total_time, total_matrices


def format_time_estimate(seconds):
    """
    秒数を人間が読みやすい形式に変換
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}時間"
    else:
        days = seconds / 86400
        return f"{days:.1f}日"


def generate_all_pm_one_matrices(n):
    """
    n×n (±1)行列をすべて生成する
    """
    matrices = []
    for entries in product([-1, 1], repeat=n*n):
        matrix = np.array(entries).reshape(n, n)
        matrices.append(matrix)
    return matrices


def calculate_r_n(n, verbose=False, show_estimate=True):
    """
    (±1)行列のパーマネントの値の個数r_nを計算する
    r_n = |{per(A) : A は n×n (±1)行列}|
    論文の定義：パーマネントが取りうる異なる値の個数
    """
    if verbose:
        print(f"\n=== r_{n}の計算 ===")
        print(f"計算する (±1)行列の総数: 2^{n*n} = {2**(n*n)}")
    
    if show_estimate and n > 2:
        print(f"\n見込み時間を計算中...")
        estimated_time, total_count = estimate_computation_time(n)
        formatted_time = format_time_estimate(estimated_time)
        print(f"予想計算時間: {formatted_time}")
        print(f"処理する行列数: {total_count:,}個")
        
        if estimated_time > 300:  # 5分以上の場合
            response = input(f"\n計算には約{formatted_time}かかる見込みです。続行しますか？ (y/N): ")
            if response.lower() != 'y':
                print("計算をキャンセルしました。")
                return None, None, None, None, None
    
    start_time = time.time()
    
    permanent_values = []
    max_permanent = float('-inf')
    min_permanent = float('inf')
    max_matrix = None
    min_matrix = None
    
    matrices = generate_all_pm_one_matrices(n)
    
    for i, matrix in enumerate(matrices):
        perm_val = permanent(matrix, method='ryser')
        permanent_values.append(perm_val)
        
        if perm_val > max_permanent:
            max_permanent = perm_val
            max_matrix = matrix.copy()
        
        if perm_val < min_permanent:
            min_permanent = perm_val
            min_matrix = matrix.copy()
        
        if verbose and (i + 1) % 100 == 0:
            unique_so_far = len(set(permanent_values[:i+1]))
            print(f"処理済み: {i + 1}/{len(matrices)} 行列, 現在のユニーク値数: {unique_so_far}")
    
    # ユニークな値の個数を計算
    unique_values, counts = np.unique(permanent_values, return_counts=True)
    r_n = len(unique_values)
    
    end_time = time.time()
    
    if verbose:
        print(f"\n計算完了 (所要時間: {end_time - start_time:.2f}秒)")
        print(f"r_{n} = {r_n} (異なるパーマネント値の個数)")
        print(f"最大パーマネント値: {max_permanent}")
        print(f"最小パーマネント値: {min_permanent}")
        print(f"最大値を与える行列:")
        print(max_matrix)
        print(f"最小値を与える行列:")
        print(min_matrix)
        
        # パーマネント値の分布を表示
        print(f"\nパーマネント値の分布:")
        for val, count in zip(unique_values, counts):
            print(f"  {val}: {count}個")
    
    return r_n, unique_values, permanent_values, max_matrix, min_matrix


def calculate_r_n_range(n_start, n_end, verbose=False):
    """
    n_start から n_end までの r_n を計算する
    """
    results = {}
    
    for n in range(n_start, n_end + 1):
        print(f"\n{'='*50}")
        print(f"n = {n} の計算開始")
        
        if n > 4:
            print(f"警告: n={n} では 2^{n*n} = {2**(n*n)} 個の行列を計算します。")
            response = input("続行しますか？ (y/N): ")
            if response.lower() != 'y':
                print(f"n={n} をスキップします。")
                continue
        
        r_n, unique_vals, all_perms, max_matrix, min_matrix = calculate_r_n(n, verbose, show_estimate=True)
        results[n] = {
            'r_n': r_n,
            'unique_values': unique_vals,
            'max_matrix': max_matrix,
            'min_matrix': min_matrix,
            'all_permanents': all_perms
        }
        
        print(f"結果: r_{n} = {r_n}")
    
    return results


def analyze_known_results():
    """
    既知の結果と比較する（論文からの値）
    r_n = |{per(A) : A は n×n (±1)行列}| （パーマネント値の個数）
    """
    # 論文に基づいた推定値（要検証）
    known_values = {
        1: 2,  # per(A) ∈ {-1, 1} なので r_1 = 2
        2: 3,  # 計算により確認が必要
        # 3以上は論文の理論値を参照
    }
    
    print("\n=== 既知の結果との比較 ===")
    print("注意: r_n は異なるパーマネント値の個数を表します")
    
    for n in sorted(known_values.keys()):
        r_n, unique_vals, _, _, _ = calculate_r_n(n, show_estimate=False)
        known_r_n = known_values.get(n, "不明")
        
        if isinstance(known_r_n, int):
            status = "✓" if r_n == known_r_n else "✗"
            print(f"n={n}: 計算値={r_n}, 既知値={known_r_n} {status}")
        else:
            print(f"n={n}: 計算値={r_n}, 既知値={known_r_n}")
        
        if n <= 3:  # 小さなnについて詳細を表示
            print(f"    異なる値: {sorted(unique_vals)}")


if __name__ == "__main__":
    print("(±1)行列のパーマネント値の個数 r_n の計算")
    print("r_n = |{per(A) : A は n×n (±1)行列}|")
    print("="*50)
    
    # 既知の結果を検証
    analyze_known_results()
    
    # ユーザー入力で計算
    try:
        n = int(input("\nn の値を入力してください (1-4推奨): "))
        if n <= 0:
            raise ValueError("nは正の整数である必要があります")
        
        verbose = input("詳細出力しますか？ (y/N): ").lower() == 'y'
        
        r_n, unique_vals, all_perms, max_matrix, min_matrix = calculate_r_n(n, verbose=verbose)
        
        print(f"\n最終結果:")
        print(f"r_{n} = {r_n} (異なるパーマネント値の個数)")
        print(f"パーマネント値の範囲: {min(unique_vals)} ～ {max(unique_vals)}")
        print(f"すべての値: {sorted(unique_vals)}")
        
        if verbose:
            print(f"\n最大パーマネント値を与える行列:")
            print(max_matrix)
            print(f"\n最小パーマネント値を与える行列:")
            print(min_matrix)
        
    except KeyboardInterrupt:
        print("\n計算を中断しました。")
    except Exception as e:
        print(f"エラー: {e}")