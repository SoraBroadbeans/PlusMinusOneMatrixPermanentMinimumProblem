import numpy as np
from itertools import product, permutations
import time

try:
    from .calc_permanent import permanent, is_pm_one_matrix
except ImportError:
    from calc_permanent import permanent, is_pm_one_matrix

def generate_pm_one_matrices_iterator(n):
    """
    n×n (±1)行列をイテレータで生成（メモリ効率化）
    """
    for entries in product([-1, 1], repeat=n*n):
        yield np.array(entries).reshape(n, n)


def matrix_to_canonical_form(matrix):
    """
    行列を正規形に変換する（対称性削減用）
    行の並び替え、列の並び替え、転置を適用して最小の辞書順表現を求める
    """
    n = matrix.shape[0]
    min_form = matrix.flatten()
    
    # 転置も考慮
    for transpose in [False, True]:
        current_matrix = matrix.T if transpose else matrix
        
        # 行の全順列を試す
        for row_perm in permutations(range(n)):
            row_permuted = current_matrix[list(row_perm), :]
            
            # 列の全順列を試す
            for col_perm in permutations(range(n)):
                col_permuted = row_permuted[:, list(col_perm)]
                flattened = col_permuted.flatten()
                
                # 辞書順で最小のものを保持
                if tuple(flattened) < tuple(min_form):
                    min_form = flattened
    
    return min_form.reshape(n, n)


def get_symmetry_group_size(matrix):
    """
    行列の対称群のサイズを計算する
    同じ正規形を持つ行列の個数を返す
    """
    n = matrix.shape[0]
    canonical = matrix_to_canonical_form(matrix)
    count = 0
    
    # 転置も考慮
    for transpose in [False, True]:
        current_matrix = matrix.T if transpose else matrix
        
        # 行の全順列を試す
        for row_perm in permutations(range(n)):
            row_permuted = current_matrix[list(row_perm), :]
            
            # 列の全順列を試す
            for col_perm in permutations(range(n)):
                col_permuted = row_permuted[:, list(col_perm)]
                
                # 正規形と同じかチェック
                if np.array_equal(matrix_to_canonical_form(col_permuted), canonical):
                    count += 1
    
    return count


def generate_canonical_representatives(n):
    """
    n×n (±1)行列の代表元のみを生成する（対称性削減版）
    """
    seen_canonical = set()
    
    for matrix in generate_pm_one_matrices_iterator(n):
        canonical = matrix_to_canonical_form(matrix)
        canonical_tuple = tuple(canonical.flatten())
        
        if canonical_tuple not in seen_canonical:
            seen_canonical.add(canonical_tuple)
            group_size = get_symmetry_group_size(matrix)
            yield matrix, group_size


def calculate_r_n_optimized(n, verbose=False, max_unique_check=None):
    """
    (±1)行列のパーマネントの値の個数r_nを計算する（最適化版）
    r_n = |{per(A) : A は n×n (±1)行列}|
    論文の定義：パーマネントが取りうる異なる値の個数
    
    Args:
        n: 行列のサイズ
        verbose: 詳細出力
        max_unique_check: 指定された数のユニーク値が見つかったら早期終了
    """
    if verbose:
        print(f"\n=== r_{n}の計算 ===")
        print(f"計算する (±1)行列の総数: 2^{n*n} = {2**(n*n)}")
    
    start_time = time.time()
    
    unique_permanent_values = set()
    permanent_counts = {}
    max_permanent = float('-inf')
    min_permanent = float('inf')
    max_matrix = None
    min_matrix = None
    total_matrices = 2**(n*n)
    seen_patterns = set()
    
    for i, matrix in enumerate(generate_pm_one_matrices_iterator(n)):
        perm_val = permanent(matrix, method='ryser')
        
        # 新しいパターンが見つかったかチェック
        if perm_val not in seen_patterns:
            seen_patterns.add(perm_val)
            if verbose:
                print(f"新しいパーマネント値: {perm_val}")
                print(f"行列:")
                print(matrix)
                print()
        
        unique_permanent_values.add(perm_val)
        permanent_counts[perm_val] = permanent_counts.get(perm_val, 0) + 1
        
        if perm_val > max_permanent:
            max_permanent = perm_val
            max_matrix = matrix.copy()
        
        if perm_val < min_permanent:
            min_permanent = perm_val
            min_matrix = matrix.copy()
        
        if verbose and (i + 1) % 1000 == 0:
            print(f"処理済み: {i + 1}/{total_matrices} 行列, 現在のユニーク値数: {len(unique_permanent_values)}")
        
        # 早期終了チェック
        if max_unique_check and len(unique_permanent_values) >= max_unique_check:
            if verbose:
                print(f"早期終了: {max_unique_check}個のユニーク値が見つかりました（{i+1}/{total_matrices}行列処理後）")
            break
    
    r_n = len(unique_permanent_values)
    unique_values = np.array(sorted(unique_permanent_values))
    counts = np.array([permanent_counts[val] for val in unique_values])
    
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
    
    # 互換性のため全てのパーマネント値のリストを作成（メモリ使用量注意）
    all_permanents = []
    for val, count in zip(unique_values, counts):
        all_permanents.extend([val] * count)
    
    return r_n, unique_values, all_permanents, max_matrix, min_matrix


