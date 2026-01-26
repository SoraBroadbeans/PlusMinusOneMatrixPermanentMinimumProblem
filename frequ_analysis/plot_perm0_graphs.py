#!/usr/bin/env python3
"""
論文用グラフ作成スクリプト（perm=0の欠けを可視化）

CSVデータから頻度分布グラフを作成する。
ビン幅と除数を手動指定し、0を中心にビンを配置する。

使用法:
    python plot_perm0_graphs.py
    -> CSVファイルのパス、除数、ビン幅を入力
    -> グラフが masterPaper/image に出力される
"""

import os
import sys
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
    plt.rcParams['font.family'] = ['Hiragino Sans', 'Hiragino Kaku Gothic Pro', 'sans-serif']
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


def extract_n_from_filename(filepath: str) -> int:
    """ファイル名から行列サイズnを抽出"""
    basename = os.path.basename(filepath)
    parts = basename.replace('.csv', '').split('_')

    for i, part in enumerate(parts):
        if part.isdigit():
            n = int(part)
            if 1 <= n <= 100:
                return n
    return 0


def get_nice_ticks(vmin: float, vmax: float, num_ticks: int = 7) -> np.ndarray:
    """最大値・最小値から適切な目盛りを生成"""
    data_range = vmax - vmin
    if data_range == 0:
        return np.array([vmin])

    raw_step = data_range / num_ticks
    magnitude = 10 ** np.floor(np.log10(raw_step))
    nice_steps = [1, 2, 5, 10]
    normalized = raw_step / magnitude
    step = magnitude * min(nice_steps, key=lambda x: abs(x - normalized))

    tick_min = np.floor(vmin / step) * step
    tick_max = np.ceil(vmax / step) * step
    ticks = np.arange(tick_min, tick_max + step / 2, step)

    return ticks


