"""Shared image preprocessing pipeline used by training, evaluation and inference.

The pipeline is deterministic, config-driven and preserves aspect ratio. It is
the only preprocessing implementation in the project (no train/serve skew).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import cv2
import numpy as np
import torch


class PreprocessingError(ValueError):
    """Raised when an image cannot be preprocessed under the current config."""


@dataclass(frozen=True)
class PreprocessedSample:
    """A single normalized line image ready for the model."""

    tensor: torch.Tensor
    input_length: int
    width: int
    height: int
    pad_value: float
    warnings: tuple[str, ...]


def _decode_image(image: bytes | str | Path | np.ndarray) -> np.ndarray:
    """Decode an image from bytes, path or array into a BGR numpy array."""
    if isinstance(image, np.ndarray):
        if image.ndim not in {2, 3}:
            raise PreprocessingError("numpy image must be 2-D or 3-D")
        return image.copy()
    if isinstance(image, (str, Path)):
        decoded = cv2.imread(str(image), cv2.IMREAD_COLOR)
        if decoded is None:
            raise PreprocessingError(f"Could not decode image: {image}")
        return decoded
    if isinstance(image, bytes):
        buffer = np.frombuffer(image, dtype=np.uint8)
        decoded = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
        if decoded is None:
            raise PreprocessingError("Could not decode image bytes")
        return decoded
    raise PreprocessingError(f"Unsupported image input type: {type(image).__name__}")


def _deskew(binary: np.ndarray, max_angle: float) -> np.ndarray:
    """Rotate a binary image by a small detected skew angle."""
    points = cv2.findNonZero(binary)
    if points is None or len(points) < 4:
        return binary
    angle = cv2.minAreaRect(points)[2]
    if angle > 45:
        angle -= 90
    if abs(angle) > max_angle:
        return binary
    center = (binary.shape[1] / 2.0, binary.shape[0] / 2.0)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(binary, matrix, (binary.shape[1], binary.shape[0]), flags=cv2.INTER_LINEAR, borderValue=0)


def preprocess_image(image: bytes | str | Path | np.ndarray, config: Mapping[str, Any]) -> PreprocessedSample:
    """Run the configured preprocessing pipeline on one text-line image."""
    cfg = config["preprocessing"]
    warnings: list[str] = []
    decoded = _decode_image(image)

    if decoded.ndim == 3:
        if cfg.get("grayscale", True):
            gray = cv2.cvtColor(decoded, cv2.COLOR_BGR2GRAY)
        else:
            gray = cv2.cvtColor(decoded, cv2.COLOR_BGR2GRAY)
            warnings.append("grayscale disabled but input is colour; converted to single channel")
    else:
        gray = decoded

    denoise_cfg = cfg["denoise"]
    if denoise_cfg.get("method", "none") == "median":
        kernel = int(denoise_cfg.get("kernel_size", 3))
        if kernel % 2 == 0:
            kernel += 1
            warnings.append("denoise kernel adjusted to odd value")
        if kernel > 1:
            gray = cv2.medianBlur(gray, kernel)

    bin_cfg = cfg["binarization"]
    if bin_cfg.get("method", "otsu") == "adaptive":
        block = int(bin_cfg.get("block_size", 11))
        if block % 2 == 0:
            block += 1
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block, int(bin_cfg.get("constant", 2))
        )
    else:
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    deskew_cfg = cfg["deskew"]
    if deskew_cfg.get("enabled", False):
        binary = _deskew(binary, float(deskew_cfg.get("max_angle_degrees", 15)))

    target_height = int(cfg["target_height_px"])
    height, width = binary.shape[:2]
    if height <= 0 or width <= 0:
        raise PreprocessingError("image has zero width or height")

    scale = target_height / float(height)
    new_width = max(1, int(round(width * scale)))
    max_width = int(cfg["max_output_width_px"])
    if new_width > max_width:
        policy = cfg.get("on_overflow", "error")
        if policy != "error":
            raise PreprocessingError(f"unsupported preprocessing.on_overflow policy: {policy}")
        raise PreprocessingError(f"line width {new_width} exceeds configured maximum {max_width}")

    interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    resized = cv2.resize(binary, (new_width, target_height), interpolation=interpolation)

    norm_min, norm_max = (float(value) for value in cfg["normalization_range"])
    normalized = (resized.astype(np.float32) / 255.0) * (norm_max - norm_min) + norm_min
    tensor = torch.from_numpy(normalized).unsqueeze(0).contiguous()
    return PreprocessedSample(
        tensor=tensor,
        input_length=new_width,
        width=new_width,
        height=target_height,
        pad_value=norm_min,
        warnings=tuple(warnings),
    )


def collate_preprocessed(samples: list[PreprocessedSample]) -> tuple[torch.Tensor, torch.Tensor]:
    """Pad a list of samples to the batch maximum and return true lengths."""
    if not samples:
        raise PreprocessingError("cannot collate an empty sample list")
    height = samples[0].height
    pad_value = samples[0].pad_value
    max_width = max(sample.input_length for sample in samples)
    batch = torch.full((len(samples), 1, height, max_width), pad_value, dtype=torch.float32)
    for index, sample in enumerate(samples):
        if sample.height != height:
            raise PreprocessingError("all samples in a batch must have the same height")
        batch[index, :, :, : sample.input_length] = sample.tensor
    lengths = torch.tensor([sample.input_length for sample in samples], dtype=torch.long)
    return batch, lengths
