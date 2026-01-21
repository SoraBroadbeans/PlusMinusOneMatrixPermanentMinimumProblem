"""
パーマネント計算パッケージ

このパッケージには以下の機能が含まれています:
- calc_permanent: 行列のパーマネント計算（愚直法とRyser法）
- calc_r_n: (±1)行列のパーマネント値の個数計算
"""

from .calc_permanent import permanent, permanent_naive, permanent_ryser, is_pm_one_matrix
from .calc_r_n import calculate_r_n, generate_all_pm_one_matrices, analyze_known_results

__version__ = "1.1"
__all__ = [
    "permanent",
    "permanent_naive", 
    "permanent_ryser",
    "is_pm_one_matrix",
    "calculate_r_n",
    "generate_all_pm_one_matrices",
    "analyze_known_results"
]