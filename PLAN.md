# FreeCAD Sketch Reader - Plan

## Goal

Python library to read Sketch objects from FreeCAD `.FCStd` files (zip containing `Document.xml`).
Expose data via dataclasses that mirror the FreeCAD Python API property names.

## Package Structure

```
freecad_sketch_reader/
  __init__.py          # Public API: read_sketches(path) -> dict[str, Sketch]
  models.py            # All dataclasses
  parser.py            # XML parsing logic
  enums.py             # ConstraintType, PointPos enums
tests/
  test_reader.py       # Tests against Misc.FCStd
  Misc.FCStd
```

## Data Model (mirrors FreeCAD Python API names)

### Core types
- `Vector` - dataclass with `x`, `y`, `z` (matches FreeCAD `App.Vector`)

### Geometry types (match `sketch.Geometry[i]` properties)
- `GeomLineSegment` - `StartPoint`, `EndPoint`, `Construction`
- `GeomCircle` - `Center`, `Radius`, `AngleXU`, `Axis`, `Construction`
- `GeomArcOfCircle` - `Center`, `Radius`, `AngleXU`, `StartAngle`, `EndAngle`, `StartPoint`, `EndPoint`, `Construction`
- `GeomEllipse` - `Center`, `MajorRadius`, `MinorRadius`, `AngleXU`, `Axis`, `Construction`
- `GeomArcOfEllipse` - `Center`, `MajorRadius`, `MinorRadius`, `AngleXU`, `StartAngle`, `EndAngle`, `StartPoint`, `EndPoint`, `Construction`
- `GeomHyperbola` - `Center`, `MajorRadius`, `MinorRadius`, `AngleXU`, `Axis`, `Construction`
- `GeomArcOfHyperbola` - `Center`, `MajorRadius`, `MinorRadius`, `AngleXU`, `StartAngle`, `EndAngle`, `StartPoint`, `EndPoint`, `Construction`
- `GeomParabola` - `Center`, `Focal`, `AngleXU`, `Axis`, `Construction`
- `GeomArcOfParabola` - `Center`, `Focal`, `AngleXU`, `StartAngle`, `EndAngle`, `StartPoint`, `EndPoint`, `Construction`
- `GeomPoint` - `X`, `Y`, `Z`, `Construction`
- `GeomLine` - `Location`, `Direction`, `Construction` (infinite line, rare)
- `GeomBSplineCurve` - `Degree`, `IsPeriodic`, `Poles`, `Weights`, `Knots`, `Multiplicities`, `StartPoint`, `EndPoint`, `Construction`
- Union type: `Geometry = GeomLineSegment | GeomCircle | ... `

### Constraint (matches `sketch.Constraints[i]` properties)
- `Constraint` - `Type` (str), `Name`, `Value`, `First`, `FirstPos`, `Second`, `SecondPos`, `Third`, `ThirdPos`, `Driving`, `InVirtualSpace`, `IsActive`

### Sketch (matches `App.activeDocument().getObject("Sketch")` properties)
- `Sketch` - `Name`, `Label`, `Geometry`, `Constraints`, `ExternalGeo`, `FullyConstrained`, `GeometryCount`, `ConstraintCount`, `ExternalGeometryCount`

### Enums
- `ConstraintType` - IntEnum: None_=0, Coincident=1, ..., Weight=19
- `PointPos` - IntEnum: none=0, start=1, end=2, mid=3

## Steps

- [x] 1. Create PLAN.md
- [x] 2. Set up project with uv (pyproject.toml, ruff, pre-commit)
- [x] 3. Implement enums.py
- [x] 4. Implement models.py (all dataclasses)
- [x] 5. Implement parser.py (XML parsing)
- [x] 6. Implement __init__.py (public API)
- [x] 7. Write tests
- [x] 8. Run ruff, ty, pytest
- [x] 9. Final commit
