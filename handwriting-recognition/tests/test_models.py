"""CPU-only tests for the CRNN-CTC architecture and greedy decoding."""

from __future__ import annotations

import torch

from config import load_config
from models.crnn_ctc_model import CRNNCTC
from models.decoding import greedy_decode, greedy_decode_batch
from preprocessing.preprocess import preprocess_image, collate_preprocessed

PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00\x08\x08\x02"
    b"\x00\x00\x00\x00\x00\x00\x00\x00IDATx\x9cc\xf8\xcf\xc0\xf0\x00\x00\x00\x05\x00\x01"
    b"\xff\xb3\x1a\xac\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _cfg():
    return load_config(overrides={"model": {"lstm_hidden_size": 32, "dropout": 0.0}})


def test_model_forward_is_device_aware_and_variable_width() -> None:
    cfg = _cfg()
    images = torch.zeros(2, 1, 8, 24, dtype=torch.float32)
    lengths = torch.tensor([9, 24], dtype=torch.long)
    model = CRNNCTC(
        vocab_size=len(cfg["model"]["vocab"]),
        cnn_channels=cfg["model"]["cnn_channels"],
        hidden_size=cfg["model"]["lstm_hidden_size"],
        dropout=0.0,
    ).to("cpu")
    model.eval()
    log_probs, output_lengths = model(images, lengths)
    assert log_probs.shape[0] == 2
    assert log_probs.shape[2] == len(cfg["model"]["vocab"]) + 1
    assert output_lengths.tolist() == [3, 6]
    assert torch.allclose(log_probs.exp().sum(dim=-1), torch.ones_like(log_probs[..., 0]), atol=1e-4)


def test_model_forward_without_lengths() -> None:
    cfg = _cfg()
    model = CRNNCTC(len(cfg["model"]["vocab"]), hidden_size=16, dropout=0.0).eval()
    log_probs, output_lengths = model(torch.zeros(1, 1, 8, 16))
    assert output_lengths.tolist() == [log_probs.shape[1]]


def test_greedy_decode_collapses_blanks_and_repeats() -> None:
    vocab = ["A", "B", "C"]
    blank = 3
    steps = [blank, 0, 0, blank, 1, 2, 2]
    logits = torch.full((len(steps), 4), -100.0)
    for time, index in enumerate(steps):
        logits[time, index] = 0.0
    assert greedy_decode(logits, vocab, blank) == "ABC"
    assert greedy_decode_batch(logits.unsqueeze(0), vocab, blank) == ["ABC"]


def test_pipeline_sample_feeds_model() -> None:
    import io

    from PIL import Image

    cfg = _cfg()
    image = Image.fromarray((torch.ones(8, 32) * 255).numpy().astype("uint8"), mode="L")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    sample = preprocess_image(buffer.getvalue(), cfg)
    batch, lengths = collate_preprocessed([sample])
    model = CRNNCTC(len(cfg["model"]["vocab"]), hidden_size=16, dropout=0.0).eval()
    log_probs, output_lengths = model(batch, lengths)
    assert log_probs.shape[0] == 1
    assert output_lengths.item() >= 1
