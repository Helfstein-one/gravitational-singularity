"""
Benchmark Test Suite: Executes the 4-tier quantitative compression benchmarks
and AST integrity assertions under pytest.
"""

import unittest
from tests.benchmark_skills import (
    TestTier1ArchitecturalIntegrity,
    TestTier2BoundaryAndCornerCases,
    TestTier3CrossFeatureCombinations,
    TestTier4RealWorldBenchmarks,
)

# Expose test cases so pytest and unittest automatically collect all 25 assertions
__all__ = [
    "TestTier1ArchitecturalIntegrity",
    "TestTier2BoundaryAndCornerCases",
    "TestTier3CrossFeatureCombinations",
    "TestTier4RealWorldBenchmarks",
]

if __name__ == "__main__":
    unittest.main()
