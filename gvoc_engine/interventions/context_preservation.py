"""Deterministic crop validation for context-preserving visual evidence acquisition.

Boxes use integer pixel coordinates [ymin, xmin, ymax, xmax] with exclusive
maximum bounds. Required context regions must come from annotation or a
grounded locator; geometry alone cannot infer semantic context.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, List, Tuple, Sequence

Box = Tuple[int, int, int, int]


class ContextKind(str, Enum):
    TABLE_HEADER = "table_header"
    ROW_LABEL = "row_label"
    COLUMN_LABEL = "column_label"
    UNIT = "unit"
    LEGEND = "legend"
    AXIS_TICK = "axis_tick"
    FOOTNOTE = "footnote"
    NEIGHBORING_CELL = "neighboring_cell"


@dataclass(frozen=True)
class EvidenceRegion:
    target_box: Box
    required_context: Tuple[Tuple[ContextKind, Box], ...] = ()
    evidence_id: str = ""


@dataclass(frozen=True)
class CropAssessment:
    valid: bool
    target_retained: bool
    retained_context: Tuple[ContextKind, ...]
    missing_context: Tuple[ContextKind, ...]
    coverage: float


def _valid_box(box: Sequence[int], width: int, height: int) -> bool:
    return (
        len(box) == 4
        and all(isinstance(v, int) for v in box)
        and 0 <= box[0] < box[2] <= height
        and 0 <= box[1] < box[3] <= width
    )


def intersection_area(a: Box, b: Box) -> int:
    y0, x0 = max(a[0], b[0]), max(a[1], b[1])
    y1, x1 = min(a[2], b[2]), min(a[3], b[3])
    return max(0, y1 - y0) * max(0, x1 - x0)


def containment_ratio(region: Box, crop: Box) -> float:
    area = max(0, region[2] - region[0]) * max(0, region[3] - region[1])
    return 0.0 if area == 0 else intersection_area(region, crop) / area


def expand_box(box: Box, width: int, height: int, margin_fraction: float = 0.20) -> Box:
    """Expand a valid box and clip it to image boundaries."""
    if width <= 0 or height <= 0:
        raise ValueError("Image width and height must be positive.")
    if not 0.0 <= margin_fraction <= 2.0:
        raise ValueError("margin_fraction must be in [0, 2].")
    if not _valid_box(box, width, height):
        raise ValueError("box must be a valid [ymin, xmin, ymax, xmax] image box.")
    y0, x0, y1, x1 = box
    dy, dx = round((y1 - y0) * margin_fraction), round((x1 - x0) * margin_fraction)
    return max(0, y0-dy), max(0, x0-dx), min(height, y1+dy), min(width, x1+dx)


def assess_crop(
    crop_box: Box,
    evidence: EvidenceRegion,
    image_width: int,
    image_height: int,
    min_target_coverage: float = 0.98,
    min_context_coverage: float = 0.95,
) -> CropAssessment:
    """Reject a crop if it loses the target or any required context region."""
    if not _valid_box(crop_box, image_width, image_height):
        raise ValueError("crop_box must be a valid image box.")
    if not 0.0 <= min_target_coverage <= 1.0 or not 0.0 <= min_context_coverage <= 1.0:
        raise ValueError("Coverage thresholds must be in [0, 1].")
    if not _valid_box(evidence.target_box, image_width, image_height):
        raise ValueError("target_box must be a valid image box.")
    for _, box in evidence.required_context:
        if not _valid_box(box, image_width, image_height):
            raise ValueError("Each context box must be valid and inside the image.")

    target_cov = containment_ratio(evidence.target_box, crop_box)
    retained: List[ContextKind] = []
    missing: List[ContextKind] = []
    coverages = [target_cov]
    for kind, box in evidence.required_context:
        ratio = containment_ratio(box, crop_box)
        coverages.append(ratio)
        (retained if ratio >= min_context_coverage else missing).append(kind)
    target_ok = target_cov >= min_target_coverage
    return CropAssessment(
        valid=target_ok and not missing,
        target_retained=target_ok,
        retained_context=tuple(retained),
        missing_context=tuple(missing),
        coverage=sum(coverages) / len(coverages),
    )


def propose_context_preserving_crop(
    target_box: Box,
    required_context_boxes: Iterable[Box],
    width: int,
    height: int,
    margin_fraction: float = 0.05,
) -> Box:
    """Build a box covering target plus declared context, then add a margin."""
    boxes = [target_box, *list(required_context_boxes)]
    if not boxes or any(not _valid_box(b, width, height) for b in boxes):
        raise ValueError("Every target/context box must be valid and inside the image.")
    union = (
        min(b[0] for b in boxes), min(b[1] for b in boxes),
        max(b[2] for b in boxes), max(b[3] for b in boxes),
    )
    return expand_box(union, width, height, margin_fraction)
