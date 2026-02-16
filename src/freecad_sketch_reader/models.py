"""Dataclasses mirroring FreeCAD Sketch Python API objects.

Property names match those exposed by the FreeCAD Python interface, e.g.
``sketch.Geometry[0].StartPoint.x`` or ``sketch.Constraints[0].First``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .enums import ConstraintTypeName, PointPos

__all__ = [
    "Constraint",
    "GeomArcOfCircle",
    "GeomArcOfEllipse",
    "GeomArcOfHyperbola",
    "GeomArcOfParabola",
    "GeomBSplineCurve",
    "GeomCircle",
    "GeomEllipse",
    "GeomHyperbola",
    "GeomLine",
    "GeomLineSegment",
    "GeomParabola",
    "GeomPoint",
    "Geometry",
    "Sketch",
    "Vector",
]


# ---------------------------------------------------------------------------
# Vector (mirrors FreeCAD App.Vector)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Vector:
    """3D vector, matching ``App.Vector``."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


# ---------------------------------------------------------------------------
# Constraint (mirrors Sketcher.Constraint)
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Constraint:
    """A single sketch constraint.

    ``Type`` is the human-readable string (e.g. ``"Distance"``).
    """

    Type: ConstraintTypeName
    Name: str = ""
    Value: float = 0.0
    First: int = -2000
    FirstPos: PointPos = PointPos.none
    Second: int = -2000
    SecondPos: PointPos = PointPos.none
    Third: int = -2000
    ThirdPos: PointPos = PointPos.none
    Driving: bool = True
    InVirtualSpace: bool = False
    IsActive: bool = True
    LabelDistance: float = 10.0
    LabelPosition: float = 0.0


# ---------------------------------------------------------------------------
# Geometry types (mirrors Part.* geometry objects)
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class GeomPoint:
    """A point in 3D space (``Part.Point``)."""

    X: float = 0.0
    Y: float = 0.0
    Z: float = 0.0
    Construction: bool = False


@dataclass(slots=True)
class GeomLine:
    """An infinite line (``Part.Line``). Rare in sketches."""

    Location: Vector = field(default_factory=Vector)
    Direction: Vector = field(default_factory=Vector)
    Construction: bool = False


@dataclass(slots=True)
class GeomLineSegment:
    """A line segment (``Part.LineSegment``)."""

    StartPoint: Vector = field(default_factory=Vector)
    EndPoint: Vector = field(default_factory=Vector)
    Construction: bool = False


@dataclass(slots=True)
class GeomCircle:
    """A full circle (``Part.Circle``)."""

    Center: Vector = field(default_factory=Vector)
    Radius: float = 0.0
    AngleXU: float = 0.0
    Axis: Vector = field(default_factory=lambda: Vector(0, 0, 1))
    Construction: bool = False


def _arc_point(
    center_x: float,
    center_y: float,
    center_z: float,
    radius: float,
    angle: float,
    angle_xu: float,
    normal_z: float,
) -> Vector:
    """Compute a point on a circular arc given the parameter angle."""
    effective_angle = angle_xu + angle
    x = center_x + radius * math.cos(effective_angle)
    y = center_y + radius * math.sin(effective_angle) * (1.0 if normal_z >= 0 else -1.0)
    return Vector(x, y, center_z)


@dataclass(slots=True)
class GeomArcOfCircle:
    """An arc of a circle (``Part.ArcOfCircle``)."""

    Center: Vector = field(default_factory=Vector)
    Radius: float = 0.0
    AngleXU: float = 0.0
    Axis: Vector = field(default_factory=lambda: Vector(0, 0, 1))
    StartAngle: float = 0.0
    EndAngle: float = 0.0
    Construction: bool = False

    @property
    def StartPoint(self) -> Vector:
        return _arc_point(
            self.Center.x,
            self.Center.y,
            self.Center.z,
            self.Radius,
            self.StartAngle,
            self.AngleXU,
            self.Axis.z,
        )

    @property
    def EndPoint(self) -> Vector:
        return _arc_point(
            self.Center.x,
            self.Center.y,
            self.Center.z,
            self.Radius,
            self.EndAngle,
            self.AngleXU,
            self.Axis.z,
        )

    @property
    def FirstParameter(self) -> float:
        return self.StartAngle

    @property
    def LastParameter(self) -> float:
        return self.EndAngle


def _ellipse_point(
    center_x: float,
    center_y: float,
    center_z: float,
    major_radius: float,
    minor_radius: float,
    angle: float,
    angle_xu: float,
    normal_z: float,
) -> Vector:
    """Compute a point on an elliptical arc given the parameter angle."""
    cos_xu = math.cos(angle_xu)
    sin_xu = math.sin(angle_xu)
    sign = 1.0 if normal_z >= 0 else -1.0
    local_x = major_radius * math.cos(angle)
    local_y = minor_radius * math.sin(angle)
    x = center_x + local_x * cos_xu - local_y * sin_xu * sign
    y = center_y + local_x * sin_xu + local_y * cos_xu * sign
    return Vector(x, y, center_z)


