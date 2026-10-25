#加载官方预训练模型，输入观测，连续输出动作
"""Run the official, unmodified rt1main SavedModel on CPU.

--smoke uses synthetic images and zero language embeddings for interface tests.
For a supplied image use --embedding-npy, or --instruction with --encoder.
No robot/environment is connected. Outputs are predictions, not success scores.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import time

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "4")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "2")
os.environ.setdefault("TFHUB_CACHE_DIR", str(ROOT / "models" / "tfhub"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=ROOT / "robotics_transformer/trained_checkpoints/rt1main")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--image", type=Path)
    parser.add_argument("--embedding-npy", type=Path)
    parser.add_argument("--instruction")
    parser.add_argument("--encoder", help="Local USE SavedModel directory or explicit TF Hub handle")
    parser.add_argument("--steps", type=int, default=7, help="7 steps also exercises the six-frame history window")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/inference.json")
    args = parser.parse_args()
    if args.steps < 1:
        parser.error("--steps must be positive")
    if args.smoke:
        if any((args.image, args.embedding_npy, args.instruction, args.encoder)):
            parser.error("--smoke cannot be combined with supplied image/language inputs")
    elif not args.image or not (bool(args.embedding_npy) ^ bool(args.encoder and args.instruction)):
        parser.error("Supply --smoke OR --image and exactly one language input: --embedding-npy / --instruction + --encoder")

    import numpy as np
    from PIL import Image
    import tensorflow as tf
    from tf_agents.policies import py_tf_eager_policy
    from tf_agents.trajectories import time_step as ts

    tf.random.set_seed(0)
    if args.smoke:
        embedding = np.zeros(512, dtype=np.float32)
        language_source = "synthetic zero vector; no sentence was encoded"
    elif args.embedding_npy:
        embedding = np.asarray(np.load(args.embedding_npy, allow_pickle=False), dtype=np.float32)
        language_source = str(args.embedding_npy.resolve())
    else:
        import tensorflow_hub as hub
        print(f"Loading language encoder: {args.encoder}", flush=True)
        encoder = hub.load(args.encoder)
        embedding = np.asarray(encoder([args.instruction])[0], dtype=np.float32)
        language_source = args.encoder
    if embedding.shape != (512,) or not np.isfinite(embedding).all():
        raise ValueError("Language embedding must be a finite float32 array with shape (512,)")

    print(f"Loading official policy: {args.model}", flush=True)
    started = time.perf_counter()
    policy = py_tf_eager_policy.SavedModelPyTFEagerPolicy(
        str(args.model), load_specs_from_pbtxt=True, use_tf_function=True)#模型加载
    load_seconds = time.perf_counter() - started
    obs_spec = policy.time_step_spec.observation
    image_shape = tuple(obs_spec["image"].shape)
    if args.image:
        with Image.open(args.image) as input_image:
            frame = np.asarray(input_image.convert("RGB").resize(
                (image_shape[1], image_shape[0]), Image.Resampling.BILINEAR))

    def zeros(spec):
        dtype = getattr(spec.dtype, "as_numpy_dtype", spec.dtype)
        if np.dtype(dtype).kind in "OSU":
            return np.full(spec.shape, b"", dtype=object)
        return np.zeros(spec.shape, dtype=dtype)

    state = policy.get_initial_state(batch_size=1)
    initial_state_shapes = {key: list(value.shape) for key, value in state.items()}
    steps = []
    for index in range(args.steps):
        obs = tf.nest.map_structure(zeros, obs_spec)
        if args.smoke:
            frame = np.random.default_rng(index).integers(0, 256, image_shape, dtype=np.uint8)
        obs["image"] = frame
        obs["natural_language_embedding"] = embedding
        if "natural_language_instruction" in obs:
            obs["natural_language_instruction"] = np.asarray((args.instruction or "").encode(), dtype=object)
        step = ts.restart(obs) if index == 0 else ts.transition(obs, reward=np.float32(0))
        started = time.perf_counter()
        result = policy.action(step, state)#调用模型结果 = 模型.预测动作(当前这一步的信息, 历史状态)
        actions = {key: np.asarray(value) for key, value in result.action.items()}
        elapsed = time.perf_counter() - started
        if actions.keys() != policy.action_spec.keys():
            raise AssertionError("Action fields do not match official specification")
        for key, value in actions.items():
            expected = policy.action_spec[key]
            dtype = np.dtype(getattr(expected.dtype, "as_numpy_dtype", expected.dtype))
            if value.shape != tuple(expected.shape) or value.dtype != dtype or not np.isfinite(value).all():
                raise AssertionError(f"Invalid action tensor: {key}")
            if hasattr(expected, "minimum") and (np.any(value < expected.minimum) or np.any(value > expected.maximum)):
                raise AssertionError(f"Out-of-range action: {key}")
        state = result.state  # Preserve the history returned by the trained policy.
        state_values = {key: np.asarray(value) for key, value in state.items()}
        if any(not np.isfinite(value).all() for value in state_values.values()):
            raise AssertionError("Non-finite policy state")
        counters = {key: value.reshape(-1).tolist() for key, value in state_values.items() if key in ("t", "step_num", "seq_idx")}
        record = {"step": index, "seconds": round(elapsed, 4),
                  "action": {key: value.tolist() for key, value in actions.items()},
                  "state_counters": counters,
                  "image_sha256": hashlib.sha256(frame.tobytes()).hexdigest()}
        steps.append(record)
        print(json.dumps(record), flush=True)

    report = {
        "mode": "synthetic_smoke" if args.smoke else "supplied_image_and_language",
        "scope": "SavedModel inference; no robot execution or task-success evaluation",
        "model": str(args.model.resolve()), "python": platform.python_version(),
        "tensorflow": tf.__version__, "devices": [device.name for device in tf.config.list_physical_devices()],
        "language_source": language_source, "instruction": args.instruction,
        "auxiliary_observations": "zero-filled; input is an interface demonstration",
        "image_source": "synthetic random RGB" if args.smoke else str(args.image.resolve()),
        "load_seconds": round(load_seconds, 3), "initial_state_shapes": initial_state_shapes,
        "steps": steps,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"PASS: {len(steps)} inference steps; report: {args.output}", flush=True)


if __name__ == "__main__":
    main()
