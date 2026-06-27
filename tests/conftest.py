"""
Shared test fixtures for the aco_vrp test suite.

Provides reusable pytest fixtures including:
    tiny_instance      A minimal CVRPInstance with 3 customers for fast unit tests.
    rc101_instance     The full Solomon RC101 instance (requires data download).
"""

from pathlib import Path

import pytest

from aco_vrp.problem import Customer, CVRPInstance, Depot

RC101_PATH = Path("data/solomon/RC101.txt")


@pytest.fixture
def tiny_instance() -> CVRPInstance:
    """3-customer instance on a simple grid for deterministic unit testing."""
    depot = Depot(x=0.0, y=0.0)
    customers = [
        Customer(index=0, x=3.0, y=0.0, demand=10.0),
        Customer(index=1, x=0.0, y=4.0, demand=15.0),
        Customer(index=2, x=3.0, y=4.0, demand=20.0),
    ]
    return CVRPInstance(
        name="tiny",
        depot=depot,
        customers=customers,
        vehicle_capacity=30.0,
    )


@pytest.fixture
def rc101_instance() -> CVRPInstance:
    from aco_vrp.problem import load_solomon
    if not RC101_PATH.exists():
        pytest.skip("RC101.txt not found — run scripts/download_solomon.py first")
    return load_solomon(str(RC101_PATH))
