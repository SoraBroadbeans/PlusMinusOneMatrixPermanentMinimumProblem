#!/usr/bin/env python3
"""
論文用グラフ作成スクリプト（対話形式）

CSVデータから頻度分布グラフを作成する。
visual.md のルールに従って図を生成する。

使用法:
    python plot_graphs.py
    -> CSVファイルのパスを入力
    -> グラフが masterPaper/image に出力される
"""

import os
import sys
import math
import platform
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# PDF保存時の日本語対応
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# macOS用の日本語フォント設定
if platform.system() == 'Darwin':
    plt.rcParams['font.family'] = ['Hiragino Sans', 'AppleGothic', 'sans-serif']
else:
    plt.rcParams['font.family'] = ['IPAexGothic', 'sans-serif']

plt.rcParams['mathtext.fontset'] = 'stix'

# 基本スタイル設定
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['font.size'] = 12
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'

# 出力ディレクトリ（論文用画像フォルダ）
OUTPUT_DIR = '/Users/sorawatanabe/Documents/stone/sim/perm/masterPaper/image'


def load_csv(filepath: str) -> pd.DataFrame:
    """CSVファイルを読み込み、列名を正規化する"""
    df = pd.read_csv(filepath)

    # 列名の正規化
    columns = df.columns.tolist()
    new_columns = []
    for col in columns:
        if col in ['det', 'detの値', 'perm', 'permの値']:
            new_columns.append('value')
        elif col == '頻度':
            new_columns.append('frequency')
        else:
            new_columns.append(col)
    df.columns = new_columns

    return df


def detect_value_type(filepath: str) -> str:
    """CSVファイルから値の種類（perm/det）を推定"""
    with open(filepath, 'r', encoding='utf-8') as f:
        header = f.readline()
    if 'perm' in header.lower():
        return 'perm'
    return 'det'


def extract_n_from_filename(filepath: str) -> int:
    """ファイル名から行列サイズnを抽出"""
    basename = os.path.basename(filepath)
    # random_full_20_1000000_0114_16_07_freq.csv -> 20
    # 6_1225_10_42_summary.csv -> 6
    # frequency_analysis_15.csv -> 15
    parts = basename.replace('.csv', '').split('_')

    for i, part in enumerate(parts):
        if part.isdigit():
            n = int(part)
            if 1 <= n <= 100:  # 妥当なサイズ
                return n
    return 0


def get_krauter_divisor(n: int) -> int:
    """
    Kräuter予想に基づく除数 k(n) を計算
    n = 2^k - 1 の場合: 2^{n - floor(log2(n)) - 1}
    それ以外: 2^{n - floor(log2(n))}
    """
    floor_log2_n = int(math.floor(math.log2(n)))

    # n = 2^k - 1 かどうかチェック
    is_mersenne = (n & (n + 1)) == 0  # n+1 が2のべき乗なら n = 2^k - 1

    if is_mersenne:
        exponent = n - floor_log2_n - 1
    else:
        exponent = n - floor_log2_n

    return 2 ** exponent


def get_det_divisor(n: int) -> int:
    """
    determinant の正規化除数を計算
    d(A) = det(A) / 2^{n-1}
    """
    return 2 ** (n - 1)


def get_nice_ticks(vmin: float, vmax: float, num_ticks: int = 7) -> np.ndarray:
    """
    最大値・最小値から適切な目盛りを生成
    -1000, -500, 0, 500, 1000 のような切りの良い値
    """
    # 範囲を計算
    data_range = vmax - vmin
    if data_range == 0:
        return np.array([vmin])

    # 目盛り間隔の候補
    raw_step = data_range / num_ticks
    # 10のべき乗でスケール
    magnitude = 10 ** np.floor(np.log10(raw_step))
    # 1, 2, 5, 10 の中から選択
    nice_steps = [1, 2, 5, 10]
    normalized = raw_step / magnitude
    step = magnitude * min(nice_steps, key=lambda x: abs(x - normalized))

    # 0を含む範囲で目盛りを生成
    tick_min = np.floor(vmin / step) * step
    tick_max = np.ceil(vmax / step) * step
    ticks = np.arange(tick_min, tick_max + step / 2, step)

    return ticks


