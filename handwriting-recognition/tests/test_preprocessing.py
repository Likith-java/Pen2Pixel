"""Tests for the shared preprocessing pipeline."""

from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from config import load_config
from preprocessing.preprocess import PreprocessingError, collate_preprocessed, preprocess_image


def _png(width: int = 160, height: int = 40) -> bytes:
    array = np.full((height, width), 255, dtype=np.uint8)
    array[10:30, 20:140] = 0
    buffer = io.BytesIO()
    Image.fromarray(array, mode="L").save(buffer, format="PNG")
    return buffer.getvalue()


def test_preprocess_shape_range_and_determinism() -> None:
    cfg = load_config()
    target_height = cfg["preprocessing"]["target_height_px"]
    sample = preprocess_image(_png(), cfg)
    assert sample.tensor.dtype == torch_dtype()
    assert sample.tensor.shape[0] == 1
    assert sample.tensor.shape[1] == target_height
    assert sample.input_length == sample.width == sample.tensor.shape[2]
    assert sample.width <= cfg["preprocessing"]["max_output_width_px"]
    low, high = cfg["preprocessing"]["normalization_range"]
    assert float(sample.tensor.min()) >= low - 1e-6
    assert float(sample.tensor.max()) <= high + 1e-6
    again = preprocess_image(_png(), cfg)
    assert torch_equal(sample.tensor, again.tensor)


def torch_dtype():
    import torch

    return torch.float32


def torch_equal(left, right) -> bool:
    import torch

    return bool(torch.equal(left, right))


def test_collate_pads_and_preserves_lengths() -> None:
    cfg = load_config()
    first = preprocess_image(_png(width=80), cfg)
    second = preprocess_image(_png(width=160), cfg)
    batch, lengths = collate_preprocessed([first, second])
    assert batch.shape[0] == 2
    assert batch.shape[3] == max(first.width, second.width)
    assert lengths.tolist() == [first.width, second.width]


def test_width_overflow_is_reported_not_silently_cropped() -> None:
    cfg = load_config(overrides={"preprocessing": {"max_output_width_px": 10}})
    with pytest.raises(PreprocessingError, match="exceeds configured maximum"):
        preprocess_image(_png(width=400), cfg)
