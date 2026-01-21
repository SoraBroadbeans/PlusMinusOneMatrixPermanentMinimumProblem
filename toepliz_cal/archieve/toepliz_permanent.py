import numpy as np
import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from calc_permanent import permanent

def create_toeplitz_matrix_from_set(n, S):
    """
    T_{n,S} 形式の(+1,-1)-トープリッツ行列を作成
    (i,j)要素は j-i ∈ S のとき +1、そうでなければ -1
    
    Args:
        n: 行列のサイズ
        S: 集合 (リストまたはセット)
    
    Returns:
        np.ndarray: nxnの(+1,-1)-トープリッツ行列
    """
    matrix = -np.ones((n, n), dtype=int)  # デフォルトを-1に変更
    
    for i in range(n):
        for j in range(n):
            if (j - i) in S:
                matrix[i, j] = 1  # S内の要素では+1に変更
    
    return matrix

def create_toepliz_matrix(n, T):
    """
    従来の形式のnxnトープリッツ行列を作成（下位互換性のため）
    
    Args:
        n: 行列のサイズ
        T: トープリッツ行列の第一行のベクトル（長さnのリスト）
    
    Returns:
        np.ndarray: nxnのトープリッツ行列
    """
    if len(T) != n:
        raise ValueError(f"Tの長さは{n}である必要があります")
    
    matrix = np.zeros((n, n), dtype=int)
    
    for i in range(n):
        for j in range(n):
            # トープリッツ行列では、i-j が同じ対角線上の要素は同じ値
            if j - i >= 0:
                # 上側の対角線（j >= i）
                matrix[i, j] = T[j - i]
            else:
                # 下側の対角線（j < i）
                # 対称性を仮定してT[i-j]を使用
                if i - j < len(T):
                    matrix[i, j] = T[i - j]
                else:
                    matrix[i, j] = 0  # 範囲外は0
    
    return matrix

def calculate_toeplitz_permanent_from_set(n, S, verbose=False):
    """
    T_{n,S} 形式のトープリッツ行列のパーマネントを計算
    
    Args:
        n: 行列のサイズ
        S: 集合 (j-i ∈ S のとき (i,j) 要素は -1)
        verbose: 詳細出力フラグ
    
    Returns:
        tuple: (パーマネント値, 計算時間)
    """
    start_time = time.time()
    
    matrix = create_toeplitz_matrix_from_set(n, S)
    
    if verbose:
        print(f"T_{{{n},S}} トープリッツ行列:")
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

def calculate_toepliz_permanent(n, T, verbose=False):
    """
    従来形式のトープリッツ行列のパーマネントを計算（下位互換性のため）
    
    Args:
        n: 行列のサイズ
        T: トープリッツ行列の第一行のベクトル（長さnのリスト）
        verbose: 詳細出力フラグ
    
    Returns:
        tuple: (パーマネント値, 計算時間)
    """
    start_time = time.time()
    
    matrix = create_toepliz_matrix(n, T)
    
    if verbose:
        print(f"トープリッツ行列 (n={n}):")
        print(f"T = {T}")
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

def parse_set_notation(notation):
    """
    T_{n,S} 形式の記法を解析する
    
    Args:
        notation: "T_7{-6,-1..7}" や "T_5{0,1,2}" のような記法文字列
    
    Returns:
        tuple: (n, S) - nは行列サイズ、Sは集合
    """
    import re
    
    # T_{n}{...} または T_n{...} の形式をパース
    match = re.match(r'T_\{?(\d+)\}?\{([^}]+)\}', notation)
    if not match:
        raise ValueError(f"無効な集合記法です: {notation}")
    
    n = int(match.group(1))
    set_content = match.group(2).strip()
    
    S = set()
    
    # カンマで分割して各要素を処理
    elements = [elem.strip() for elem in set_content.split(',')]
    
    for elem in elements:
        # 範囲記法 (例: -1..7, 2..5)
        range_match = re.match(r'(-?\d+)\.\.(-?\d+)', elem)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if end < start:
                raise ValueError(f"範囲が無効です: {start}..{end}")
            S.update(range(start, end + 1))
        else:
            # 単一の数値
            try:
                S.add(int(elem))
            except ValueError:
                raise ValueError(f"無効な集合要素です: {elem}")
    
    return n, S

