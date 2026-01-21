"""
triangle_cal - Upper triangular (+-1) matrix permanent calculator

Comprehensive toolkit for Krauter conjecture verification

Main Components:
    - core: Permanent calculation, Krauter conjecture, Toeplitz matrices
    - algorithms: Random search, exhaustive search, verification
    - parallel: Parallel processing utilities
    - generators: Matrix generation utilities
    - io: Result writing, report generation

Usage:
    from triangle_cal import permanent, calculate_krauter_conjecture_value
"""

__version__ = '2.0.0'
__author__ = 'Research Team'

# Core exports
from .core.permanent import permanent, is_pm_one_matrix
from .core.krauter import calculate_krauter_conjecture_value
from .core.toeplitz import (
    create_toeplitz_matrix_from_set,
    calculate_toeplitz_permanent_from_set
)
from .core.matrix_utils import (
    calculate_matrix_properties,
    is_upper_triangular,
    create_upper_triangular_matrix
)

# Generator exports
from .generators.toeplitz_indices import generate_upper_triangular_toeplitz_indices

__all__ = [
    # Core
    'permanent',
    'is_pm_one_matrix',
    'calculate_krauter_conjecture_value',
    'create_toeplitz_matrix_from_set',
    'calculate_toeplitz_permanent_from_set',
    'calculate_matrix_properties',
    'is_upper_triangular',
    'create_upper_triangular_matrix',
    # Generators
    'generate_upper_triangular_toeplitz_indices',
]
