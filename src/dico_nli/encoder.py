"""Encoder fine-tuned sulle quattro etichette (richiede `uv run --group ml`).

Stessa procedura di analisi/dico_nli_esperimento.py di settembre: coppia (text1, text2) come input,
cross-entropia, AdamW, warmup lineare 10%, bf16, max 64 token. Restituisce le log-probabilita' per
istanza, da passare a `decoding.decode`.
"""
from __future__ import annotations

import math
import random

from .labels import LABELS


def train_and_predict(train: list[dict], evals: list[dict], seed: int, *, model_name: str,
                      epochs: int = 5, lr: float = 3e-5, batch: int = 32, max_length: int = 64,
                      local_only: bool = True) -> dict[str, list[float]]:
    import torch
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        get_linear_schedule_with_warmup,
    )

    random.seed(seed)
    torch.manual_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(model_name, local_files_only=local_only)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=len(LABELS), local_files_only=local_only).to(device)
    lab = {l: i for i, l in enumerate(LABELS)}

    def batches(rows, shuffle):
        order = list(range(len(rows)))
        if shuffle:
            random.shuffle(order)
        for i in range(0, len(order), batch):
            chunk = [rows[j] for j in order[i:i + batch]]
            enc = tok([r["text1"] for r in chunk], [r["text2"] for r in chunk], padding=True,
                      truncation=True, max_length=max_length, return_tensors="pt").to(device)
            yield chunk, enc

    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    steps = epochs * math.ceil(len(train) / batch)
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    model.train()
    for _ in range(epochs):
        for chunk, enc in batches(train, shuffle=True):
            y = torch.tensor([lab[r["label"]] for r in chunk], device=device)
            with torch.autocast(device, dtype=torch.bfloat16):
                loss = torch.nn.functional.cross_entropy(model(**enc).logits.float(), y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            opt.zero_grad()

    model.eval()
    out: dict[str, list[float]] = {}
    with torch.no_grad():
        for chunk, enc in batches(evals, shuffle=False):
            with torch.autocast(device, dtype=torch.bfloat16):
                lp = torch.log_softmax(model(**enc).logits.float(), dim=-1).cpu().tolist()
            out.update({r["instance_id"]: v for r, v in zip(chunk, lp, strict=True)})
    del model
    if device == "cuda":
        torch.cuda.empty_cache()
    return out
