"""CNN + Bidirectional LSTM + CTC model for handwritten text-line recognition."""

from __future__ import annotations

from typing import Sequence

import torch
from torch import nn

from models.cnn_model import CNNFeatureExtractor


class CRNNCTC(nn.Module):
    """Device-agnostic CRNN producing log probabilities over vocab plus blank.

    The blank index is always the final class (``vocab_size``). Decoding must use
    the same index; see :mod:`models.decoding`.
    """

    def __init__(
        self,
        vocab_size: int,
        cnn_channels: Sequence[int] = (32, 64, 128),
        hidden_size: int = 256,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        if vocab_size <= 0:
            raise ValueError("vocab_size must be positive")
        self.cnn = CNNFeatureExtractor(channels=cnn_channels)
        self.lstm = nn.LSTM(
            input_size=self.cnn.out_channels,
            hidden_size=hidden_size,
            num_layers=1,
            bidirectional=True,
            batch_first=True,
        )
        self.dropout = nn.Dropout(dropout)
        self.projection = nn.Linear(hidden_size * 2, vocab_size + 1)
        self.blank_index = vocab_size

    @staticmethod
    def _sequence_lengths(input_lengths: torch.Tensor, max_length: int) -> torch.Tensor:
        lengths = (((input_lengths + 1) // 2) + 1) // 2
        return torch.clamp(lengths, min=1, max=max_length)

    def forward(
        self,
        images: torch.Tensor,
        input_lengths: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Return ``(log_probs, output_lengths)``.

        Args:
            images: Float tensor ``(batch, 1, height, width)``.
            input_lengths: Optional true widths ``(batch,)``; when supplied,
                padded columns are excluded from the BiLSTM via packing.

        Returns:
            Log probabilities ``(batch, time, vocab_size + 1)`` and the true
            output length for each batch item.
        """
        features = self.cnn(images).squeeze(2).permute(0, 2, 1)
        batch_size, max_time, _ = features.shape

        if input_lengths is None:
            recurrent, _ = self.lstm(features)
            output_lengths = torch.full((batch_size,), max_time, dtype=torch.long, device=features.device)
        else:
            lengths = self._sequence_lengths(input_lengths.to(device=features.device), max_time)
            packed = nn.utils.rnn.pack_padded_sequence(
                features, lengths.cpu(), batch_first=True, enforce_sorted=False
            )
            packed_out, _ = self.lstm(packed)
            recurrent, _ = nn.utils.rnn.pad_packed_sequence(
                packed_out, batch_first=True, total_length=max_time
            )
            output_lengths = lengths

        logits = self.projection(self.dropout(recurrent))
        return torch.log_softmax(logits, dim=-1), output_lengths