def plot_frequency_distribution(
    df: pd.DataFrame,
    n: int,
    value_type: str,
    output_path: str,
    log_scale: bool = False,
    percentile_range: tuple = None,
    x_range: tuple = None,
    use_binning: bool = True,
    n_bins: int = 100,
    use_division: bool = True
):
    """
    頻度分布の棒グラフを作成する
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # データをコピーしてソート
    df_sorted = df.sort_values('value').copy()

    # 軸ラベル
    if value_type == 'perm':
        if use_division:
            xlabel = r'$p(A)$'
        else:
            xlabel = r'$\mathrm{per}(A)$'
    else:
        if use_division:
            xlabel = r'$d(A)$'
        else:
            xlabel = r'$\det(A)$'

    # 外れ値の処理（割り算後の値で行う）
    if percentile_range is not None:
        # 頻度を考慮したパーセンタイル計算
        all_values = np.repeat(df_sorted['value'].values, df_sorted['frequency'].values)
        p_low, p_high = np.percentile(all_values, percentile_range)
        df_sorted = df_sorted[(df_sorted['value'] >= p_low) & (df_sorted['value'] <= p_high)]
        print(f"  パーセンタイル範囲: {p_low:.0f} ~ {p_high:.0f}")
    elif x_range is not None:
        df_sorted = df_sorted[(df_sorted['value'] >= x_range[0]) & (df_sorted['value'] <= x_range[1])]
        print(f"  x軸範囲: {x_range[0]} ~ {x_range[1]}")

    values = df_sorted['value'].values
    frequencies = df_sorted['frequency'].values

    if use_binning:
        # ビン化ヒストグラム
        vmin, vmax = values.min(), values.max()
        data_range = vmax - vmin

        # 頻度最大の値と次に多い値からビン幅を計算
        max_freq_idx = frequencies.argmax()
        max_freq_value = values[max_freq_idx]

        # 頻度でソートして上位2つを取得
        freq_sorted_idx = np.argsort(frequencies)[::-1]
        top_value = values[freq_sorted_idx[0]]
        second_value = values[freq_sorted_idx[1]] if len(freq_sorted_idx) > 1 else top_value

        # 上位2つの差でビン幅を決定
        bin_width = abs(second_value - top_value)
        if bin_width == 0:
            bin_width = 1

        # ビン数を計算
        n_bins_calc = max(1, int(np.ceil(data_range / bin_width))) + 1
        actual_bins = n_bins_calc

        # 頻度最大値を中心にビン境界を生成
        bin_start = top_value - bin_width / 2
        while bin_start > vmin - bin_width / 2:
            bin_start -= bin_width
        bin_edges = np.arange(bin_start, vmax + bin_width, bin_width)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        actual_bins = len(bin_centers)

        # 各ビンの頻度を集計
        bin_frequencies = np.zeros(actual_bins)
        for val, freq in zip(values, frequencies):
            bin_idx = np.searchsorted(bin_edges[:-1], val, side='right') - 1
            bin_idx = max(0, min(bin_idx, actual_bins - 1))
            bin_frequencies[bin_idx] += freq

        ax.bar(bin_centers, bin_frequencies, width=bin_width,
               color='#4472C4', edgecolor='none')

        # x軸の範囲
        margin = (vmax - vmin) * 0.02
        ax.set_xlim(vmin - margin, vmax + margin)
    else:
        # 個別値の棒グラフ
        n_bars = len(values)
        if n_bars > 1:
            sorted_vals = np.sort(values)
            diffs = np.diff(sorted_vals)
            if len(diffs) > 0 and diffs.min() > 0:
                bar_width = diffs.min() * 0.9
            else:
                bar_width = (values.max() - values.min()) / n_bars * 0.9
        else:
            bar_width = 1

        ax.bar(values, frequencies, width=bar_width, color='#4472C4', edgecolor='none')

        vmin, vmax = values.min(), values.max()
        margin = (vmax - vmin) * 0.02
        ax.set_xlim(vmin - margin, vmax + margin)

    # 軸ラベル
    ax.set_xlabel(xlabel)
    ax.set_ylabel('頻度')

    if log_scale:
        ax.set_yscale('log')

    # x軸の目盛りを適切に設定
    ticks = get_nice_ticks(vmin, vmax, num_ticks=8)
    ticks = ticks[(ticks >= vmin - margin) & (ticks <= vmax + margin)]

    # 整数目盛りのみに絞り込む（重複防止）
    int_ticks = np.unique(np.round(ticks).astype(int))
    # 範囲内の整数のみを使用
    int_ticks = int_ticks[(int_ticks >= np.floor(vmin)) & (int_ticks <= np.ceil(vmax))]
    ax.set_xticks(int_ticks)

    # 科学表記を無効化（整数表示）
    ax.ticklabel_format(style='plain', axis='x')
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

    # グリッド（y軸のみ）
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)

    # レイアウト調整
    plt.tight_layout()

    # 保存
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f'保存完了: {output_path}')

    plt.close()


def main():
    """メイン処理（対話形式）"""
    print("=" * 50)
    print("論文用グラフ作成スクリプト")
    print("=" * 50)
    print()

    # CSVファイルパスの入力
    csv_path = input("CSVファイルのパスを入力してください: ").strip()

    # パスの正規化（引用符除去）
    csv_path = csv_path.strip('"').strip("'")

    if not os.path.exists(csv_path):
        print(f"エラー: ファイルが見つかりません: {csv_path}")
        sys.exit(1)

    # CSV読み込み
    print(f"\n読み込み中: {csv_path}")
    df = load_csv(csv_path)
    print(f"  データ数: {len(df)}")
    print(f"  元の値の範囲: {df['value'].min()} ~ {df['value'].max()}")
    print(f"  頻度の合計: {df['frequency'].sum()}")

    # 値の種類を推定
    value_type = detect_value_type(csv_path)
    print(f"  値の種類: {value_type}")

    # nを推定
    n = extract_n_from_filename(csv_path)
    if n == 0:
        try:
            n = int(input("行列サイズ n を入力してください: "))
        except ValueError:
            print("エラー: 有効な整数を入力してください")
            sys.exit(1)
    else:
        print(f"  行列サイズ: n = {n}")
        confirm = input(f"  この値でよろしいですか？ (y/n, デフォルト: y): ").strip().lower()
        if confirm == 'n':
            try:
                n = int(input("行列サイズ n を入力してください: "))
            except ValueError:
                print("エラー: 有効な整数を入力してください")
                sys.exit(1)

    # 正規化（割り算）の設定
    use_division = False
    if value_type == 'perm':
        print(f"\n正規化の設定:")
        print(f"  1: p(A) = per(A) / k(n) で正規化 (推奨)")
        print(f"  2: 割らない（生の値 per(A)）")
        div_choice = input("選択 (デフォルト: 1): ").strip()
        if div_choice != '2':
            use_division = True
            divisor = get_krauter_divisor(n)
            df['value'] = df['value'] / divisor
            print(f"  k(n) = 2^{int(np.log2(divisor))} = {divisor} で割り算")
            print(f"  p(A) の範囲: {df['value'].min():.0f} ~ {df['value'].max():.0f}")
        else:
            print(f"  割り算なし（生の値 per(A) を使用）")
    else:  # det
        print(f"\n正規化の設定:")
        print(f"  1: d(A) = det(A) / 2^{{n-1}} で正規化 (推奨)")
        print(f"  2: 割らない（生の値 det(A)）")
        div_choice = input("選択 (デフォルト: 1): ").strip()
        if div_choice != '2':
            use_division = True
            divisor = get_det_divisor(n)
            df['value'] = df['value'] / divisor
            print(f"  2^{{{n}-1}} = {divisor} で割り算")
            print(f"  d(A) の範囲: {df['value'].min():.0f} ~ {df['value'].max():.0f}")
        else:
            print(f"  割り算なし（生の値 det(A) を使用）")

    # 出力ファイル名（自動生成）
    basename = os.path.basename(csv_path).replace('.csv', '')
    if use_division:
        output_name = f"{basename}_divided"
    else:
        output_name = f"{basename}_raw"
    print(f"\n出力先ディレクトリ: {OUTPUT_DIR}")
    print(f"出力ファイル名: {output_name}.png")

    # 表示方法の選択
    print(f"\n表示方法:")
    print(f"  1: ビン化ヒストグラム (推奨)")
    print(f"  2: 個別値の棒グラフ")
    display_choice = input("選択 (デフォルト: 1): ").strip()
    use_binning = display_choice != '2'

    # 外れ値の処理
    print(f"\n外れ値の処理:")
    print(f"  1: パーセンタイル範囲 (0.5%〜99.5%) - 推奨")
    print(f"  2: 全データ表示")
    print(f"  3: x軸範囲を手動指定")
    outlier_choice = input("選択 (デフォルト: 1): ").strip()

    percentile_range = None
    x_range = None
    if outlier_choice == '2':
        pass  # 全データ
    elif outlier_choice == '3':
        try:
            xmin = float(input("  x軸の最小値: "))
            xmax = float(input("  x軸の最大値: "))
            x_range = (xmin, xmax)
        except ValueError:
            print("  無効な入力、パーセンタイル範囲を使用")
            percentile_range = (0.5, 99.5)
    else:
        percentile_range = (0.5, 99.5)

    # ビン数の計算（外れ値処理後の範囲で）
    n_bins = 100
    if use_binning:
        # 外れ値処理後の範囲を計算
        df_temp = df.copy()
        if percentile_range is not None:
            all_values = np.repeat(df_temp['value'].values, df_temp['frequency'].values)
            p_low, p_high = np.percentile(all_values, percentile_range)
            df_temp = df_temp[(df_temp['value'] >= p_low) & (df_temp['value'] <= p_high)]
        elif x_range is not None:
            df_temp = df_temp[(df_temp['value'] >= x_range[0]) & (df_temp['value'] <= x_range[1])]

        # 頻度最大の値と次に多い値からビン幅を計算
        values_temp = df_temp['value'].values
        frequencies_temp = df_temp['frequency'].values
        freq_sorted_idx = np.argsort(frequencies_temp)[::-1]
        top_value = values_temp[freq_sorted_idx[0]]
        second_value = values_temp[freq_sorted_idx[1]] if len(freq_sorted_idx) > 1 else top_value

        bin_width = abs(second_value - top_value)
        if bin_width == 0:
            bin_width = 1

        data_range = values_temp.max() - values_temp.min()
        default_bins = max(1, int(np.ceil(data_range / bin_width))) + 1

        print(f"\n  頻度上位2値: {top_value:.0f}, {second_value:.0f}")
        print(f"  計算されたビン幅: {bin_width:.0f}")
        print(f"  推奨ビン数: {default_bins}")
        bins_input = input(f"ビン数 (デフォルト: {default_bins}): ").strip()
        if bins_input.isdigit():
            n_bins = int(bins_input)
        else:
            n_bins = default_bins

    # 出力ディレクトリ確認
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # グラフ作成
    print("\n" + "=" * 50)
    print("グラフを作成中...")
    print("=" * 50)

    # グラフ出力（PNG）
    output_png = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    plot_frequency_distribution(df, n, value_type, output_png, log_scale=False,
                                percentile_range=percentile_range, x_range=x_range,
                                use_binning=use_binning, n_bins=n_bins,
                                use_division=use_division)

    print("\n" + "=" * 50)
    print("完了!")
    print(f"出力先: {OUTPUT_DIR}")
    print("=" * 50)


if __name__ == '__main__':
    main()
