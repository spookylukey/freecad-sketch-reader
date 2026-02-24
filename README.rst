=====================
freecad-sketch-reader
=====================

Small library to read FreeCAD files and extract Sketch information.

The Sketch objects returned have a read-only API that mirrors the Python API
that can be used to examine a Sketch from within FreeCAD.

Installation::

    pip install freecad-sketch-reader


Or::

  uv add freecad-sketch-reader


Quick start:

.. code-block:: python

  >>> import freecad_sketch_reader
  >>> sketches = freecad_sketch_reader.read_sketches("MyFile.FCStd")
  >>> sketch = sketches['MySketch'].Geometry[0]
  GeomLineSegment(StartPoint=Vector(x=0.0, y=0.0, z=0.0), EndPoint=Vector(x=67.54724367780743, y=0.0, z=0.0), Construction=False)
