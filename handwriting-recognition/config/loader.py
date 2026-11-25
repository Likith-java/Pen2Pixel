"""Configuration loading, environment overrides and validation for Pen2Pixel.

The configuration file is the single source of truth for paths, limits, seeds and
hyperparameters. No machine-specific absolute path is stored in it.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "default.yaml"
CONFIG_PATH_ENV = "PEN2PIXEL_CONFIG"
ENV_PREFIX = "PEN2PIXEL__"

REQUIRED_SECTIONS = (
    "version",
    "random",
    "device",
    "paths",
    "logging",
    "api",
    "upload",
    "image",
    "preprocessing",
    "training",
    "model",
    "dataset",
)
VALID_DEVICES = frozenset({"auto", "cpu", "cuda"})
VALID_LOG_LEVELS = frozenset({"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"})
SCALAR_SECTIONS = frozenset({"version", "device"})


class ConfigError(ValueError):
    """Raised when configuration is missing, malformed or invalid."""


def load_config(
    config_path: str | Path | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Load YAML configuration, apply overrides, then validate.

    Args:
        config_path: Optional path to a YAML file. Relative paths are resolved
            against the repository root. Defaults to ``configs/default.yaml`` or
            the path in the ``PEN2PIXEL_CONFIG`` environment variable.
        overrides: Optional explicit mapping merged on top of the file contents.

    Returns:
        A validated configuration dictionary.

    Raises:
        ConfigError: If the file cannot be read, parsed or validated.
    """
    path = Path(config_path) if config_path is not None else Path(os.environ.get(CONFIG_PATH_ENV, str(DEFAULT_CONFIG_PATH)))
    if not path.is_absolute():
        path = REPO_ROOT / path
    if not path.is_file():
        raise ConfigError(f"Configuration file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as stream:
            data = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"Could not read configuration file {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Configuration root must be a mapping")

    merged = _deep_merge(data, dict(overrides or {}))
    merged = _apply_env_overrides(merged)
    validate_config(merged)
    return merged


def get_path(config: Mapping[str, Any], dotted_key: str) -> Path:
    """Resolve a configured path relative to the repository root.

    Args:
        config: A validated configuration mapping.
        dotted_key: Dot-separated key, e.g. ``paths.model_dir``.

    Returns:
        An absolute path. Already-absolute values are returned unchanged.

    Raises:
        ConfigError: If the key is missing or its value is not a path string.
    """
    node: Any = config
    for part in dotted_key.split("."):
        if not isinstance(node, Mapping) or part not in node:
            raise ConfigError(f"Missing configuration key: {dotted_key}")
        node = node[part]
    if node is None or not isinstance(node, str) or not node.strip():
        raise ConfigError(f"Configuration key {dotted_key} must be a non-empty path string")
    path = Path(node)
    return path if path.is_absolute() else REPO_ROOT / path


