"""Convolutional feature extractor for the CRNN-CTC baseline."""

from __future__ import annotations

from typing import Sequence

import torch
from torch import nn


class CNNFeatureExtractor(nn.Module):
    """Extract a vertical-collapsed feature sequence from a line image.

    Input:  ``(batch, 1, height, width)``
    Output: ``(batch, channels[-1], 1, ceil(width / 4))``

    Height is collapsed with adaptive pooling so any configured target height
    works, while width is only reduced by strided pooling (never distorted).
    """

    def __init__(self, channels: Sequence[int], in_channels: int = 1) -> None:
        super().__init__()
        if not channels:
            raise ValueError("channels must be non-empty")
        layers: list[nn.Module] = []
        previous = in_channels
        for index, out_channels in enumerate(channels):
            layers.extend(
                [
                    nn.Conv2d(previous, out_channels, kernel_size=3, padding=1, bias=False),
                    nn.BatchNorm2d(out_channels),
                    nn.ReLU(inplace=True),
                ]
            )
            if index < 2:
                layers.append(nn.MaxPool2d(kernel_size=2, stride=2, ceil_mode=True))
            previous = out_channels
        layers.append(nn.AdaptiveAvgPool2d((1, None)))
        self.network = nn.Sequential(*layers)
        self.out_channels = int(channels[-1])

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        """Return features of shape ``(batch, channels, 1, width')``."""
        if images.dim() != 4:
            raise ValueError(f"expected (B, C, H, W) tensor, got shape {tuple(images.shape)}")
        return self.network(images)
