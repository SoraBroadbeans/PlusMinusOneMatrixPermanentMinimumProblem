# permanent simulation

(±1)行列のパーマネントに関するシミュレーション用コード一式。

## 対象フォルダ

- `src/`: 基本的なパーマネント計算・補助関数
- `circulant_cal/`: 巡回行列の計算
- `toepliz_cal/`: Toeplitz 行列の計算
- `triangle_cal_ver2/`: 上三角関連の計算（ver2）
- `reverse_triangle_cal/`: 逆三角系の計算
- `rn_calculator/`: Krauter 予想値の検証
- `frequ_analysis/`: 頻度解析
- `tools/`: 補助スクリプト

## 使い方（例）

```bash
python src/calc_permanent.py
python src/calc_r_n.py
python circulant_cal/main.py
python toepliz_cal/main.py
python triangle_cal_ver2/main.py
python reverse_triangle_cal/main.py
python rn_calculator/main.py
python frequ_analysis/main.py
```

各サブプロジェクトの依存関係は、必要に応じて各フォルダ内の `requirements.txt` を参照してください。
