#!/usr/bin/env python3
"""
トープリッツ行列パーマネント総合計算ツール

T_n のすべてのパターンを生成し、ストリーミング処理で1つずつ計算する。
"""

import sys
import os
import time
import random
from datetime import datetime
from itertools import combinations

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from toepliz_permanent import create_toeplitz_matrix_from_set, calculate_toeplitz_permanent_from_set
from toepliz_permanent import calculate_krauter_theoretical_value


def generate_all_toeplitz_patterns(n):
    """
    T_n のすべての可能な集合Sパターンを生成（ジェネレータ）
    
    Args:
        n: 行列のサイズ
        
    Yields:
        set: 各集合S
    """
    # 可能なインデックス範囲: -(n-1) から (n-1)
    possible_indices = list(range(-(n-1), n))
    
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
        # T_{n,S} 行列を作成
        matrix = create_toeplitz_matrix_from_set(n, S)
        
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
        perm_value, calc_time = calculate_toeplitz_permanent_from_set(n, S, verbose=False)
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
        
        # T_n{S} 形式で表示
        t_display = f"T_{n}{{{S if S else '∅'}}}"
        
        # スキップされた場合の表示
        if 'skipped' in result:
            ratio = result['ones_ratio']
            threshold = result['rate_threshold']
            if verbose:
                if isinstance(threshold, tuple):
                    rate_lower, rate_upper = threshold
                    print(f"パターン {pattern:,}: {t_display} → スキップ (1の比率: {ratio:.3f} <= {rate_lower:.1f} または >= {rate_upper:.1f})")
                else:
                    print(f"パターン {pattern:,}: {t_display} → スキップ (1の比率: {ratio:.3f} > {threshold:.3f})")
            else:
                print(f"{pattern:,}: {t_display} → スキップ")
            return
        
        # 通常の計算結果表示
        perm = result['permanent']
        time_taken = result['calc_time']
        ones_ratio = result.get('ones_ratio', 0.0)
        
        if verbose:
            print(f"パターン {pattern:,}: {t_display} → パーマネント = {perm} (1の比率: {ones_ratio:.3f}, {time_taken:.6f}秒)")
        else:
            # 簡潔表示
            print(f"{pattern:,}: {t_display} → {perm} (r={ones_ratio:.3f})")
    else:
        print(f"パターン {result['pattern_num']:,}: エラー - {result['error']}")


def calculate_total_patterns(n):
    """
    総パターン数を計算
    T_n の場合、可能なインデックス範囲は -(n-1) から (n-1) まで
    つまり 2n-1 個のインデックスがある
    各インデックスを含むか含まないかで 2^(2n-1) 通りの集合S
    """
    # 可能なインデックス数: -(n-1), -(n-2), ..., -1, 0, 1, ..., n-2, n-1
    # これは2n-1個
    num_indices = 2 * n - 1
    return 2 ** num_indices


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


def generate_random_toeplitz_set(n, rate, max_attempts=10000):
    """
    rateの制約を満たすランダムなトープリッツ集合Sを生成
    
    Args:
        n: 行列のサイズ
        rate: 1の要素の比率制約。単一値(上限のみ)またはタプル(下限, 上限)
        max_attempts: 最大試行回数
        
    Returns:
        set: 生成された集合S
    """
    possible_indices = list(range(-(n-1), n))
    
    for attempt in range(max_attempts):
        # ランダムに集合Sを生成
        subset_size = random.randint(0, len(possible_indices))
        S = set(random.sample(possible_indices, subset_size))
        
        # 行列を作成して1の比率をチェック
        matrix = create_toeplitz_matrix_from_set(n, S)
        ones_ratio = calculate_matrix_ones_ratio(matrix)
        
        # 生成したTを出力
        print(f"  試行 {attempt + 1}: S = {sorted(S) if S else '∅'}, 1の比率 = {ones_ratio:.3f}", end="")
        
        # rate制約をチェック
        if isinstance(rate, tuple):
            rate_lower, rate_upper = rate
            if rate_lower < ones_ratio < rate_upper:
                print(" → 制約を満たすため採用")
                return S
            else:
                print(" → 制約を満たさない")
        else:
            if ones_ratio <= rate:
                print(" → 制約を満たすため採用")
                return S
            else:
                print(" → 制約を満たさない")
    
    # 制約を満たす集合が見つからない場合は空集合を返す
    print(f"警告: {max_attempts}回の試行で制約を満たす集合が見つかりませんでした。空集合を使用します。")
    return set()


