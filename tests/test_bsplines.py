"""Tests for BSplines.FCStd — InternalAlignment, Block, Weight constraints."""

from pathlib import Path

import pytest

from freecad_sketch_reader import (
    GeomBSplineCurve,
    GeomCircle,
    GeomPoint,
    PointPos,
    Sketch,
    read_sketches,
)

TEST_DIR = Path(__file__).parent
BSPLINE_FILE = TEST_DIR / "BSplines.FCStd"


@pytest.fixture
def sketch() -> Sketch:
    sketches = read_sketches(BSPLINE_FILE)
    return sketches["Sketch"]


class TestBSplineGeometry:
    def test_geometry_count(self, sketch: Sketch) -> None:
        assert sketch.GeometryCount == 9

    def test_bspline_present(self, sketch: Sketch) -> None:
        geom = sketch.Geometry[5]
        assert isinstance(geom, GeomBSplineCurve)

    def test_control_point_circles(self, sketch: Sketch) -> None:
        """Geometry 0-4 are circles (weight circles for the B-spline poles)."""
        for i in range(5):
            assert isinstance(sketch.Geometry[i], GeomCircle)

    def test_knot_points(self, sketch: Sketch) -> None:
        """Geometry 6-8 are points (knot points for the B-spline)."""
        for i in range(6, 9):
            assert isinstance(sketch.Geometry[i], GeomPoint)


class TestWeightConstraint:
    def test_weight_type(self, sketch: Sketch) -> None:
        c = sketch.Constraints[0]
        assert c.Type == "Weight"

    def test_weight_value(self, sketch: Sketch) -> None:
        c = sketch.Constraints[0]
        assert c.Value == pytest.approx(1.0)

    def test_weight_first(self, sketch: Sketch) -> None:
        c = sketch.Constraints[0]
        assert c.First == 0
        assert c.Driving is True

    def test_weight_no_internal_alignment(self, sketch: Sketch) -> None:
        """Weight constraints are not InternalAlignment."""
        c = sketch.Constraints[0]
        assert c.InternalAlignmentType == "Undef"
        assert c.InternalAlignmentIndex == -1


class TestEqualConstraints:
    def test_equal_constraints(self, sketch: Sketch) -> None:
        """Constraints 1-4 are Equal constraints between weight circles."""
        for i in range(1, 5):
            c = sketch.Constraints[i]
            assert c.Type == "Equal"
            assert c.First == 0
            assert c.Second == i

    def test_equal_no_internal_alignment(self, sketch: Sketch) -> None:
        for i in range(1, 5):
            c = sketch.Constraints[i]
            assert c.InternalAlignmentType == "Undef"
            assert c.InternalAlignmentIndex == -1


class TestInternalAlignmentBSplineControlPoint:
    """Constraints 5-9 are InternalAlignment:BSplineControlPoint."""

    def test_type(self, sketch: Sketch) -> None:
        for i in range(5, 10):
            c = sketch.Constraints[i]
            assert c.Type == "InternalAlignment"

    def test_internal_alignment_type(self, sketch: Sketch) -> None:
        for i in range(5, 10):
            c = sketch.Constraints[i]
            assert c.InternalAlignmentType == "BSplineControlPoint"

    def test_internal_alignment_index(self, sketch: Sketch) -> None:
        """InternalAlignmentIndex maps to the pole index (0-4)."""
        for i in range(5, 10):
            c = sketch.Constraints[i]
            assert c.InternalAlignmentIndex == i - 5

    def test_first_references_circle(self, sketch: Sketch) -> None:
        """First references the weight circle, via its mid point."""
        for i in range(5, 10):
            c = sketch.Constraints[i]
            assert c.First == i - 5
            assert c.FirstPos == PointPos.mid

    def test_second_references_bspline(self, sketch: Sketch) -> None:
        """Second references the B-spline geometry (index 5)."""
        for i in range(5, 10):
            c = sketch.Constraints[i]
            assert c.Second == 5
            assert c.SecondPos == PointPos.none