def parse_matrix_notation(notation):
    """
    T_n(a..b) のような従来記法を解析する（下位互換性のため）
    
    Args:
        notation: "T_7(2..4)" のような記法文字列
    
    Returns:
        tuple: (n, values) - nは行列サイズ、valuesは第一行の値のリスト
    """
    import re
    
    # T_n(a..b) の形式をパース
    match = re.match(r'T_(\d+)\((\d+)\.\.(\d+)\)', notation)
    if match:
        n = int(match.group(1))
        start = int(match.group(2))
        end = int(match.group(3))
        
        if end < start:
            raise ValueError(f"範囲が無効です: {start}..{end}")
        
        # 範囲から値を生成
        values = list(range(start, end + 1))
        
        # 必要に応じてパディングまたはトリミング
        if len(values) < n:
            # 不足分は最後の値で埋める
            values.extend([end] * (n - len(values)))
        elif len(values) > n:
            # 余分な要素をトリミング
            values = values[:n]
        
        return n, values
    
    # T_n(a,b,c,...) の形式もサポート
    match = re.match(r'T_(\d+)\(([0-9,\s]+)\)', notation)
    if match:
        n = int(match.group(1))
        values_str = match.group(2)
        values = [int(x.strip()) for x in values_str.split(',')]
        
        if len(values) != n:
            raise ValueError(f"値の個数({len(values)})がn({n})と一致しません")
        
        return n, values
    
    raise ValueError(f"無効な記法です: {notation}")

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
    print("=== トープリッツ行列パーマネント計算ツール ===")
    print("\n使用例:")
    print("  T_7{-6,-1..7}     : T_{7,S} 形式の(+1,-1)行列 (論文形式)")
    print("  T_5{0,1,2}        : T_{5,{0,1,2}} 形式")
    print("  T_7(2..4)         : 従来形式、第一行が [2,3,4,4,4,4,4]")
    print("  T_5(1,2,3,0,1)    : 従来形式、第一行が [1,2,3,0,1]")
    
    try:
        # 記法による入力
        notation = input("\n行列記法を入力してください: ").strip()
        
        if notation:
            # 集合記法を優先して試行
            try:
                n, S = parse_set_notation(notation)
                print(f"\n入力された値: n={n}, S={sorted(S)}")
                
                # T_{n,S} 形式でパーマネント計算
                perm, calc_time = calculate_toeplitz_permanent_from_set(n, S, verbose=True)
                
                # Kräuter理論値と比較
                krauter_value = calculate_krauter_theoretical_value(n)
                print(f"\nKräuter理論値: {krauter_value}")
                print(f"実際の値: {perm} (絶対値: {abs(perm)})")
                print(f"一致: {'Yes' if abs(perm) == krauter_value else 'No'}")
                print(f"総計算時間: {calc_time:.6f}秒")
                
            except ValueError:
                # 従来記法で試行
                n, T = parse_matrix_notation(notation)
                print(f"\n入力された値: n={n}, T={T}")
                
                # 従来形式でパーマネント計算
                perm, calc_time = calculate_toepliz_permanent(n, T, verbose=True)
                
                # Kräuter理論値と比較
                krauter_value = calculate_krauter_theoretical_value(n)
                print(f"\nKräuter理論値: {krauter_value}")
                print(f"実際の値: {perm} (絶対値: {abs(perm)})")
                print(f"一致: {'Yes' if abs(perm) == krauter_value else 'No'}")
                print(f"総計算時間: {calc_time:.6f}秒")
        else:
            # 従来の方法（個別入力）
            n = int(input("行列サイズ n を入力してください: "))
            if n <= 0:
                print("エラー: nは正の整数である必要があります")
                sys.exit(1)
            
            print(f"トープリッツ行列の第一行の要素を{n}個入力してください:")
            T = []
            for i in range(n):
                value = int(input(f"T[{i}] = "))
                T.append(value)
            
            print(f"\n入力された値: n={n}, T={T}")
            
            # パーマネント計算
            perm, calc_time = calculate_toepliz_permanent(n, T, verbose=True)
            
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