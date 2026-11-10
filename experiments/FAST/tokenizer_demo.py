"""Re-run the FAST reading-session numeric example; no policy/model training.

Requires NumPy. This is an orthonormal DCT-II and integer-symbol BPE teaching
implementation, not the official FAST+ processor or a paper reproduction.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import platform

import numpy as np


def merge(sequence, pair):
    result, index = [], 0
    while index < len(sequence):
        if index + 1 < len(sequence) and (sequence[index], sequence[index + 1]) == pair:
            result.append(sequence[index] + sequence[index + 1])
            index += 2
        else:
            result.append(sequence[index])
            index += 1
    return result


def run_demo():
    horizon = 8
    time = np.arange(horizon)
    frequency = np.arange(horizon)[:, None]
    basis = np.sqrt(2.0 / horizon) * np.cos(np.pi * (time + 0.5) * frequency / horizon)
    basis[0] /= np.sqrt(2.0)
    chosen_coefficients = np.array([0.8, -0.6, 0.12, 0.0, 0.06, 0.0, 0.0, 0.0])
    actions = basis.T @ chosen_coefficients
    coefficients = basis @ actions
    roundtrip_error = float(np.max(np.abs(basis.T @ coefficients - actions)))
    assert np.allclose(basis @ basis.T, np.eye(horizon), atol=1e-12)
    assert roundtrip_error < 1e-12
    quantization = []
    for scale in (2, 10, 100):
        integers = np.rint(scale * coefficients).astype(int)
        reconstructed = basis.T @ (integers / scale)
        quantization.append({
            "scale": scale,
            "integer_coefficients": integers.tolist(),
            "zero_count": int(np.sum(integers == 0)),
            "reconstructed_actions": reconstructed.tolist(),
            "mse": float(np.mean((actions - reconstructed) ** 2)),
            "max_abs_error": float(np.max(np.abs(actions - reconstructed))),
        })

    # Sixteen deliberately related integer sequences; the example is in this
    # corpus. These are neither independent robot demonstrations nor held-out data.
    corpus = [[(dc,), (-amplitude,), (1,), (0,), (1,), (0,), (0,), (0,)]
              for dc in range(7, 11) for amplitude in range(4, 8)]
    rules = []
    for _ in range(4):
        counts = Counter(pair for seq in corpus for pair in zip(seq, seq[1:]))
        pair = counts.most_common(1)[0][0]
        rules.append(pair)
        corpus = [merge(seq, pair) for seq in corpus]

    target = quantization[1]["integer_coefficients"]
    encoded = [(value,) for value in target]
    token_counts = [len(encoded)]
    for rule in rules:
        encoded = merge(encoded, rule)
        token_counts.append(len(encoded))
    decoded = [value for token in encoded for value in token]
    assert decoded == target
    assert token_counts == [8, 6, 5, 4, 3]
    reconstructed = basis.T @ (np.array(decoded) / 10)
    post_bpe_mse = float(np.mean((actions - reconstructed) ** 2))
    assert np.isclose(post_bpe_mse, quantization[1]["mse"], atol=1e-15)
    assert np.allclose([row["mse"] for row in quantization], [0.0085, 0.00025, 0.0], atol=1e-12)
    return {
        "record_date": "2026-11-10",
        "run_type": "assistant_executed_synthetic_encoding_demo",
        "scope": "DCT, quantization, integer-symbol BPE, reconstruction only",
        "limitations": [
            "No official FAST+ processor or weights loaded",
            "No VLA/Transformer training, inference or robot evaluation",
            "BPE trained on 16 constructed sequences; example included in training corpus",
            "No claim about generalization, latency, compression on real data or learning benefit",
            "Single dimension, no normalization fitting, no multidimensional flattening",
            "Scale 100 is exact only because the chosen coefficients lie on that quantization grid",
        ],
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "dct_convention": "orthonormal DCT-II, computed explicitly as an 8x8 matrix",
        "original_actions": actions.tolist(),
        "chosen_coefficients": chosen_coefficients.tolist(),
        "dct_coefficients": coefficients.tolist(),
        "dct_roundtrip_max_error": roundtrip_error,
        "quantization": quantization,
        "bpe": {
            "training_sequence_count": 16,
            "rules": [{"left": list(left), "right": list(right), "merged": list(left + right)}
                      for left, right in rules],
            "token_counts_after_merges": token_counts,
            "encoded_token_expansions": [list(token) for token in encoded],
            "decoded_coefficients": decoded,
            "exact_integer_roundtrip": decoded == target,
            "post_bpe_action_mse": post_bpe_mse,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optionally save the numeric record as JSON")
    args = parser.parse_args()
    result = run_demo()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Synthetic encoding checks passed; no model training or robot evaluation.")
    for row in result["quantization"]:
        print(f"scale={row['scale']}; zeros={row['zero_count']}; MSE={row['mse']:.8g}")
    print("BPE token counts:", result["bpe"]["token_counts_after_merges"])
    print("BPE integer reconstruction is exact.")


if __name__ == "__main__":
    main()