@dataclass(slots=True)
class GeomEllipse:
    """A full ellipse (``Part.Ellipse``)."""

    Center: Vector = field(default_factory=Vector)
    MajorRadius: float = 0.0
    MinorRadius: float = 0.0
    AngleXU: float = 0.0
    Axis: Vector = field(default_factory=lambda: Vector(0, 0, 1))
    Construction: bool = False

    @property
    def Focal(self) -> float:
        return math.sqrt(abs(self.MajorRadius**2 - self.MinorRadius**2))

    @property
    def Focus1(self) -> Vector:
        cos_xu = math.cos(self.AngleXU)
        sin_xu = math.sin(self.AngleXU)
        f = self.Focal
        return Vector(
            self.Center.x + f * cos_xu,
            self.Center.y + f * sin_xu,
            self.Center.z,
        )

    @property
    def Focus2(self) -> Vector:
        cos_xu = math.cos(self.AngleXU)
        sin_xu = math.sin(self.AngleXU)
        f = self.Focal
        return Vector(
            self.Center.x - f * cos_xu,
            self.Center.y - f * sin_xu,
            self.Center.z,
        )


@dataclass(slots=True)
class GeomArcOfEllipse:
    """An arc of an ellipse (``Part.ArcOfEllipse``)."""

    Center: Vector = field(default_factory=Vector)
    MajorRadius: float = 0.0
    MinorRadius: float = 0.0
    AngleXU: float = 0.0
    Axis: Vector = field(default_factory=lambda: Vector(0, 0, 1))
    StartAngle: float = 0.0
    EndAngle: float = 0.0
    Construction: bool = False

    @property
    def StartPoint(self) -> Vector:
        return _ellipse_point(
            self.Center.x,
            self.Center.y,
            self.Center.z,
            self.MajorRadius,
            self.MinorRadius,
            self.StartAngle,
            self.AngleXU,
            self.Axis.z,
        )

    @property
    def EndPoint(self) -> Vector:
        return _ellipse_point(
            self.Center.x,
            self.Center.y,
            self.Center.z,
            self.MajorRadius,
            self.MinorRadius,
            self.EndAngle,
            self.AngleXU,
            self.Axis.z,
        )

    @property
    def FirstParameter(self) -> float:
        return self.StartAngle

    @property
    def LastParameter(self) -> float:
        return self.EndAngle


@dataclass(slots=True)
class GeomHyperbola:
    """A full hyperbola (``Part.Hyperbola``)."""

    Center: Vector = field(default_factory=Vector)
    MajorRadius: float = 0.0
    MinorRadius: float = 0.0
    AngleXU: float = 0.0
    Axis: Vector = field(default_factory=lambda: Vector(0, 0, 1))
    Construction: bool = False


@dataclass(slots=True)
class GeomArcOfHyperbola:
    """An arc of a hyperbola (``Part.ArcOfHyperbola``)."""

    Center: Vector = field(default_factory=Vector)
    MajorRadius: float = 0.0
    MinorRadius: float = 0.0
    AngleXU: float = 0.0
    Axis: Vector = field(default_factory=lambda: Vector(0, 0, 1))
    StartAngle: float = 0.0
    EndAngle: float = 0.0
    Construction: bool = False

    @property
    def StartPoint(self) -> Vector:
        cos_xu = math.cos(self.AngleXU)
        sin_xu = math.sin(self.AngleXU)
        sign = 1.0 if self.Axis.z >= 0 else -1.0
        a, b = self.MajorRadius, self.MinorRadius
        local_x = a * math.cosh(self.StartAngle)
        local_y = b * math.sinh(self.StartAngle)
        return Vector(
            self.Center.x + local_x * cos_xu - local_y * sin_xu * sign,
            self.Center.y + local_x * sin_xu + local_y * cos_xu * sign,
            self.Center.z,
        )

    @property
    def EndPoint(self) -> Vector:
        cos_xu = math.cos(self.AngleXU)
        sin_xu = math.sin(self.AngleXU)
        sign = 1.0 if self.Axis.z >= 0 else -1.0
        a, b = self.MajorRadius, self.MinorRadius
        local_x = a * math.cosh(self.EndAngle)
        local_y = b * math.sinh(self.EndAngle)
        return Vector(
            self.Center.x + local_x * cos_xu - local_y * sin_xu * sign,
            self.Center.y + local_x * sin_xu + local_y * cos_xu * sign,
            self.Center.z,
        )

    @property
    def FirstParameter(self) -> float:
        return self.StartAngle

    @property
    def LastParameter(self) -> float:
        return self.EndAngle


