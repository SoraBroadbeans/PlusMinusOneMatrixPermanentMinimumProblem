# PlusMinusOne Permanent Minimum Problem

(±1)行列の permanent（パーマネント）最小値問題を扱うシミュレーションコード集。
行列の制約（Toeplitz, 上三角, 巡回, Hankel など）ごとに探索・頻度分析・可視化を行う。

## 対象環境

- Python 3.10+（動作確認は 3.12 系）

## セットアップ

```bash
pip install -r requirements.txt
```

## 共通の前提

- ほとんどのスクリプトは **対話入力**（`input()`）で実行設定を決める。
- 結果は各フォルダの `result/` に保存される（自動作成）。
- 計算量は指数オーダー。`n` は小さい値から試すことを推奨。

## 使い方（最短）

```bash
python src/calc_permanent.py
python src/calc_r_n.py
python circulant_cal/main.py
python toepliz_cal/main.py
python triangle_cal_ver2/main.py
python reverse_triangle_cal/main.py
python rn_calculator/main.py
python frequ_analysis/main.py
python frequ_analysis/random_sampling.py
python frequ_analysis/plot_graphs.py
```

## フォルダ別マニュアル（MECE）

### 1. 基本計算（`src/`）

- 目的: permanent の基本計算・r_n 計算・検算
- エントリ:
  - `src/calc_permanent.py` : 1つの行列の permanent を計算（対話入力）
  - `src/calc_r_n.py` : r_n を全探索で計算（対話入力）
  - `src/calc_r_n_optimized.py` : r_n を最適化版で計算（対話入力）
  - `src/incremental_calc.py` : 逐次計算の試験用（対話入力）
- 出力: 画面表示中心

### 2. 巡回行列（`circulant_cal/`）

- 目的: 巡回行列の全探索・理論値比較
- エントリ:
  - `circulant_cal/main.py` : 全パターン探索（`n`, `rate` の入力あり）
  - `circulant_cal/circulant_permanent.py` : 単一の集合 `S` から permanent を計算
- 入力:
  - `n`（行列サイズ）
  - `rate`（+1 比率のフィルタ。単値 or `0.3-0.7` の範囲指定）
- 出力: 画面表示（理論値一致で停止）

### 3. Toeplitz 行列（`toepliz_cal/`）

- 目的: Toeplitz 行列の全探索・焼きなまし・ランダム探索
- エントリ:
  - `toepliz_cal/main.py` : 3モード
    - `0` 全探索
    - `1` 焼きなまし
    - `2` ランダム探索
  - `toepliz_cal/toepliz_permanent.py` : 記法入力から単発計算
- 入力:
  - `n`, `rate`
  - 焼きなまし: `checknum`, 初期集合S（カンマ区切り or 空白でランダム）
- 出力:
  - `toepliz_cal/result/` にログファイル（焼きなまし・ランダム探索）
  - 全探索は画面中心

### 4. 上三角 Toeplitz 行列（`triangle_cal_ver2/`）

- 目的: 上三角 Toeplitz 制約下での全探索
- エントリ:
  - `triangle_cal_ver2/main.py`
- 入力: `n`
- 出力: `triangle_cal_ver2/result/` に探索ログ

### 5. Triangle Hankel 行列（`reverse_triangle_cal/`）

- 目的: 上三角 Hankel（下三角固定）での全探索
- エントリ:
  - `reverse_triangle_cal/main.py`
- 入力: `n`（大きい場合は警告と確認）
- 出力: `reverse_triangle_cal/result/` に探索ログ

### 6. Kräuter 予想検証（`rn_calculator/`）

- 目的: Toeplitz 行列における最小正 permanent を探索
- エントリ:
  - `rn_calculator/main.py`
- 入力:
  - `n`
  - 戦略（sparse / symmetric / continuous / random / all）
  - random の場合はサンプル数・最大時間
- 出力: 画面表示（必要なら達成行列の詳細表示）

### 7. 上三角行列の頻度分析（`frequ_analysis/`）

- 目的: 上三角行列の permanent / determinant 分布の集計と可視化
- エントリ:
  - `frequ_analysis/main.py` : 全探索し頻度CSVを出力
  - `frequ_analysis/random_sampling.py` : ランダムサンプリング版
  - `frequ_analysis/plot_graphs.py` : CSVからヒストグラムを作成
- 入力:
  - `n`, 出力形式（集計/行列出力）, `perm/det` 選択
  - ランダム版: 試行回数, 行列タイプ（full/upper/toeplitz）
- 出力:
  - `frequ_analysis/result/` に CSV と画像

### 8. 補助ツール（`tools/`）

- `tools/file_hook.py` : 変更検知とハッシュ管理
- `tools/auto_hook.sh` : 自動チェックのラッパー

## よくある使い方（例）

- 上三角 Toeplitz の全探索: `python triangle_cal_ver2/main.py`
- Toeplitz の焼きなまし探索: `python toepliz_cal/main.py` → モード `1`
- 上三角行列の分布集計: `python frequ_analysis/main.py`
- CSV の可視化: `python frequ_analysis/plot_graphs.py`

## 注意

- 全探索は計算量が非常に大きい。`n` が大きい場合はランダム探索を推奨。
- 生成される `result/` フォルダは Git 管理対象外。
