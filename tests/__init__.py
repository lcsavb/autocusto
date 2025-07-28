"""
Centralized test suite for AutoCusto application.

This package contains all tests organized by functionality rather than by Django app.
This provides better test organization and easier maintenance.

Structure:
- unit/: Fast, isolated unit tests
- integration/: Cross-app integration tests 
- e2e/: End-to-end workflow tests
- test_base.py: Unified test base classes and helpers
"""
# Import test base classes and helpers for easy access
from .test_base import *
