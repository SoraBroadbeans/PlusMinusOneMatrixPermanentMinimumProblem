"""
reverse_triangle_cal - Triangle Hankel matrix permanent calculator

Comprehensive toolkit for Triangle Hankel matrix analysis and Krauter conjecture verification

Triangle Hankel Definition:
    T[i,j] = h[i+j]  if i ≤ j  (upper triangle uses Hankel indexing)
    T[i,j] = 1       if i > j  (lower triangle fixed to 1)

where h[k] ∈ {±1} for k = 0, 1, 2, ..., 2n-2
"""

__version__ = '1.0.0'
__author__ = 'Research Team'

# Core exports
from .core.permanent import permanent, is_pm_one_matrix
from .core.krauter import calculate_krauter_conjecture_value
from .core.hankel import (
    create_hankel_matrix_from_set,
    calculate_hankel_permanent_from_set
)
from .core.matrix_utils import (
    calculate_matrix_properties,
    is_upper_triangular,
    create_upper_triangular_matrix
)

# Generator exports
from .generators.hankel_indices import generate_upper_triangular_hankel_indices

__all__ = [
    # Core
    'permanent',
    'is_pm_one_matrix',
    'calculate_krauter_conjecture_value',
    'create_hankel_matrix_from_set',
    'calculate_hankel_permanent_from_set',
    'calculate_matrix_properties',
    'is_upper_triangular',
    'create_upper_triangular_matrix',
    # Generators
    'generate_upper_triangular_hankel_indices',
]