class TestInternalAlignmentBSplineKnotPoint:
    """Constraints 10-12 are InternalAlignment:BSplineKnotPoint."""

    def test_type(self, sketch: Sketch) -> None:
        for i in range(10, 13):
            c = sketch.Constraints[i]
            assert c.Type == "InternalAlignment"

    def test_internal_alignment_type(self, sketch: Sketch) -> None:
        for i in range(10, 13):
            c = sketch.Constraints[i]
            assert c.InternalAlignmentType == "BSplineKnotPoint"

    def test_internal_alignment_index(self, sketch: Sketch) -> None:
        """InternalAlignmentIndex maps to the knot index (0-2)."""
        for i in range(10, 13):
            c = sketch.Constraints[i]
            assert c.InternalAlignmentIndex == i - 10

    def test_first_references_point(self, sketch: Sketch) -> None:
        """First references a GeomPoint, via its start point."""
        for i in range(10, 13):
            c = sketch.Constraints[i]
            assert c.First == i - 10 + 6  # geometry indices 6, 7, 8
            assert c.FirstPos == PointPos.start

    def test_second_references_bspline(self, sketch: Sketch) -> None:
        for i in range(10, 13):
            c = sketch.Constraints[i]
            assert c.Second == 5
            assert c.SecondPos == PointPos.none


class TestBlockConstraint:
    """Constraints 16-18 are Block constraints."""

    def test_block_type(self, sketch: Sketch) -> None:
        for i in [16, 17, 18]:
            c = sketch.Constraints[i]
            assert c.Type == "Block"

    def test_block_first_references(self, sketch: Sketch) -> None:
        assert sketch.Constraints[16].First == 1
        assert sketch.Constraints[17].First == 3
        assert sketch.Constraints[18].First == 5

    def test_block_no_internal_alignment(self, sketch: Sketch) -> None:
        for i in [16, 17, 18]:
            c = sketch.Constraints[i]
            assert c.InternalAlignmentType == "Undef"
            assert c.InternalAlignmentIndex == -1


class TestOtherConstraintsInBSplineSketch:
    """Other constraint types present in the BSpline sketch."""

    def test_coincident(self, sketch: Sketch) -> None:
        c = sketch.Constraints[13]
        assert c.Type == "Coincident"
        assert c.First == 0
        assert c.FirstPos == PointPos.mid
        assert c.Second == -1
        assert c.SecondPos == PointPos.start

    def test_point_on_object(self, sketch: Sketch) -> None:
        c = sketch.Constraints[14]
        assert c.Type == "PointOnObject"
        assert c.First == 4
        assert c.FirstPos == PointPos.mid

    def test_distance(self, sketch: Sketch) -> None:
        c = sketch.Constraints[15]
        assert c.Type == "Distance"
        assert c.Value == pytest.approx(25.0)
        assert c.First == 5
        assert c.FirstPos == PointPos.end


class TestConstraintCount:
    def test_total_constraint_count(self, sketch: Sketch) -> None:
        assert sketch.ConstraintCount == 19


class TestNonInternalAlignmentDefaults:
    """Constraints that are not InternalAlignment should have default values."""

    def test_weight_defaults(self, sketch: Sketch) -> None:
        c = sketch.Constraints[0]  # Weight
        assert c.InternalAlignmentType == "Undef"
        assert c.InternalAlignmentIndex == -1

    def test_equal_defaults(self, sketch: Sketch) -> None:
        c = sketch.Constraints[1]  # Equal
        assert c.InternalAlignmentType == "Undef"
        assert c.InternalAlignmentIndex == -1

    def test_coincident_defaults(self, sketch: Sketch) -> None:
        c = sketch.Constraints[13]  # Coincident
        assert c.InternalAlignmentType == "Undef"
        assert c.InternalAlignmentIndex == -1

    def test_distance_defaults(self, sketch: Sketch) -> None:
        c = sketch.Constraints[15]  # Distance
        assert c.InternalAlignmentType == "Undef"
        assert c.InternalAlignmentIndex == -1

    def test_block_defaults(self, sketch: Sketch) -> None:
        c = sketch.Constraints[16]  # Block
        assert c.InternalAlignmentType == "Undef"
        assert c.InternalAlignmentIndex == -1


class TestConstraintHashability:
    """InternalAlignment constraints with new fields should remain hashable."""

    def test_all_constraints_hashable(self, sketch: Sketch) -> None:
        for c in sketch.Constraints:
            hash(c)

    def test_internal_alignment_constraints_in_set(self, sketch: Sketch) -> None:
        ia_constraints = [c for c in sketch.Constraints if c.Type == "InternalAlignment"]
        ia_set = set(ia_constraints)
        assert len(ia_set) == len(ia_constraints)
