"""Parse FreeCAD Document.xml to extract Sketch objects."""

from __future__ import annotations

import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import IO

from .enums import CONSTRAINT_TYPE_NAMES, ConstraintType, PointPos
from .models import (
    BSplineKnot,
    BSplinePole,
    Constraint,
    GeomArcOfCircle,
    GeomArcOfEllipse,
    GeomArcOfHyperbola,
    GeomArcOfParabola,
    GeomBSplineCurve,
    GeomCircle,
    GeomEllipse,
    Geometry,
    GeomHyperbola,
    GeomLine,
    GeomLineSegment,
    GeomParabola,
    GeomPoint,
    Sketch,
    Vector,
)

__all__ = ["read_sketches", "read_sketches_from_xml"]


# ---------------------------------------------------------------------------
# Geometry XML parsing
# ---------------------------------------------------------------------------


def _parse_construction(geom_el: ET.Element) -> bool:
    cons_el = geom_el.find("Construction")
    if cons_el is not None:
        return cons_el.get("value", "0") == "1"
    return False


def _float(el: ET.Element, attr: str, default: float = 0.0) -> float:
    val = el.get(attr)
    return float(val) if val is not None else default


def _int(el: ET.Element, attr: str, default: int = 0) -> int:
    val = el.get(attr)
    return int(val) if val is not None else default


def _axis_from(el: ET.Element) -> Vector:
    return Vector(
        _float(el, "NormalX"),
        _float(el, "NormalY"),
        _float(el, "NormalZ", 1.0),
    )