def calculate_r_n_with_symmetry(n, verbose=False, max_unique_check=None):
    """
    対称性削減を用いた r_n の計算
    代表元のみを計算して計算量を削減する
    """
    if verbose:
        print(f"\n=== r_{n}の計算（対称性削減版） ===")
        print(f"計算する (±1)行列の総数: 2^{n*n} = {2**(n*n)}")
    
    start_time = time.time()
    
    unique_permanent_values = set()
    permanent_counts = {}
    max_permanent = float('-inf')
    min_permanent = float('inf')
    max_matrix = None
    min_matrix = None
    processed_representatives = 0
    total_matrices_represented = 0
    seen_patterns = set()
    
    for matrix, group_size in generate_canonical_representatives(n):
        perm_val = permanent(matrix, method='ryser')
        
        # 新しいパターンが見つかったかチェック
        if perm_val not in seen_patterns:
            seen_patterns.add(perm_val)
            if verbose:
                print(f"新しいパーマネント値: {perm_val}")
                print(f"行列:")
                print(matrix)
                print()
        
        unique_permanent_values.add(perm_val)
        permanent_counts[perm_val] = permanent_counts.get(perm_val, 0) + group_size
        
        if perm_val > max_permanent:
            max_permanent = perm_val
            max_matrix = matrix.copy()
        
        if perm_val < min_permanent:
            min_permanent = perm_val
            min_matrix = matrix.copy()
        
        processed_representatives += 1
        total_matrices_represented += group_size
        
        if verbose and processed_representatives % 100 == 0:
            print(f"処理済み代表元: {processed_representatives}, 表現行列数: {total_matrices_represented}, 現在のユニーク値数: {len(unique_permanent_values)}")
        
        # 早期終了チェック
        if max_unique_check and len(unique_permanent_values) >= max_unique_check:
            if verbose:
                print(f"早期終了: {max_unique_check}個のユニーク値が見つかりました（{processed_representatives}代表元処理後）")
            break
    
    r_n = len(unique_permanent_values)
    unique_values = np.array(sorted(unique_permanent_values))
    counts = np.array([permanent_counts[val] for val in unique_values])
    
    end_time = time.time()
    
    if verbose:
        print(f"\n計算完了 (所要時間: {end_time - start_time:.2f}秒)")
        print(f"処理した代表元: {processed_representatives}")
        print(f"表現された行列数: {total_matrices_represented} / {2**(n*n)}")
        print(f"削減率: {(1 - processed_representatives / (2**(n*n))) * 100:.1f}%")
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
    
    # 互換性のため全てのパーマネント値のリストを作成
    all_permanents = []
    for val, count in zip(unique_values, counts):
        all_permanents.extend([val] * count)
    
    return r_n, unique_values, all_permanents, max_matrix, min_matrix






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
        
        r_n, unique_vals, all_perms, max_matrix, min_matrix = calculate_r_n_optimized(n, verbose)
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
        r_n, unique_vals, _, _, _ = calculate_r_n_optimized(n)
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
        use_symmetry = input("対称性削減を使用しますか？ (y/N): ").lower() == 'y'
        
        if use_symmetry:
            r_n, unique_vals, all_perms, max_matrix, min_matrix = calculate_r_n_with_symmetry(n, verbose=verbose)
        else:
            r_n, unique_vals, all_perms, max_matrix, min_matrix = calculate_r_n_optimized(n, verbose=verbose)
        
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