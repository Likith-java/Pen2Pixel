"""Milestone 2 environment smoke tests.

These tests verify the foundation only: imports, CPU PyTorch, image decoding,
configuration, logging and validation. They require no network, GPU, dataset or
trained checkpoint.
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np
import pytest
import torch
from PIL import Image

from config import ConfigError, get_path, load_config
from utils import configure_logging


def test_package_imports() -> None:
    """All foundation packages are importable."""
    import api  # noqa: F401
    import backend  # noqa: F401
    import config  # noqa: F401
    import dataset  # noqa: F401
    import models  # noqa: F401
    import preprocessing  # noqa: F401
    import utils  # noqa: F401


def test_torch_cpu_tensor_operations() -> None:
    """PyTorch is installed and performs CPU tensor arithmetic."""
    device = torch.device("cpu")
    left = torch.tensor([1.0, 2.0, 3.0], device=device)
    right = torch.tensor([4.0, 5.0, 6.0], device=device)
    result = left + right
    assert result.device.type == "cpu"
    assert torch.allclose(result, torch.tensor([5.0, 7.0, 9.0]))


def test_image_loading_with_pillow_and_opencv(tmp_path: Path) -> None:
    """A generated PNG can be written by Pillow and decoded by OpenCV."""
    image_path = tmp_path / "line.png"
    array = np.zeros((24, 96, 3), dtype=np.uint8)
    array[:, :] = 255
    Image.fromarray(array).save(image_path)

    with Image.open(image_path) as loaded:
        assert loaded.size == (96, 24)

    decoded = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    assert decoded is not None
    assert decoded.shape == (24, 96)


def test_configuration_loads_defaults() -> None:
    """The default config is loadable, validated and path-aware."""
    cfg = load_config()
    assert cfg["version"] == 1
    assert cfg["random"]["seed"] == 42
    assert cfg["device"] in {"auto", "cpu", "cuda"}
    assert get_path(cfg, "paths.mnist_dir").name == "mnist"
    assert get_path(cfg, "paths.upload_dir").name == "uploads"


def test_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Nested environment variables override configuration values."""
    monkeypatch.setenv("PEN2PIXEL__TRAINING__BATCH_SIZE", "16")
    monkeypatch.setenv("PEN2PIXEL__LOGGING__LEVEL", "DEBUG")
    cfg = load_config()
    assert cfg["training"]["batch_size"] == 16
    assert cfg["logging"]["level"] == "DEBUG"


def test_invalid_config_is_rejected() -> None:
    """Invalid values are rejected with a typed configuration error."""
    with pytest.raises(ConfigError, match="training.batch_size"):
        load_config(overrides={"training": {"batch_size": -1}})


def test_logging_initialization() -> None:
    """Logging initializes from config and is idempotent."""
    cfg = load_config()
    logger = configure_logging(cfg)
    assert logger.name == "pen2pixel"
    assert logger.level == logging.INFO
    assert logger.handlers
    first_handler_count = len(logger.handlers)
    again = configure_logging(cfg)
    assert len(again.handlers) == first_handler_count
