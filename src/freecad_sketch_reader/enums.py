"""Enums matching FreeCAD Sketcher internal types."""

from enum import IntEnum

__all__ = ["ConstraintType", "InternalAlignmentType", "PointPos"]


class ConstraintType(IntEnum):
    """Sketcher constraint types, matching Sketcher::ConstraintType."""

    NONE = 0
    Coincident = 1
    Horizontal = 2
    Vertical = 3
    Parallel = 4
    Tangent = 5
    Distance = 6
    DistanceX = 7
    DistanceY = 8
    Angle = 9
    Perpendicular = 10
    Radius = 11
    Equal = 12
    PointOnObject = 13
    Symmetric = 14
    InternalAlignment = 15
    SnellsLaw = 16
    Block = 17
    Diameter = 18
    Weight = 19


# String names used by the FreeCAD Python API for Constraint.Type
CONSTRAINT_TYPE_NAMES: dict[int, str] = {
    0: "None",
    1: "Coincident",
    2: "Horizontal",
    3: "Vertical",
    4: "Parallel",
    5: "Tangent",
    6: "Distance",
    7: "DistanceX",
    8: "DistanceY",
    9: "Angle",
    10: "Perpendicular",
    11: "Radius",
    12: "Equal",
    13: "PointOnObject",
    14: "Symmetric",
    15: "InternalAlignment",
    16: "SnellsLaw",
    17: "Block",
    18: "Diameter",
    19: "Weight",
}


class PointPos(IntEnum):
    """Point position enum, matching Sketcher::PointPos."""

    none = 0
    start = 1
    end = 2
    mid = 3


class InternalAlignmentType(IntEnum):
    """Internal alignment sub-type, matching Sketcher::InternalAlignmentType."""

    Undef = 0
    EllipseMajorDiameter = 1
    EllipseMinorDiameter = 2
    EllipseFocus1 = 3
    EllipseFocus2 = 4
    HyperbolaMajor = 5
    HyperbolaMinor = 6
    HyperbolaFocus = 7
    ParabolaFocus = 8
    BSplineControlPoint = 9
    BSplineKnotPoint = 10
    ParabolaFocalAxis = 11
