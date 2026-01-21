import numpy as np
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from calc_permanent import permanent

def create_circulant_matrix_from_set(n, S):
    """
    C_{n,S} 形式の(+1,-1)-巡回行列を作成
    第一行の要素iが S に含まれるとき +1、そうでなければ -1
    各行は前の行の左循環シフト
    
    Args:
        n: 行列のサイズ
        S: 集合 (リストまたはセット)
    
    Returns:
        np.ndarray: nxnの(+1,-1)-巡回行列
    """
    # 第一行を作成: i ∈ S なら +1、そうでなければ -1
    first_row = np.array([1 if i in S else -1 for i in range(n)], dtype=int)
    
    matrix = np.zeros((n, n), dtype=int)
    
    for i in range(n):
        for j in range(n):
            # C[i,j] = c[(j-i) mod n] (第一行の循環シフト)
            matrix[i, j] = first_row[(j - i) % n]
    
    return matrix

def calculate_circulant_permanent_from_set(n, S, verbose=False):
    """
    C_{n,S} 形式の巡回行列のパーマネントを計算
    
    Args:
        n: 行列のサイズ
        S: 集合 (第一行でi ∈ S のとき (0,i) 要素は +1)
        verbose: 詳細出力フラグ
    
    Returns:
        tuple: (パーマネント値, 計算時間)
    """
    start_time = time.time()
    
    matrix = create_circulant_matrix_from_set(n, S)
    
    if verbose:
        print(f"C_{{{n},S}} 巡回行列:")
        print(f"S = {sorted(S)}")
        print(f"行列:\n{matrix}")
    
    perm_calculation_start = time.time()
    perm_value = permanent(matrix, method='ryser', verbose=verbose)
    perm_calculation_time = time.time() - perm_calculation_start
    
    total_time = time.time() - start_time
    
    if verbose:
        print(f"パーマネント値: {perm_value}")
        print(f"パーマネント計算時間: {perm_calculation_time:.6f}秒")
        print(f"総計算時間: {total_time:.6f}秒")
    
    return perm_value, total_time

def parse_circulant_set_notation(notation):
    """
    C_{n,S} 形式の記法を解析する
    
    Args:
        notation: "C_20{0,1,5}" や "C_7{2..5}" のような記法文字列
    
    Returns:
        tuple: (n, S) - nは行列サイズ、Sは集合
    """
    import re
    
    # C_{n}{...} または C_n{...} の形式をパース
    match = re.match(r'C_\{?(\d+)\}?\{([^}]+)\}', notation)
    if not match:
        raise ValueError(f"無効な集合記法です: {notation}")
    
    n = int(match.group(1))
    set_content = match.group(2).strip()
    
    S = set()
    
    # カンマで分割して各要素を処理
    elements = [elem.strip() for elem in set_content.split(',')]
    
    for elem in elements:
        # 範囲記法 (例: 2..5, 0..3)
        range_match = re.match(r'(-?\d+)\.\.(-?\d+)', elem)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if end < start:
                raise ValueError(f"範囲が無効です: {start}..{end}")
            # 巡回行列では0からn-1の範囲内でなければならない
            for i in range(start, end + 1):
                if 0 <= i < n:
                    S.add(i)
        else:
            # 単一の数値
            try:
                val = int(elem)
                if 0 <= val < n:
                    S.add(val)
            except ValueError:
                raise ValueError(f"無効な集合要素です: {elem}")
    
    return n, S

def calculate_krauter_theoretical_value(n):
    """
    Kräuter予想による理論値を計算
    2^{n - ⌊log₂(n + 1)⌋}
    
    Args:
        n: 行列のサイズ
    
    Returns:
        int: Kräuter予想による理論値
    """
    import math
    
    if n <= 0:
        raise ValueError("nは正の整数である必要があります")
    
    exponent = n - math.floor(math.log2(n + 1))
    theoretical_value = 2 ** exponent
    
    return int(theoretical_value)

if __name__ == "__main__":
    print("=== 巡回行列パーマネント計算ツール ===")
    print("\n使用例:")
    print("  C_20{0,1,5}       : C_{20,{0,1,5}} 形式の(+1,-1)行列")
    print("  C_7{2..5}         : C_{7,{2,3,4,5}} 形式")
    print("  C_10{0,2,4,6,8}   : C_{10,{0,2,4,6,8}} 形式")
    
    try:
        # 記法による入力
        notation = input("\n行列記法を入力してください: ").strip()
        
        if notation:
            n, S = parse_circulant_set_notation(notation)
            print(f"\n入力された値: n={n}, S={sorted(S)}")
            
            # C_{n,S} 形式でパーマネント計算
            perm, calc_time = calculate_circulant_permanent_from_set(n, S, verbose=True)
            
            # Kräuter理論値と比較
            krauter_value = calculate_krauter_theoretical_value(n)
            print(f"\nKräuter理論値: {krauter_value}")
            print(f"実際の値: {perm} (絶対値: {abs(perm)})")
            print(f"一致: {'Yes' if abs(perm) == krauter_value else 'No'}")
            print(f"総計算時間: {calc_time:.6f}秒")
        else:
            # 個別入力
            n = int(input("行列サイズ n を入力してください: "))
            if n <= 0:
                print("エラー: nは正の整数である必要があります")
                sys.exit(1)
            
            print(f"第一行で+1にするインデックス位置を入力してください (0から{n-1}の範囲):")
            S_input = input("カンマ区切りで入力 (例: 0,1,3,5): ").strip()
            
            S = set()
            if S_input:
                for idx_str in S_input.split(','):
                    idx = int(idx_str.strip())
                    if 0 <= idx < n:
                        S.add(idx)
                    else:
                        print(f"警告: インデックス {idx} は範囲外です (0-{n-1})")
            
            print(f"\n入力された値: n={n}, S={sorted(S)}")
            
            # パーマネント計算
            perm, calc_time = calculate_circulant_permanent_from_set(n, S, verbose=True)
            
            # Kräuter理論値と比較
            krauter_value = calculate_krauter_theoretical_value(n)
            print(f"\nKräuter理論値: {krauter_value}")
            print(f"実際の値: {perm} (絶対値: {abs(perm)})")
            print(f"一致: {'Yes' if abs(perm) == krauter_value else 'No'}")
            print(f"総計算時間: {calc_time:.6f}秒")
        
    except ValueError as e:
        print(f"エラー: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n計算を中断しました")
        sys.exit(0)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)