def generate_neighborhood(S, n, checknum):
    """
    集合Sの近傍解を生成
    
    Args:
        S: 現在の集合
        n: 行列のサイズ
        checknum: 変更する要素数
        
    Returns:
        set: 近傍解の集合S'
    """
    possible_indices = list(range(-(n-1), n))
    S_new = S.copy()
    
    # checknum個の要素をランダムに変更
    for _ in range(checknum):
        # ランダムにインデックスを選択
        index = random.choice(possible_indices)
        
        # 集合に含まれている場合は削除、含まれていない場合は追加
        if index in S_new:
            S_new.remove(index)
        else:
            S_new.add(index)
    
    return S_new


def create_result_directory():
    """
    resultディレクトリを作成
    
    Returns:
        str: resultディレクトリのパス
    """
    result_dir = os.path.join(os.path.dirname(__file__), 'result')
    os.makedirs(result_dir, exist_ok=True)
    return result_dir


def create_output_filename(n, result_dir):
    """
    出力ファイル名を作成（焼きなまし法用）
    
    Args:
        n: 行列のサイズ
        result_dir: resultディレクトリのパス
        
    Returns:
        str: 出力ファイルのパス
    """
    now = datetime.now()
    filename = f"n{n}-toepliz-SimulatedAnnealing-{now.strftime('%y-%m-%d-%H-%M-%S')}.txt"
    # ファイル名の/を-に置換（ファイルシステム対応）
    filename = filename.replace('/', '-').replace(':', '-')
    return os.path.join(result_dir, filename)


def create_random_output_filename(n, result_dir):
    """
    出力ファイル名を作成（ランダム探索用）
    
    Args:
        n: 行列のサイズ
        result_dir: resultディレクトリのパス
        
    Returns:
        str: 出力ファイルのパス
    """
    now = datetime.now()
    filename = f"n{n}-toepliz-random-{now.strftime('%y-%m-%d-%H-%M-%S')}.txt"
    # ファイル名の/を-に置換（ファイルシステム対応）
    filename = filename.replace('/', '-').replace(':', '-')
    return os.path.join(result_dir, filename)


def log_result(filename, iteration, S, permanent, ones_ratio, accepted, timestamp):
    """
    結果をファイルに記録
    
    Args:
        filename: 出力ファイル名
        iteration: 反復回数
        S: 集合
        permanent: パーマネント値
        ones_ratio: 1の比率
        accepted: 受諾/棄却
        timestamp: タイムスタンプ
    """
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"Iteration {iteration}: S={sorted(S) if S else '∅'}, "
                f"Permanent={permanent}, Ones_ratio={ones_ratio:.3f}, "
                f"Accepted={accepted}, Time={timestamp}\n")


