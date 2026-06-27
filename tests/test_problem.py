"""
Unit tests for the problem representation module (aco_vrp.problem).
"""

import numpy as np
import pytest

from aco_vrp.problem import (
    CVRPSolution,
    Customer,
    Depot,
    load_solomon,
)


# ---------------------------------------------------------------------------
# Dataclass construction
# ---------------------------------------------------------------------------


def test_customer_defaults():
    c = Customer(index=0, x=1.0, y=2.0, demand=5.0)
    assert c.ready_time == 0.0
    assert c.due_date == float("inf")
    assert c.service_time == 0.0


def test_depot_fields():
    d = Depot(x=10.0, y=20.0)
    assert d.x == 10.0
    assert d.y == 20.0


def test_instance_construction(tiny_instance):
    assert tiny_instance.name == "tiny"
    assert len(tiny_instance.customers) == 3
    assert tiny_instance.vehicle_capacity == 30.0
    assert tiny_instance.max_vehicles is None


# ---------------------------------------------------------------------------
# Distance computation
# ---------------------------------------------------------------------------


def test_distance_same_node(tiny_instance):
    assert tiny_instance.distance(0, 0) == 0.0
    assert tiny_instance.distance(1, 1) == 0.0


def test_distance_depot_to_customer(tiny_instance):
    # depot(0,0) -> customer[0](3,0): distance = 3.0
    assert tiny_instance.distance(0, 1) == pytest.approx(3.0)


def test_distance_symmetry(tiny_instance):
    assert tiny_instance.distance(1, 2) == pytest.approx(tiny_instance.distance(2, 1))


def test_distance_customer_to_customer(tiny_instance):
    # customer[0](3,0) -> customer[1](0,4): distance = 5.0
    assert tiny_instance.distance(1, 2) == pytest.approx(5.0)


def test_distance_matrix_shape(tiny_instance):
    mat = tiny_instance.distance_matrix()
    n = len(tiny_instance.customers) + 1
    assert mat.shape == (n, n)


def test_distance_matrix_diagonal_zero(tiny_instance):
    mat = tiny_instance.distance_matrix()
    assert np.all(np.diag(mat) == 0.0)


def test_distance_matrix_symmetric(tiny_instance):
    mat = tiny_instance.distance_matrix()
    np.testing.assert_array_almost_equal(mat, mat.T)


def test_distance_matrix_matches_distance(tiny_instance):
    mat = tiny_instance.distance_matrix()
    for i in range(len(tiny_instance.customers) + 1):
        for j in range(len(tiny_instance.customers) + 1):
            assert mat[i, j] == pytest.approx(tiny_instance.distance(i, j))


# ---------------------------------------------------------------------------
# Subset extraction
# ---------------------------------------------------------------------------


def test_subset_returns_correct_count(tiny_instance):
    sub = tiny_instance.subset(2)
    assert len(sub.customers) == 2


def test_subset_name_suffixed(tiny_instance):
    sub = tiny_instance.subset(2)
    assert sub.name == "tiny_2"


def test_subset_preserves_capacity(tiny_instance):
    sub = tiny_instance.subset(2)
    assert sub.vehicle_capacity == tiny_instance.vehicle_capacity


def test_subset_preserves_depot(tiny_instance):
    sub = tiny_instance.subset(2)
    assert sub.depot.x == tiny_instance.depot.x
    assert sub.depot.y == tiny_instance.depot.y


def test_subset_keeps_first_n(tiny_instance):
    sub = tiny_instance.subset(2)
    assert sub.customers[0].index == tiny_instance.customers[0].index
    assert sub.customers[1].index == tiny_instance.customers[1].index


def test_subset_oversize_raises(tiny_instance):
    with pytest.raises(ValueError):
        tiny_instance.subset(100)


# ---------------------------------------------------------------------------
# Solution feasibility
# ---------------------------------------------------------------------------