def _parse_geometry_element(geom_el: ET.Element) -> Geometry:
    """Parse a single <Geometry type="..."> element."""
    geom_type = geom_el.get("type", "")
    construction = _parse_construction(geom_el)

    def _require(tag: str) -> ET.Element:
        el = geom_el.find(tag)
        if el is None:
            msg = f"Missing <{tag}> child element in <Geometry type='{geom_type}'>"
            raise ValueError(msg)
        return el

    match geom_type:
        case "Part::GeomPoint":
            pt_el = _require("GeomPoint")
            return GeomPoint(
                X=_float(pt_el, "X"),
                Y=_float(pt_el, "Y"),
                Z=_float(pt_el, "Z"),
                Construction=construction,
            )

        case "Part::GeomLine":
            line_el = _require("GeomLine")
            return GeomLine(
                Location=Vector(
                    _float(line_el, "PosX"), _float(line_el, "PosY"), _float(line_el, "PosZ")
                ),
                Direction=Vector(
                    _float(line_el, "DirX"), _float(line_el, "DirY"), _float(line_el, "DirZ")
                ),
                Construction=construction,
            )

        case "Part::GeomLineSegment":
            ls_el = _require("LineSegment")
            return GeomLineSegment(
                StartPoint=Vector(
                    _float(ls_el, "StartX"), _float(ls_el, "StartY"), _float(ls_el, "StartZ")
                ),
                EndPoint=Vector(
                    _float(ls_el, "EndX"), _float(ls_el, "EndY"), _float(ls_el, "EndZ")
                ),
                Construction=construction,
            )

        case "Part::GeomCircle":
            c_el = _require("Circle")
            return GeomCircle(
                Center=Vector(
                    _float(c_el, "CenterX"), _float(c_el, "CenterY"), _float(c_el, "CenterZ")
                ),
                Radius=_float(c_el, "Radius"),
                AngleXU=_float(c_el, "AngleXU"),
                Axis=_axis_from(c_el),
                Construction=construction,
            )

        case "Part::GeomArcOfCircle":
            a_el = _require("ArcOfCircle")
            return GeomArcOfCircle(
                Center=Vector(
                    _float(a_el, "CenterX"), _float(a_el, "CenterY"), _float(a_el, "CenterZ")
                ),
                Radius=_float(a_el, "Radius"),
                AngleXU=_float(a_el, "AngleXU"),
                Axis=_axis_from(a_el),
                StartAngle=_float(a_el, "StartAngle"),
                EndAngle=_float(a_el, "EndAngle"),
                Construction=construction,
            )

        case "Part::GeomEllipse":
            e_el = _require("Ellipse")
            return GeomEllipse(
                Center=Vector(
                    _float(e_el, "CenterX"), _float(e_el, "CenterY"), _float(e_el, "CenterZ")
                ),
                MajorRadius=_float(e_el, "MajorRadius"),
                MinorRadius=_float(e_el, "MinorRadius"),
                AngleXU=_float(e_el, "AngleXU"),
                Axis=_axis_from(e_el),
                Construction=construction,
            )

        case "Part::GeomArcOfEllipse":
            ae_el = _require("ArcOfEllipse")
            return GeomArcOfEllipse(
                Center=Vector(
                    _float(ae_el, "CenterX"), _float(ae_el, "CenterY"), _float(ae_el, "CenterZ")
                ),
                MajorRadius=_float(ae_el, "MajorRadius"),
                MinorRadius=_float(ae_el, "MinorRadius"),
                AngleXU=_float(ae_el, "AngleXU"),
                Axis=_axis_from(ae_el),
                StartAngle=_float(ae_el, "StartAngle"),
                EndAngle=_float(ae_el, "EndAngle"),
                Construction=construction,
            )

        case "Part::GeomHyperbola":
            h_el = _require("Hyperbola")
            return GeomHyperbola(
                Center=Vector(
                    _float(h_el, "CenterX"), _float(h_el, "CenterY"), _float(h_el, "CenterZ")
                ),
                MajorRadius=_float(h_el, "MajorRadius"),
                MinorRadius=_float(h_el, "MinorRadius"),
                AngleXU=_float(h_el, "AngleXU"),
                Axis=_axis_from(h_el),
                Construction=construction,
            )

        case "Part::GeomArcOfHyperbola":
            ah_el = _require("ArcOfHyperbola")
            return GeomArcOfHyperbola(
                Center=Vector(
                    _float(ah_el, "CenterX"), _float(ah_el, "CenterY"), _float(ah_el, "CenterZ")
                ),
                MajorRadius=_float(ah_el, "MajorRadius"),
                MinorRadius=_float(ah_el, "MinorRadius"),
                AngleXU=_float(ah_el, "AngleXU"),
                Axis=_axis_from(ah_el),
                StartAngle=_float(ah_el, "StartAngle"),
                EndAngle=_float(ah_el, "EndAngle"),
                Construction=construction,
            )

        case "Part::GeomParabola":
            p_el = _require("Parabola")
            return GeomParabola(
                Center=Vector(
                    _float(p_el, "CenterX"), _float(p_el, "CenterY"), _float(p_el, "CenterZ")
                ),
                Focal=_float(p_el, "Focal"),
                AngleXU=_float(p_el, "AngleXU"),
                Axis=_axis_from(p_el),
                Construction=construction,
            )

        case "Part::GeomArcOfParabola":
            ap_el = _require("ArcOfParabola")
            return GeomArcOfParabola(
                Center=Vector(
                    _float(ap_el, "CenterX"), _float(ap_el, "CenterY"), _float(ap_el, "CenterZ")
                ),
                Focal=_float(ap_el, "Focal"),
                AngleXU=_float(ap_el, "AngleXU"),
                Axis=_axis_from(ap_el),
                StartAngle=_float(ap_el, "StartAngle"),
                EndAngle=_float(ap_el, "EndAngle"),
                Construction=construction,
            )

        case "Part::GeomBSplineCurve":
            bs_el = _require("BSplineCurve")
            poles: list[BSplinePole] = []
            knots: list[BSplineKnot] = []
            for child in bs_el:
                if child.tag == "Pole":
                    poles.append(
                        BSplinePole(
                            Point=Vector(
                                _float(child, "X"), _float(child, "Y"), _float(child, "Z")
                            ),
                            Weight=_float(child, "Weight", 1.0),
                        )
                    )
                elif child.tag == "Knot":
                    knots.append(
                        BSplineKnot(
                            Value=_float(child, "Value"),
                            Mult=_int(child, "Mult", 1),
                        )
                    )
            return GeomBSplineCurve(
                Degree=_int(bs_el, "Degree"),
                IsPeriodic=bs_el.get("IsPeriodic", "0") == "1",
                Poles=tuple(poles),
                Knots=tuple(knots),
                Construction=construction,
            )

        case _:
            msg = f"Unknown geometry type: {geom_type!r}"
            raise ValueError(msg)


def _parse_geometry_list(prop_el: ET.Element) -> list[Geometry]:
    """Parse a <GeometryList> element."""
    geom_list_el = prop_el.find("GeometryList")
    if geom_list_el is None:
        return []
    result: list[Geometry] = []
    for geom_el in geom_list_el.findall("Geometry"):
        result.append(_parse_geometry_element(geom_el))
    return result


def _parse_geometry_dict(prop_el: ET.Element) -> dict[int, Geometry]:
    """Parse a <GeometryList> element, returning a dict keyed by geometry id."""
    geom_list_el = prop_el.find("GeometryList")
    if geom_list_el is None:
        return {}
    result: dict[int, Geometry] = {}
    for geom_el in geom_list_el.findall("Geometry"):
        geo_id = geom_el.get("id")
        if geo_id is not None:
            result[int(geo_id)] = _parse_geometry_element(geom_el)
    return result


# ---------------------------------------------------------------------------
# Constraint XML parsing
# ---------------------------------------------------------------------------


