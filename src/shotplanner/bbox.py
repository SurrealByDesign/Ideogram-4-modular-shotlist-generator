from __future__ import annotations

from typing import Any

BBox = list[int]


def validate_bbox(bbox: list[Any]) -> None:
    if not isinstance(bbox, list) or len(bbox) != 4:
        raise ValueError("bbox must be a list of four coordinates")
    if any(not isinstance(coord, int) for coord in bbox):
        raise ValueError("bbox coordinates must be integers")

    y_min, x_min, y_max, x_max = bbox
    if not (0 <= y_min < y_max <= 1000):
        raise ValueError("bbox y coordinates must satisfy 0 <= y_min < y_max <= 1000")
    if not (0 <= x_min < x_max <= 1000):
        raise ValueError("bbox x coordinates must satisfy 0 <= x_min < x_max <= 1000")


def validate_layout(layout: dict[str, Any]) -> None:
    if not layout.get("name"):
        raise ValueError("layout must include a name")
    if not layout.get("aspect_ratio"):
        raise ValueError("layout must include an aspect_ratio")
    elements = layout.get("elements")
    if not isinstance(elements, list) or not elements:
        raise ValueError("layout must include at least one element")
    for element in elements:
        if not isinstance(element, dict):
            raise ValueError("layout elements must be dictionaries")
        if "type" not in element or "desc" not in element or "bbox" not in element:
            raise ValueError("layout elements must include type, desc, and bbox")
        validate_bbox(element["bbox"])