def validate_config(config: Mapping[str, Any]) -> None:
    """Validate the configuration structure and value ranges.

    Raises:
        ConfigError: With a message describing the first invalid value found.
    """
    for section in REQUIRED_SECTIONS:
        if section not in config:
            raise ConfigError(f"Missing configuration section: {section}")
        if section not in SCALAR_SECTIONS and not isinstance(config[section], Mapping):
            raise ConfigError(f"Configuration section {section!r} must be a mapping")

    seed = config["random"].get("seed")
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ConfigError("random.seed must be a non-negative integer")

    device = config.get("device")
    if device not in VALID_DEVICES:
        raise ConfigError(f"device must be one of {sorted(VALID_DEVICES)}, got {device!r}")

    for key, value in config["paths"].items():
        if value is not None and not isinstance(value, str):
            raise ConfigError(f"paths.{key} must be a string or null")

    level = config["logging"].get("level")
    if not isinstance(level, str) or level.upper() not in VALID_LOG_LEVELS:
        raise ConfigError(f"logging.level must be a valid log level, got {level!r}")

    max_bytes = config["upload"].get("max_bytes")
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0:
        raise ConfigError("upload.max_bytes must be a positive integer")
    mime_types = config["upload"].get("allowed_mime_types")
    if not isinstance(mime_types, list) or not all(isinstance(item, str) for item in mime_types):
        raise ConfigError("upload.allowed_mime_types must be a list of strings")

    for lower, upper in (("min_width_px", "max_width_px"), ("min_height_px", "max_height_px")):
        low = config["image"].get(lower)
        high = config["image"].get(upper)
        if not isinstance(low, int) or not isinstance(high, int) or low <= 0 or high < low:
            raise ConfigError(f"image.{lower}/image.{upper} must be positive with {lower} <= {upper}")

    target_height = config["preprocessing"].get("target_height_px")
    if not isinstance(target_height, int) or target_height <= 0:
        raise ConfigError("preprocessing.target_height_px must be a positive integer")
    norm_range = config["preprocessing"].get("normalization_range")
    if (
        not isinstance(norm_range, list)
        or len(norm_range) != 2
        or not all(isinstance(v, (int, float)) for v in norm_range)
        or norm_range[0] >= norm_range[1]
    ):
        raise ConfigError("preprocessing.normalization_range must be [min, max] with min < max")

    training = config["training"]
    if not isinstance(training.get("batch_size"), int) or isinstance(training.get("batch_size"), bool) or training["batch_size"] <= 0:
        raise ConfigError("training.batch_size must be a positive integer")
    lr = training.get("learning_rate")
    if not isinstance(lr, (int, float)) or isinstance(lr, bool) or lr <= 0:
        raise ConfigError("training.learning_rate must be a positive number")
    if not isinstance(training.get("epochs"), int) or training["epochs"] <= 0:
        raise ConfigError("training.epochs must be a positive integer")

    model_cfg = config["model"]
    vocab = model_cfg.get("vocab")
    if (
        not isinstance(vocab, list)
        or not vocab
        or not all(isinstance(char, str) and len(char) == 1 for char in vocab)
        or len(set(vocab)) != len(vocab)
    ):
        raise ConfigError("model.vocab must be a non-empty list of unique single-character strings")
    blank_token = model_cfg.get("blank_token")
    if not isinstance(blank_token, str) or len(blank_token) != 1 or blank_token in vocab:
        raise ConfigError("model.blank_token must be a single character not present in model.vocab")
    channels = model_cfg.get("cnn_channels")
    if not isinstance(channels, list) or not channels or not all(isinstance(c, int) and c > 0 for c in channels):
        raise ConfigError("model.cnn_channels must be a non-empty list of positive integers")
    hidden = model_cfg.get("lstm_hidden_size")
    if not isinstance(hidden, int) or hidden <= 0:
        raise ConfigError("model.lstm_hidden_size must be a positive integer")


def _deep_merge(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge ``extra`` into ``base`` without mutating the inputs."""
    result = dict(base)
    for key, value in extra.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _deep_merge(dict(result[key]), dict(value))
        else:
            result[key] = value
    return result


def _apply_env_overrides(config: dict[str, Any]) -> dict[str, Any]:
    """Apply ``PEN2PIXEL__SECTION__KEY`` environment variables to the config.

    Values are parsed with ``yaml.safe_load`` so integers, booleans, nulls and
    lists are converted to the corresponding Python types.
    """
    for name, raw_value in os.environ.items():
        if not name.startswith(ENV_PREFIX):
            continue
        parts = [part.lower() for part in name[len(ENV_PREFIX) :].split("__") if part]
        if not parts:
            continue
        try:
            value = yaml.safe_load(raw_value)
        except yaml.YAMLError as exc:
            raise ConfigError(f"Environment variable {name} is not valid YAML: {exc}") from exc

        node = config
        for part in parts[:-1]:
            child = node.get(part)
            if not isinstance(child, dict):
                raise ConfigError(f"Environment variable {name} targets a missing section: {part}")
            node = child
        node[parts[-1]] = value
    return config
