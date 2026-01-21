import numpy as np
from itertools import product
import time


def permanent_ryser(matrix):
    """Ryser法でパーマネントを計算（正しい実装）"""
    n = matrix.shape[0]
    total = 0
    
    # 空集合を除く全ての部分集合について計算
    for subset in range(1, 2 ** n):
        S = [(subset >> j) & 1 for j in range(n)]
        subset_indices = [j for j in range(n) if S[j] == 1]
        
        # 各行について、部分集合Sに含まれる列の要素の和を計算
        prod = 1
        for i in range(n):
            row_sum = sum(matrix[i, j] for j in subset_indices)
            prod *= row_sum
        
        # 符号を計算: (-1)^{n-|S|}
        sign = (-1) ** (n - len(subset_indices))
        total += sign * prod
    
    return int(total)


def generate_incremental_matrices(n):
    """
    全ての(±1)行列を段階的に生成する
    右下から順番に-1を増やしていく方式
    """
    base_matrix = np.ones((n, n), dtype=int)
    
    # 位置のインデックスを右下から順番に生成
    positions = []
    for i in range(n-1, -1, -1):
        for j in range(n-1, -1, -1):
            positions.append((i, j))
    
    # 0個から n*n個まで全ての-1の配置を生成
    for num_negatives in range(n*n + 1):
        # num_negatives個の-1を持つすべての行列を生成
        for neg_positions in combinations(positions, num_negatives):
            matrix = base_matrix.copy()
            for pos in neg_positions:
                matrix[pos] = -1
            yield matrix


def combinations(items, r):
    """組み合わせを生成"""
    if r == 0:
        yield []
        return
    
    for i in range(len(items)):
        for rest in combinations(items[i+1:], r-1):
            yield [items[i]] + rest


def calculate_r_n_incremental(n, verbose=True):
    """
    段階的生成でr_nを計算
    """
    if verbose:
        print(f"n={n}の計算を開始...")
    
    permanent_values = set()
    processed_count = 0
    start_time = time.time()
    seen_patterns = set()
    
    # 段階的に行列を生成・処理
    for matrix in generate_incremental_matrices(n):
        perm = permanent_ryser(matrix)
        
        # 新しいパターンが見つかったかチェック
        if perm not in seen_patterns:
            seen_patterns.add(perm)
            if verbose:
                print(f"新しいパーマネント値: {perm}")
                print(f"行列:")
                print(matrix)
                print()
        
        permanent_values.add(perm)
        processed_count += 1
        
        if verbose and processed_count % 1000 == 0:
            elapsed = time.time() - start_time
            print(f"処理済み: {processed_count}, 異なる値: {len(permanent_values)}, 経過時間: {elapsed:.2f}s")
    
    if verbose:
        total_time = time.time() - start_time
        print(f"完了: 総行列数: {processed_count}, r_{n} = {len(permanent_values)}, 総時間: {total_time:.2f}s")
    
    return len(permanent_values)


def calculate_r_n_optimized(n, early_stop_ratio=0.99, verbose=True):
    """
    最適化版: 新しい値の発見率が低下したら早期終了
    """
    if verbose:
        print(f"n={n}の最適化計算を開始...")
    
    permanent_values = set()
    processed_count = 0
    last_new_count = 0
    check_interval = max(100, 2**(n*n-8))  # 適応的チェック間隔
    seen_patterns = set()
    
    start_time = time.time()
    
    for matrix in generate_incremental_matrices(n):
        perm = permanent_ryser(matrix)
        
        # 新しいパターンが見つかったかチェック
        if perm not in seen_patterns:
            seen_patterns.add(perm)
            if verbose:
                print(f"新しいパーマネント値: {perm}")
                print(f"行列:")
                print(matrix)
                print()
        
        permanent_values.add(perm)
        processed_count += 1
        
        # 定期的に早期終了判定
        if processed_count % check_interval == 0:
            new_values = len(permanent_values) - last_new_count
            discovery_rate = new_values / check_interval
            
            if verbose:
                elapsed = time.time() - start_time
                print(f"処理済み: {processed_count}, 異なる値: {len(permanent_values)}, "
                      f"発見率: {discovery_rate:.4f}, 経過時間: {elapsed:.2f}s")
            
            # 発見率が低下したら早期終了
            if discovery_rate < (1 - early_stop_ratio) / check_interval:
                if verbose:
                    print(f"発見率低下により早期終了 (閾値: {(1-early_stop_ratio)/check_interval:.6f})")
                break
            
            last_new_count = len(permanent_values)
    
    if verbose:
        total_time = time.time() - start_time
        estimated_total = 2**(n*n)
        completion_rate = processed_count / estimated_total * 100
        print(f"完了: 処理率: {completion_rate:.2f}%, r_{n} >= {len(permanent_values)}, 総時間: {total_time:.2f}s")
    
    return len(permanent_values)


if __name__ == "__main__":
    print("段階的計算による(±1)行列のパーマネント値の個数 r_n の計算")
    print("r_n = |{per(A) : A は n×n (±1)行列}|")
    print("="*50)
    
    try:
        n = int(input("\nn の値を入力してください (1-4推奨): "))
        if n <= 0:
            raise ValueError("nは正の整数である必要があります")
        
        verbose = input("詳細出力しますか？ (y/N): ").lower() == 'y'
        
        # 最適化版を使うかどうかを選択
        use_optimized = input("最適化版を使用しますか？ (y/N): ").lower() == 'y'
        
        total_matrices = 2**(n*n)
        print(f"\n総行列数: {total_matrices}")
        
        if use_optimized:
            result = calculate_r_n_optimized(n, verbose=verbose)
            print(f"\n最終結果:")
            print(f"r_{n} >= {result} (最適化版による下限値)")
        else:
            result = calculate_r_n_incremental(n, verbose=verbose)
            print(f"\n最終結果:")
            print(f"r_{n} = {result} (完全計算)")
        
    except KeyboardInterrupt:
        print("\n計算を中断しました。")
    except Exception as e:
        print(f"エラー: {e}")