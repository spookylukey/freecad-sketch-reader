"""Tests for freecad_sketch_reader against Misc.FCStd."""

from pathlib import Path

import pytest

from freecad_sketch_reader import (
    GeomArcOfCircle,
    GeomLineSegment,
    PointPos,
    Sketch,
    Vector,
    read_sketches,
    read_sketches_from_xml,
)

TEST_DIR = Path(__file__).parent
FCSTD_FILE = TEST_DIR / "Misc.FCStd"
XML_FILE = TEST_DIR / "Misc.FCStd.unpacked" / "Document.xml"


@pytest.fixture
def sketch() -> Sketch:
    sketches = read_sketches(FCSTD_FILE)
    return sketches["Sketch"]


@pytest.fixture
def sketch_from_xml() -> Sketch:
    sketches = read_sketches_from_xml(XML_FILE)
    return sketches["Sketch"]


class TestReadFromFCStd:
    def test_returns_dict_with_sketch(self, sketch: Sketch) -> None:
        assert sketch.Name == "Sketch"

    def test_label(self, sketch: Sketch) -> None:
        assert sketch.Label == "Sketch"


class TestReadFromXml:
    def test_same_as_fcstd(self, sketch: Sketch, sketch_from_xml: Sketch) -> None:
        assert sketch == sketch_from_xml


class TestGeometry:
    def test_geometry_count(self, sketch: Sketch) -> None:
        assert sketch.GeometryCount == 8
        assert len(sketch.Geometry) == 8

    def test_first_geom_is_line_segment(self, sketch: Sketch) -> None:
        geom = sketch.Geometry[0]
        assert isinstance(geom, GeomLineSegment)

    def test_line_segment_start_point(self, sketch: Sketch) -> None:
        geom = sketch.Geometry[0]
        assert isinstance(geom, GeomLineSegment)
        assert geom.StartPoint == Vector(0.0, 0.0, 0.0)

    def test_line_segment_end_point(self, sketch: Sketch) -> None:
        geom = sketch.Geometry[0]
        assert isinstance(geom, GeomLineSegment)
        assert geom.EndPoint.x == pytest.approx(67.5472436778074297)
        assert geom.EndPoint.y == pytest.approx(0.0)

    def test_line_segment_not_construction(self, sketch: Sketch) -> None:
        geom = sketch.Geometry[0]
        assert isinstance(geom, GeomLineSegment)
        assert geom.Construction is False

    def test_arc_of_circle(self, sketch: Sketch) -> None:
        # Geometry[3] is an ArcOfCircle
        geom = sketch.Geometry[3]
        assert isinstance(geom, GeomArcOfCircle)
        assert geom.Center.x == pytest.approx(83.8837494467609588)
        assert geom.Center.y == pytest.approx(68.6823157097693269)
        assert geom.Radius == pytest.approx(36.6331336625265180)
        assert geom.StartAngle == pytest.approx(0.0)
        assert geom.EndAngle == pytest.approx(2.9080758210602404)

    def test_arc_start_point(self, sketch: Sketch) -> None:
        geom = sketch.Geometry[3]
        assert isinstance(geom, GeomArcOfCircle)
        # StartAngle=0, AngleXU=0, so start point is at Center + (Radius, 0)
        assert geom.StartPoint.x == pytest.approx(83.8837494467609588 + 36.6331336625265180)
        assert geom.StartPoint.y == pytest.approx(68.6823157097693269)

    def test_all_geometry_types_present(self, sketch: Sketch) -> None:
        types = {type(g).__name__ for g in sketch.Geometry}
        assert "GeomLineSegment" in types
        assert "GeomArcOfCircle" in types


