"""CTC decoding utilities (greedy best-path baseline)."""

from __future__ import annotations

import torch


def greedy_decode(log_probs: torch.Tensor, vocab: list[str], blank_index: int) -> str:
    """Decode one CTC output sequence with best-path decoding.

    Args:
        log_probs: Tensor of shape ``(time, vocab_size + 1)``.
        vocab: Character list; class indices ``0..len(vocab)-1`` map to it.
        blank_index: Index of the CTC blank class.

    Returns:
        The decoded text string.
    """
    if log_probs.dim() != 2:
        raise ValueError(f"expected (time, classes) tensor, got {tuple(log_probs.shape)}")
    if blank_index < 0 or blank_index >= log_probs.size(1):
        raise ValueError("blank_index outside class range")
    indices = log_probs.argmax(dim=-1).detach().cpu().tolist()
    characters: list[str] = []
    previous = blank_index
    for index in indices:
        if index == blank_index:
            previous = index
            continue
        if index != previous:
            if index >= len(vocab):
                raise ValueError(f"class index {index} outside vocabulary")
            characters.append(vocab[index])
        previous = index
    return "".join(characters)


def greedy_decode_batch(log_probs: torch.Tensor, vocab: list[str], blank_index: int) -> list[str]:
    """Decode a batch of shape ``(batch, time, classes)``."""
    if log_probs.dim() != 3:
        raise ValueError(f"expected (batch, time, classes) tensor, got {tuple(log_probs.shape)}")
    return [greedy_decode(item, vocab, blank_index) for item in log_probs]