def plot_frequency_distribution(
    df: pd.DataFrame,
    n: int,
    output_path: str,
    divisor: int,
    bin_width: int,
    x_range: tuple = None,
    log_scale: bool = False,
    remove_outliers: bool = True
):
    """
    頻度分布の棒グラフを作成する（0中心のビン配置）
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # データをコピーしてソート
    df_sorted = df.sort_values('value').copy()

    # 軸ラベル
    xlabel = r'$p(A)$'

    # 外れ値除去（IQR法）
    if remove_outliers:
        values_for_iqr = df_sorted['value'].values
        q1 = np.percentile(values_for_iqr, 25)
        q3 = np.percentile(values_for_iqr, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # 外れ値を抽出
        outliers = df_sorted[(df_sorted['value'] < lower_bound) | (df_sorted['value'] > upper_bound)]
        removed_count = len(outliers)

        print(f"  外れ値除去 (IQR法): 範囲 {lower_bound:.0f} ~ {upper_bound:.0f}")
        print(f"  除去件数: {removed_count} 件")
        if removed_count > 0:
            print(f"  除去された値:")
            for _, row in outliers.iterrows():
                print(f"    {row['value']:.0f} (頻度: {row['frequency']:.0f})")

        df_sorted = df_sorted[(df_sorted['value'] >= lower_bound) & (df_sorted['value'] <= upper_bound)]

    # x軸範囲でフィルタ
    if x_range is not None:
        df_sorted = df_sorted[(df_sorted['value'] >= x_range[0]) & (df_sorted['value'] <= x_range[1])]
        print(f"  x軸範囲: {x_range[0]} ~ {x_range[1]}")

    values = df_sorted['value'].values
    frequencies = df_sorted['frequency'].values

    if len(values) == 0:
        print("エラー: 指定範囲にデータがありません")
        plt.close()
        return

    vmin, vmax = values.min(), values.max()

    # 0を中心にビン境界を生成
    # ビンは ..., -2*bin_width, -bin_width, 0, bin_width, 2*bin_width, ... を中心とする
    bin_edges_negative = np.arange(-bin_width / 2, vmin - bin_width, -bin_width)[::-1]
    bin_edges_positive = np.arange(-bin_width / 2, vmax + bin_width, bin_width)
    bin_edges = np.unique(np.concatenate([bin_edges_negative, bin_edges_positive]))
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    actual_bins = len(bin_centers)

    print(f"  ビン数: {actual_bins}")
    print(f"  ビン幅: {bin_width}")

    # 各ビンの頻度を集計
    bin_frequencies = np.zeros(actual_bins)
    for val, freq in zip(values, frequencies):
        bin_idx = np.searchsorted(bin_edges[:-1], val, side='right') - 1
        bin_idx = max(0, min(bin_idx, actual_bins - 1))
        bin_frequencies[bin_idx] += freq

    # 0付近のビンの頻度を確認（デバッグ用）
    zero_bin_idx = np.argmin(np.abs(bin_centers))
    print(f"\n  === 0付近のビン状況 ===")
    for i in range(max(0, zero_bin_idx - 5), min(actual_bins, zero_bin_idx + 6)):
        marker = " <-- 0" if i == zero_bin_idx else ""
        print(f"  ビン中心 {bin_centers[i]:6.1f}: 頻度 {bin_frequencies[i]:5.0f}{marker}")
    print()

    ax.bar(bin_centers, bin_frequencies, width=bin_width * 0.9,
           color='#4472C4', edgecolor='none')

    # x軸の範囲
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
    ax.set_xticks(ticks)

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
    print("論文用グラフ作成スクリプト（perm=0可視化版）")
    print("=" * 50)
    print()

    # CSVファイルパスの入力
    csv_path = input("CSVファイルのパスを入力してください: ").strip()
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

    # 除数の入力
    print(f"\n除数の設定:")
    print(f"  n=15 の場合、値は2048の倍数なので除数=2048が適切")
    try:
        divisor = int(input("除数を入力してください: ").strip())
    except ValueError:
        print("エラー: 有効な整数を入力してください")
        sys.exit(1)

    # 割り算実行
    df['value'] = df['value'] / divisor
    print(f"  割り算後の値の範囲: {df['value'].min():.0f} ~ {df['value'].max():.0f}")

    # 0が存在するか確認
    has_zero = 0 in df['value'].values
    print(f"  0の存在: {'あり' if has_zero else 'なし'}")

    # 0付近の値を表示
    sorted_vals = df.sort_values('value')
    near_zero = sorted_vals[(sorted_vals['value'] >= -10) & (sorted_vals['value'] <= 10)]
    print(f"  0付近の値 (-10〜10):")
    for _, row in near_zero.iterrows():
        print(f"    値: {row['value']:6.1f}, 頻度: {row['frequency']}")

    # ビン幅の入力
    print(f"\nビン幅の設定:")
    print(f"  値が整数なら bin_width=2 で各偶数/奇数が1ビン")
    print(f"  値が2刻みなら bin_width=2 で各値が1ビン")
    try:
        bin_width = int(input("ビン幅を入力してください: ").strip())
    except ValueError:
        print("エラー: 有効な整数を入力してください")
        sys.exit(1)

    # 外れ値除去の設定
    print(f"\n外れ値除去の設定:")
    print(f"  1: 外れ値を除去する（IQR法、推奨）")
    print(f"  2: 外れ値を除去しない")
    outlier_choice = input("選択 (デフォルト: 1): ").strip()
    remove_outliers = outlier_choice != '2'

    # x軸範囲の設定
    print(f"\nx軸範囲の設定:")
    print(f"  1: 全データ表示")
    print(f"  2: 範囲を手動指定")
    range_choice = input("選択 (デフォルト: 1): ").strip()

    x_range = None
    if range_choice == '2':
        try:
            xmin = float(input("  x軸の最小値: "))
            xmax = float(input("  x軸の最大値: "))
            x_range = (xmin, xmax)
        except ValueError:
            print("  無効な入力、全データ表示を使用")

    # 出力ファイル名
    basename = os.path.basename(csv_path).replace('.csv', '')
    output_name = f"{basename}_perm0"
    print(f"\n出力先ディレクトリ: {OUTPUT_DIR}")
    print(f"出力ファイル名: {output_name}.png")

    # 出力ディレクトリ確認
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # グラフ作成
    print("\n" + "=" * 50)
    print("グラフを作成中...")
    print("=" * 50)

    output_png = os.path.join(OUTPUT_DIR, f"{output_name}.png")
    plot_frequency_distribution(df, n, output_png, divisor, bin_width, x_range=x_range, remove_outliers=remove_outliers)

    print("\n" + "=" * 50)
    print("完了!")
    print(f"出力先: {OUTPUT_DIR}")
    print("=" * 50)


if __name__ == '__main__':
    main()