class TestExternalGeo:
    def test_external_geo_count(self, sketch: Sketch) -> None:
        assert sketch.ExternalGeometryCount == 2

    def test_external_geo_is_construction(self, sketch: Sketch) -> None:
        for geom in sketch.ExternalGeo:
            assert isinstance(geom, GeomLineSegment)
            assert geom.Construction is True

    def test_h_axis(self, sketch: Sketch) -> None:
        # First external geom is H-axis: (0,0,0) -> (1,0,0)
        geom = sketch.ExternalGeo[0]
        assert isinstance(geom, GeomLineSegment)
        assert geom.StartPoint == Vector(0.0, 0.0, 0.0)
        assert geom.EndPoint == Vector(1.0, 0.0, 0.0)

    def test_v_axis(self, sketch: Sketch) -> None:
        # Second external geom is V-axis: (0,0,0) -> (0,1,0)
        geom = sketch.ExternalGeo[1]
        assert isinstance(geom, GeomLineSegment)
        assert geom.StartPoint == Vector(0.0, 0.0, 0.0)
        assert geom.EndPoint == Vector(0.0, 1.0, 0.0)

    def test_external_geo_dict_keys(self, sketch: Sketch) -> None:
        assert set(sketch.ExternalGeoDict.keys()) == {-1, -2}

    def test_external_geo_dict_h_axis(self, sketch: Sketch) -> None:
        geom = sketch.ExternalGeoDict[-1]
        assert isinstance(geom, GeomLineSegment)
        assert geom.StartPoint == Vector(0.0, 0.0, 0.0)
        assert geom.EndPoint == Vector(1.0, 0.0, 0.0)

    def test_external_geo_dict_v_axis(self, sketch: Sketch) -> None:
        geom = sketch.ExternalGeoDict[-2]
        assert isinstance(geom, GeomLineSegment)
        assert geom.StartPoint == Vector(0.0, 0.0, 0.0)
        assert geom.EndPoint == Vector(0.0, 1.0, 0.0)


class TestConstraints:
    def test_constraint_count(self, sketch: Sketch) -> None:
        assert sketch.ConstraintCount == 16
        assert len(sketch.Constraints) == 16

    def test_first_constraint_type(self, sketch: Sketch) -> None:
        c = sketch.Constraints[0]
        assert c.Type == "Coincident"

    def test_first_constraint_geometry_refs(self, sketch: Sketch) -> None:
        c = sketch.Constraints[0]
        assert c.First == 0
        assert c.FirstPos == PointPos.start
        assert c.Second == -1
        assert c.SecondPos == PointPos.start

    def test_distance_constraint(self, sketch: Sketch) -> None:
        # Constraint 12 is Distance with Value=130
        c = sketch.Constraints[12]
        assert c.Type == "Distance"
        assert c.Value == pytest.approx(130.0)
        assert c.Driving is True

    def test_angle_constraint(self, sketch: Sketch) -> None:
        # Constraint 14 is Angle
        c = sketch.Constraints[14]
        assert c.Type == "Angle"
        assert c.Value == pytest.approx(0.6981320000000000)

    def test_point_on_object_constraint(self, sketch: Sketch) -> None:
        c = sketch.Constraints[1]
        assert c.Type == "PointOnObject"

    def test_perpendicular_constraint(self, sketch: Sketch) -> None:
        c = sketch.Constraints[3]
        assert c.Type == "Perpendicular"

    def test_horizontal_constraint(self, sketch: Sketch) -> None:
        c = sketch.Constraints[7]
        assert c.Type == "Horizontal"

    def test_vertical_constraint(self, sketch: Sketch) -> None:
        c = sketch.Constraints[9]
        assert c.Type == "Vertical"

    def test_tangent_constraint(self, sketch: Sketch) -> None:
        c = sketch.Constraints[13]
        assert c.Type == "Tangent"

    def test_all_constraints_active(self, sketch: Sketch) -> None:
        for c in sketch.Constraints:
            assert c.IsActive is True


class TestFullyConstrained:
    def test_not_fully_constrained(self, sketch: Sketch) -> None:
        assert sketch.FullyConstrained is False


class TestNoSketches:
    def test_empty_document(self, tmp_path: Path) -> None:
        xml = """<?xml version='1.0' encoding='utf-8'?>
        <Document SchemaVersion="4">
            <Objects Count="0"></Objects>
            <ObjectData Count="0"></ObjectData>
        </Document>"""
        xml_path = tmp_path / "Document.xml"
        xml_path.write_text(xml)
        result = read_sketches_from_xml(xml_path)
        assert result == {}