def random_search_mode(n, rate):
    """
    ランダム探索モード
    
    Args:
        n: 行列のサイズ
        rate: 1の要素の比率制約
    """
    print("\n=== ランダム探索モード ===")
    
    # resultディレクトリ作成
    result_dir = create_result_directory()
    output_file = create_random_output_filename(n, result_dir)
    
    # 初期解の生成
    print("最初の有効なパーマネント値を探索中...")
    current_best = None
    best_S = None
    iteration = 0
    
    # 最初の有効な解を見つけるまでループ
    while current_best is None:
        S = generate_random_toeplitz_set(n, rate)
        matrix = create_toeplitz_matrix_from_set(n, S)
        ones_ratio = calculate_matrix_ones_ratio(matrix)
        
        # rate制約チェック
        rate_satisfied = True
        if rate is not None:
            if isinstance(rate, tuple):
                rate_lower, rate_upper = rate
                if ones_ratio <= rate_lower or ones_ratio >= rate_upper:
                    rate_satisfied = False
            else:
                if ones_ratio > rate:
                    rate_satisfied = False
        
        if rate_satisfied:
            # パーマネント計算
            perm_value, calc_time = calculate_toeplitz_permanent_from_set(n, S, verbose=False)
            current_best = perm_value
            best_S = S.copy()
            
            # 初期解を出力・記録
            print(f"\n初期解:")
            print(f"S = {sorted(S) if S else '∅'}")
            print(f"パーマネント = {current_best}")
            print(f"1の比率 = {ones_ratio:.3f}")
            print(f"絶対値 = {abs(current_best)}")
            
            # ファイルに記録
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Random Search Results for n={n}\n")
                f.write(f"Rate constraint: {rate}\n")
                f.write(f"Start time: {timestamp}\n")
                f.write(f"="*50 + "\n")
            
            log_result(output_file, iteration, S, current_best, ones_ratio, "Initial", timestamp)
            print(f"\n結果ファイル: {output_file}")
            break
    
    # ランダム探索ループ
    improvements = 0
    
    try:
        print("\nランダム探索開始 (Ctrl+Cで終了)...")
        
        while True:
            iteration += 1
            
            # ランダムな集合Sを生成
            S_new = generate_random_toeplitz_set(n, rate)
            
            # 新しい解の行列作成・rate制約チェック
            matrix_new = create_toeplitz_matrix_from_set(n, S_new)
            ones_ratio_new = calculate_matrix_ones_ratio(matrix_new)
            
            # rate制約チェック
            rate_satisfied = True
            if rate is not None:
                if isinstance(rate, tuple):
                    rate_lower, rate_upper = rate
                    if ones_ratio_new <= rate_lower or ones_ratio_new >= rate_upper:
                        rate_satisfied = False
                else:
                    if ones_ratio_new > rate:
                        rate_satisfied = False
            
            if rate_satisfied:
                # パーマネント計算
                new_perm, calc_time = calculate_toeplitz_permanent_from_set(n, S_new, verbose=False)
                
                # 改善判定: |new_perm| < |current_best|
                if abs(new_perm) < abs(current_best):
                    # より良い解を発見
                    current_best = new_perm
                    best_S = S_new.copy()
                    improvements += 1
                    
                    print(f"\nIteration {iteration}: 改善発見!")
                    print(f"S = {sorted(S_new) if S_new else '∅'}")
                    print(f"パーマネント = {new_perm}")
                    print(f"1の比率 = {ones_ratio_new:.3f}")
                    print(f"絶対値 = {abs(new_perm)} (前回: {abs(current_best) if current_best != new_perm else 'N/A'})")
                    print(f"改善回数: {improvements}")
                    
                    # ログ記録
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_result(output_file, iteration, S_new, new_perm, ones_ratio_new, "Yes", timestamp)
            
            # 進捗表示（1000回ごと）
            if iteration % 1000 == 0:
                print(f"進捗: {iteration} iterations, 改善回数: {improvements}, 現在の|perm|: {abs(current_best)}")
    
    except KeyboardInterrupt:
        print("\n\nランダム探索が中断されました。")
    
    # 最終結果
    print(f"\n{'='*60}")
    print("=== ランダム探索結果 ===")
    print(f"総反復回数: {iteration}")
    print(f"改善回数: {improvements}")
    print(f"最終解:")
    print(f"  S = {sorted(best_S) if best_S else '∅'}")
    print(f"  パーマネント = {current_best}")
    print(f"  絶対値 = {abs(current_best)}")
    print(f"結果ファイル: {output_file}")


