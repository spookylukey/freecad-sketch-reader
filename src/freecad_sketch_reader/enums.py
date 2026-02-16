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
CONSTRAINT_TYPE_NAMES: dict[ConstraintType, str] = {
    ConstraintType.NONE: "None",
    ConstraintType.Coincident: "Coincident",
    ConstraintType.Horizontal: "Horizontal",
    ConstraintType.Vertical: "Vertical",
    ConstraintType.Parallel: "Parallel",
    ConstraintType.Tangent: "Tangent",
    ConstraintType.Distance: "Distance",
    ConstraintType.DistanceX: "DistanceX",
    ConstraintType.DistanceY: "DistanceY",
    ConstraintType.Angle: "Angle",
    ConstraintType.Perpendicular: "Perpendicular",
    ConstraintType.Radius: "Radius",
    ConstraintType.Equal: "Equal",
    ConstraintType.PointOnObject: "PointOnObject",
    ConstraintType.Symmetric: "Symmetric",
    ConstraintType.InternalAlignment: "InternalAlignment",
    ConstraintType.SnellsLaw: "SnellsLaw",
    ConstraintType.Block: "Block",
    ConstraintType.Diameter: "Diameter",
    ConstraintType.Weight: "Weight",
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