@dataclass(slots=True)
class GeomParabola:
    """A full parabola (``Part.Parabola``)."""

    Center: Vector = field(default_factory=Vector)
    Focal: float = 0.0
    AngleXU: float = 0.0
    Axis: Vector = field(default_factory=lambda: Vector(0, 0, 1))
    Construction: bool = False


@dataclass(slots=True)
class GeomArcOfParabola:
    """An arc of a parabola (``Part.ArcOfParabola``)."""

    Center: Vector = field(default_factory=Vector)
    Focal: float = 0.0
    AngleXU: float = 0.0
    Axis: Vector = field(default_factory=lambda: Vector(0, 0, 1))
    StartAngle: float = 0.0
    EndAngle: float = 0.0
    Construction: bool = False

    @property
    def StartPoint(self) -> Vector:
        cos_xu = math.cos(self.AngleXU)
        sin_xu = math.sin(self.AngleXU)
        sign = 1.0 if self.Axis.z >= 0 else -1.0
        p = 2.0 * self.Focal
        t = self.StartAngle
        local_x = p * t * t / 2.0
        local_y = p * t
        return Vector(
            self.Center.x + local_x * cos_xu - local_y * sin_xu * sign,
            self.Center.y + local_x * sin_xu + local_y * cos_xu * sign,
            self.Center.z,
        )

    @property
    def EndPoint(self) -> Vector:
        cos_xu = math.cos(self.AngleXU)
        sin_xu = math.sin(self.AngleXU)
        sign = 1.0 if self.Axis.z >= 0 else -1.0
        p = 2.0 * self.Focal
        t = self.EndAngle
        local_x = p * t * t / 2.0
        local_y = p * t
        return Vector(
            self.Center.x + local_x * cos_xu - local_y * sin_xu * sign,
            self.Center.y + local_x * sin_xu + local_y * cos_xu * sign,
            self.Center.z,
        )

    @property
    def FirstParameter(self) -> float:
        return self.StartAngle

    @property
    def LastParameter(self) -> float:
        return self.EndAngle


@dataclass(slots=True)
class BSplinePole:
    """A single pole of a B-spline curve with its weight."""

    Point: Vector = field(default_factory=Vector)
    Weight: float = 1.0


@dataclass(slots=True)
class BSplineKnot:
    """A single knot of a B-spline curve with its multiplicity."""

    Value: float = 0.0
    Mult: int = 1


@dataclass(slots=True)
class GeomBSplineCurve:
    """A B-spline curve (``Part.BSplineCurve``)."""

    Degree: int = 0
    IsPeriodic: bool = False
    Poles: list[BSplinePole] = field(default_factory=list)
    Knots: list[BSplineKnot] = field(default_factory=list)
    Construction: bool = False

    @property
    def NbPoles(self) -> int:
        return len(self.Poles)

    @property
    def NbKnots(self) -> int:
        return len(self.Knots)

    @property
    def StartPoint(self) -> Vector:
        if self.Poles:
            return self.Poles[0].Point
        return Vector()

    @property
    def EndPoint(self) -> Vector:
        if self.Poles:
            return self.Poles[-1].Point
        return Vector()

    @property
    def KnotSequence(self) -> list[float]:
        seq: list[float] = []
        for k in self.Knots:
            seq.extend([k.Value] * k.Mult)
        return seq


# Union of all geometry types that can appear in a sketch.
# Named with underscore prefix to avoid shadowing by the Sketch.Geometry field;
# re-exported as ``Geometry`` in __all__ and __init__.
type _GeometryType = (
    GeomPoint
    | GeomLine
    | GeomLineSegment
    | GeomCircle
    | GeomArcOfCircle
    | GeomEllipse
    | GeomArcOfEllipse
    | GeomHyperbola
    | GeomArcOfHyperbola
    | GeomParabola
    | GeomArcOfParabola
    | GeomBSplineCurve
)
Geometry = _GeometryType


# ---------------------------------------------------------------------------
# Sketch (mirrors Sketcher::SketchObject top-level properties)
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class Sketch:
    """A Sketch object matching ``App.activeDocument().getObject("Sketch")``."""

    Name: str = ""
    Label: str = ""
    Geometry: list[_GeometryType] = field(default_factory=list)
    Constraints: list[Constraint] = field(default_factory=list)
    ExternalGeo: list[_GeometryType] = field(default_factory=list)
    FullyConstrained: bool = False

    @property
    def GeometryCount(self) -> int:
        return len(self.Geometry)

    @property
    def ConstraintCount(self) -> int:
        return len(self.Constraints)

    @property
    def ExternalGeometryCount(self) -> int:
        return len(self.ExternalGeo)