def simulated_annealing_mode(n, rate):
    """
    焼きなまし法モード
    
    Args:
        n: 行列のサイズ
        rate: 1の要素の比率制約
    """
    print("\n=== 焼きなまし法モード ===")
    
    # checknum入力
    try:
        checknum = int(input("checknum (近傍生成時に変更する要素数): "))
        if checknum <= 0:
            print("エラー: checknumは正の整数である必要があります")
            return
    except ValueError:
        print("エラー: 有効な整数を入力してください")
        return
    
    # 初期集合S生成 - 直接数値入力を受け付け
    indices_input = input(f"初期T設定 (範囲: {-(n-1)} to {n-1}, カンマ区切り, 空白でランダム生成): ").strip()
    
    if indices_input:
        # 手動入力の場合
        try:
            indices = [int(x.strip()) for x in indices_input.split(',')]
            # 範囲チェック
            valid_range = list(range(-(n-1), n))
            for idx in indices:
                if idx not in valid_range:
                    print(f"エラー: インデックス {idx} は範囲外です")
                    return
            S = set(indices)
            print(f"手動入力された集合S: {sorted(S)}")
        except ValueError:
            print("エラー: 有効な整数を入力してください")
            return
    else:
        # ランダム生成の場合
        print("ランダムに初期集合Sを生成しています...")
        S = generate_random_toeplitz_set(n, rate)
    
    # resultディレクトリ作成
    result_dir = create_result_directory()
    output_file = create_output_filename(n, result_dir)
    
    # 初期解の評価
    matrix = create_toeplitz_matrix_from_set(n, S)
    ones_ratio = calculate_matrix_ones_ratio(matrix)
    
    # rate制約チェック
    if rate is not None:
        should_skip = False
        if isinstance(rate, tuple):
            rate_lower, rate_upper = rate
            if ones_ratio <= rate_lower or ones_ratio >= rate_upper:
                should_skip = True
        else:
            if ones_ratio > rate:
                should_skip = True
        
        if should_skip:
            print(f"初期解がrate制約を満たしません (ratio: {ones_ratio:.3f})")
            return
    
    # 初期パーマネント計算
    current_perm, calc_time = calculate_toeplitz_permanent_from_set(n, S, verbose=False)
    current_S = S.copy()
    
    # 初期解を出力・記録
    print(f"\n初期解:")
    print(f"S = {sorted(S) if S else '∅'}")
    print(f"パーマネント = {current_perm}")
    print(f"1の比率 = {ones_ratio:.3f}")
    print(f"計算時間 = {calc_time:.6f}秒")
    
    # ファイルに記録
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Simulated Annealing Results for n={n}\n")
        f.write(f"Rate constraint: {rate}\n")
        f.write(f"Checknum: {checknum}\n")
        f.write(f"Start time: {timestamp}\n")
        f.write(f"="*50 + "\n")
    
    log_result(output_file, 0, S, current_perm, ones_ratio, "Initial", timestamp)
    
    print(f"\n結果ファイル: {output_file}")
    print(f"初期解の絶対値: |{current_perm}| = {abs(current_perm)}")
    
    # 焼きなまし法ループ
    iteration = 1
    improvements = 0
    
    try:
        print("\n焼きなまし法開始 (Ctrl+Cで終了)...")
        
        while True:
            # 近傍解生成
            S_new = generate_neighborhood(current_S, n, checknum)
            
            # 新しい解の行列作成・rate制約チェック
            matrix_new = create_toeplitz_matrix_from_set(n, S_new)
            ones_ratio_new = calculate_matrix_ones_ratio(matrix_new)
            
            # rate制約チェック
            rate_satisfied = True
            if rate is not None:
                if isinstance(rate, tuple):
                    rate_lower, rate_upper = rate
                    if ones_ratio_new <= rate_lower or ones_ratio_new >= rate_upper:
                        rate_satisfied = False
                else:
                    if ones_ratio_new > rate:
                        rate_satisfied = False
            
            # 生成したTを表示
            print(f"Iteration {iteration}: 生成したT_{n}")
            print(f"S = {sorted(S_new) if S_new else '∅'}")
            print(f"1の比率 = {ones_ratio_new:.3f}")
            
            if not rate_satisfied:
                print("  → rate制約を満たさないため、パーマネント計算をスキップ")
            else:
                # パーマネント計算（rate制約を満たす場合のみ）
                new_perm, calc_time = calculate_toeplitz_permanent_from_set(n, S_new, verbose=False)
                print(f"パーマネント = {new_perm}")
                # 受諾判定: |new_perm| < |current_perm|
                if abs(new_perm) < abs(current_perm):
                    # より良い解を受諾
                    current_S = S_new.copy()
                    current_perm = new_perm
                    accepted = "Yes"
                    improvements += 1
                    
                    print(f"  → 改善発見! (|{new_perm}| < |{current_perm}|)")
                    print(f"改善回数: {improvements}")
                    
                    # ログ記録
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    log_result(output_file, iteration, S_new, new_perm, ones_ratio_new, accepted, timestamp)
                else:
                    accepted = "No"
            
            iteration += 1
            
            # 進捗表示（100回ごと）
            if iteration % 100 == 0:
                print(f"進捗: {iteration} iterations, 改善回数: {improvements}, 現在の|perm|: {abs(current_perm)}")
    
    except KeyboardInterrupt:
        print("\n\n焼きなまし法が中断されました。")
    
    # 最終結果
    print(f"\n{'='*60}")
    print("=== 焼きなまし法結果 ===")
    print(f"総反復回数: {iteration - 1}")
    print(f"改善回数: {improvements}")
    print(f"最終解:")
    print(f"  S = {sorted(current_S) if current_S else '∅'}")
    print(f"  パーマネント = {current_perm}")
    print(f"  絶対値 = {abs(current_perm)}")
    print(f"結果ファイル: {output_file}")


def main():
    """
    メイン関数
    """
    print("=== トープリッツ行列パーマネント総合計算ツール ===")
    print("T_n のすべてのパターンを生成し、ストリーミング処理で計算します。\n")
    
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
    
    # モード選択
    print("\n実行モードを選択してください:")
    print("0: 全パターン計算")
    print("1: 焼きなまし法")
    print("2: ランダム探索")
    
    mode = input("モードを選択 (0/1/2): ").strip()
    if mode == "1":
        simulated_annealing_mode(n, rate)
        return
    elif mode == "2":
        random_search_mode(n, rate)
        return
    
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
        for S in generate_all_toeplitz_patterns(n):
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
        
        # ユニークな値の数の表示を削除（メモリ節約のため）
        
        if rate is not None:
            efficiency = (processed / (processed + skipped_count)) * 100 if (processed + skipped_count) > 0 else 0
            print(f"計算効率: {efficiency:.1f}% (計算実行 / 総パターン)")


if __name__ == "__main__":
    main()