def test_feasible_solution(tiny_instance):
    # Route 1: customers 1, 2 (demand 10+15=25 <= 30)
    # Route 2: customer 3 (demand 20 <= 30)
    sol = CVRPSolution(routes=[[1, 2], [3]])
    assert sol.is_feasible(tiny_instance) is True


def test_infeasible_capacity_exceeded(tiny_instance):
    # All three customers on one route: demand 10+15+20=45 > 30
    sol = CVRPSolution(routes=[[1, 2, 3]])
    assert sol.is_feasible(tiny_instance) is False


def test_infeasible_missing_customer(tiny_instance):
    # Only visits customers 1 and 2, skips 3
    sol = CVRPSolution(routes=[[1, 2]])
    assert sol.is_feasible(tiny_instance) is False


def test_infeasible_duplicate_customer(tiny_instance):
    sol = CVRPSolution(routes=[[1, 1], [2, 3]])
    assert sol.is_feasible(tiny_instance) is False


def test_infeasible_invalid_node(tiny_instance):
    # Node 99 doesn't exist
    sol = CVRPSolution(routes=[[1, 2], [99]])
    assert sol.is_feasible(tiny_instance) is False


def test_empty_routes_infeasible(tiny_instance):
    sol = CVRPSolution(routes=[])
    assert sol.is_feasible(tiny_instance) is False


# ---------------------------------------------------------------------------
# Solution distance computation
# ---------------------------------------------------------------------------


def test_compute_distance_single_route(tiny_instance):
    # Route: depot(0,0) -> c1(3,0) -> depot: 3 + 3 = 6.0
    sol = CVRPSolution(routes=[[1]])
    assert sol.compute_distance(tiny_instance) == pytest.approx(6.0)


def test_compute_distance_empty_route(tiny_instance):
    sol = CVRPSolution(routes=[[]])
    assert sol.compute_distance(tiny_instance) == pytest.approx(0.0)


def test_compute_distance_multiple_routes(tiny_instance):
    sol = CVRPSolution(routes=[[1, 2], [3]])
    d1 = tiny_instance.distance(0, 1) + tiny_instance.distance(1, 2) + tiny_instance.distance(2, 0)
    d2 = tiny_instance.distance(0, 3) + tiny_instance.distance(3, 0)
    assert sol.compute_distance(tiny_instance) == pytest.approx(d1 + d2)


# ---------------------------------------------------------------------------
# Solomon RC101 parser
# ---------------------------------------------------------------------------


def test_rc101_customer_count(rc101_instance):
    assert len(rc101_instance.customers) == 100


def test_rc101_name(rc101_instance):
    assert "RC101" in rc101_instance.name.upper()


def test_rc101_depot_coordinates(rc101_instance):
    assert rc101_instance.depot.x == pytest.approx(40.0)
    assert rc101_instance.depot.y == pytest.approx(50.0)


def test_rc101_vehicle_capacity(rc101_instance):
    assert rc101_instance.vehicle_capacity == pytest.approx(200.0)


def test_rc101_max_vehicles(rc101_instance):
    assert rc101_instance.max_vehicles == 25


def test_rc101_customer_indices_zero_based(rc101_instance):
    for i, c in enumerate(rc101_instance.customers):
        assert c.index == i


def test_rc101_demands_positive(rc101_instance):
    assert all(c.demand > 0 for c in rc101_instance.customers)


def test_rc101_distance_matrix_valid(rc101_instance):
    mat = rc101_instance.distance_matrix()
    assert mat.shape == (101, 101)
    assert np.all(mat >= 0)
    np.testing.assert_array_almost_equal(mat, mat.T)


def test_rc101_subset_25(rc101_instance):
    sub = rc101_instance.subset(25)
    assert len(sub.customers) == 25
    assert sub.name == "RC101_25"


def test_rc101_subset_50(rc101_instance):
    sub = rc101_instance.subset(50)
    assert len(sub.customers) == 50


def test_load_solomon_missing_file():
    with pytest.raises(FileNotFoundError):
        load_solomon("data/solomon/DOESNOTEXIST.txt")
