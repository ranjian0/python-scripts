from .collision import (
    CircletoCircle,
    CircletoPolygon,
    PolygontoCircle,
    PolygontoPolygon
)

Dispatch = [
    [CircletoCircle, CircletoPolygon],
    [PolygontoCircle, PolygontoPolygon]
]