def _parse_constraints(prop_el: ET.Element) -> list[Constraint]:
    """Parse a <ConstraintList> element."""
    cl_el = prop_el.find("ConstraintList")
    if cl_el is None:
        return []
    result: list[Constraint] = []
    for c_el in cl_el.findall("Constrain"):
        type_int = _int(c_el, "Type")
        try:
            type_enum = ConstraintType(type_int)
        except ValueError as err:
            raise AssertionError(f"Unknown constraint type {type_int}") from err
        type_str = CONSTRAINT_TYPE_NAMES[type_enum]
        result.append(
            Constraint(
                Type=type_str,
                Name=c_el.get("Name", ""),
                Value=_float(c_el, "Value"),
                First=_int(c_el, "First", -2000),
                FirstPos=PointPos(_int(c_el, "FirstPos")),
                Second=_int(c_el, "Second", -2000),
                SecondPos=PointPos(_int(c_el, "SecondPos")),
                Third=_int(c_el, "Third", -2000),
                ThirdPos=PointPos(_int(c_el, "ThirdPos")),
                Driving=c_el.get("IsDriving", "1") == "1",
                InVirtualSpace=c_el.get("IsInVirtualSpace", "0") == "1",
                IsActive=c_el.get("IsActive", "1") == "1",
                LabelDistance=_float(c_el, "LabelDistance", 10.0),
                LabelPosition=_float(c_el, "LabelPosition"),
            )
        )
    return result


# ---------------------------------------------------------------------------
# Sketch assembly
# ---------------------------------------------------------------------------


def _find_property(properties_el: ET.Element, name: str) -> ET.Element | None:
    """Find a <Property name="..."> child element."""
    for prop in properties_el:
        if prop.tag == "Property" and prop.get("name") == name:
            return prop
    return None


def _parse_sketch_object(obj_data_el: ET.Element, obj_name: str) -> Sketch:
    """Parse an <Object name="..."> element from <ObjectData>."""
    props_el = obj_data_el.find("Properties")
    if props_el is None:
        return Sketch(Name=obj_name)

    # Label
    label = obj_name
    label_prop = _find_property(props_el, "Label")
    if label_prop is not None:
        str_el = label_prop.find("String")
        if str_el is not None:
            label = str_el.get("value", obj_name)

    # Geometry
    geom_prop = _find_property(props_el, "Geometry")
    geometry = _parse_geometry_list(geom_prop) if geom_prop is not None else []

    # ExternalGeo
    ext_prop = _find_property(props_el, "ExternalGeo")
    external_geo = _parse_geometry_list(ext_prop) if ext_prop is not None else []
    external_geo_dict = _parse_geometry_dict(ext_prop) if ext_prop is not None else {}

    # Constraints
    cons_prop = _find_property(props_el, "Constraints")
    constraints = _parse_constraints(cons_prop) if cons_prop is not None else []

    # FullyConstrained
    fully_constrained = False
    fc_prop = _find_property(props_el, "FullyConstrained")
    if fc_prop is not None:
        bool_el = fc_prop.find("Bool")
        if bool_el is not None:
            fully_constrained = bool_el.get("value", "false") == "true"

    return Sketch(
        Name=obj_name,
        Label=label,
        Geometry=geometry,
        Constraints=constraints,
        ExternalGeo=external_geo,
        ExternalGeoDict=external_geo_dict,
        FullyConstrained=fully_constrained,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def _sketch_object_names(root: ET.Element) -> set[str]:
    """Return names of all Sketcher::SketchObject objects."""
    names: set[str] = set()
    objects_el = root.find("Objects")
    if objects_el is None:
        return names
    for obj_el in objects_el.findall("Object"):
        if obj_el.get("type") == "Sketcher::SketchObject":
            name = obj_el.get("name")
            if name:
                names.add(name)
    return names


def read_sketches_from_xml(source: str | Path | IO[bytes]) -> dict[str, Sketch]:
    """Read sketches from a Document.xml file or file-like object.

    Returns a dict mapping object name -> Sketch.
    """
    tree = ET.parse(source)
    root = tree.getroot()

    sketch_names = _sketch_object_names(root)
    if not sketch_names:
        return {}

    sketches: dict[str, Sketch] = {}
    object_data = root.find("ObjectData")
    if object_data is None:
        return sketches

    for obj_el in object_data.findall("Object"):
        name = obj_el.get("name", "")
        if name in sketch_names:
            sketches[name] = _parse_sketch_object(obj_el, name)

    return sketches


def read_sketches(path: str | Path) -> dict[str, Sketch]:
    """Read sketches from an ``.FCStd`` file.

    Parameters
    ----------
    path:
        Path to the ``.FCStd`` file (a zip archive containing ``Document.xml``).

    Returns
    -------
    dict[str, Sketch]
        Mapping of object name to :class:`Sketch`.
    """
    path = Path(path)
    with zipfile.ZipFile(path, "r") as zf, zf.open("Document.xml") as f:
        return read_sketches_from_xml(f)
