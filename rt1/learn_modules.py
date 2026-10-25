"""Small, runnable RT-1 source-code lessons; these are NOT trained RT-1 inference.

Run with --stage action / film / tokens / transformer / all.
Randomly initialized modules demonstrate operations and tensor shapes only.
"""
import argparse
import os

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_NUM_INTRAOP_THREADS", "4")
os.environ.setdefault("TF_NUM_INTEROP_THREADS", "2")


def action_lesson(tf):
    from robotics_transformer.tokenizers.action_tokenizer import RT1ActionTokenizer
    from robotics_transformer.tensorspec_compat import TensorSpecStruct
    from tf_agents.specs import tensor_spec

    # Teaching range and vocabulary; not the real robot's units or bounds.
    specs = TensorSpecStruct(move=tensor_spec.BoundedTensorSpec(
        [1], tf.float32, minimum=-1.0, maximum=1.0))
    tokenizer = RT1ActionTokenizer(specs, vocab_size=5, action_order=["move"])
    values = tf.constant([[-2.0], [-1.0], [-0.5], [0.0], [0.3], [0.5], [1.0], [2.0]])
    tokens = tokenizer.tokenize(TensorSpecStruct(move=values))
    decoded = tokenizer.detokenize(tokens)["move"]
    print("\nACTION: teaching example with 5 bins in [-1, 1]")
    print("input -> token -> decoded")
    for before, token, after in zip(values.numpy().ravel(), tokens.numpy().ravel(), decoded.numpy().ravel()):
        print(f"{before:5.2f} -> {token} -> {after:5.2f}")
    print("Notice clipping at the limits and truncation, rather than nearest-bin rounding.")


def film_lesson(tf):
    from robotics_transformer.film_efficientnet.film_conditioning_layer import FilmConditioning

    features = tf.random.normal([1, 3, 3, 4])
    language = tf.random.normal([1, 512])
    layer = FilmConditioning(num_channels=4)
    output = layer(features, language)
    print("\nFILM: [batch, height, width, channels] + [batch, language_dim]")
    print("features:", features.shape, "language:", language.shape, "output:", output.shape)
    print("initial max |output - input|:", float(tf.reduce_max(tf.abs(output - features))))
    tf.debugging.assert_near(output, features)
    print("Zero-initialized projections give (1 + 0) * features + 0.")


def token_lesson(tf):
    from robotics_transformer.tokenizers.token_learner import TokenLearnerModule

    features = tf.random.normal([1, 81, 512])
    layer = TokenLearnerModule(num_tokens=8)
    tokens = layer(features, training=False)
    print("\nTOKEN LEARNER: weighted pooling over spatial positions")
    print("input:", features.shape, "output:", tokens.shape)
    print("81 spatial tokens become 8 tokens; each still has 512 features.")


def transformer_lesson(tf):
    from robotics_transformer.transformer import Transformer

    # Small teaching config, not the paper's config or the trained SavedModel.
    count = 12
    inputs = tf.random.normal([1, count, 512])
    mask = tf.linalg.band_part(tf.ones([count, count]), -1, 0)
    model = Transformer(num_layers=2, layer_size=32, num_heads=4,
                        feed_forward_size=512, vocab_size=256,
                        return_attention_scores=True)
    logits, scores = model(inputs, training=False, attention_mask=mask)
    print("\nTRANSFORMER: small randomly initialized source model")
    print("input:", inputs.shape, "logits:", logits.shape)
    print("attention scores per layer:", [tuple(score.shape) for score in scores])
    print("probability sums (first 3 positions):", tf.reduce_sum(tf.nn.softmax(logits), -1)[0, :3].numpy())
    print("argmax token IDs (not meaningful actions):", tf.argmax(logits, -1).numpy())
    modified = tf.concat([inputs[:, :9], tf.zeros_like(inputs[:, 9:])], axis=1)
    changed_logits, _ = model(modified, training=False, attention_mask=mask)
    delta = tf.reduce_max(tf.abs(logits[:, :9] - changed_logits[:, :9]))
    print("max change at first 9 positions after replacing future inputs:", float(delta))
    tf.debugging.assert_near(logits[:, :9], changed_logits[:, :9], atol=1e-5)
    print("This uses a plain causal mask; RT-1's full network adds action-specific masking.")


def main():
    lessons = {"action": action_lesson, "film": film_lesson,
               "tokens": token_lesson, "transformer": transformer_lesson}
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=[*lessons, "all"], default="all")
    args = parser.parse_args()
    import tensorflow as tf
    tf.random.set_seed(0)
    print("SOURCE LEARNING DEMO: no trained policy, no training, no robot execution.")
    for name, lesson in lessons.items():
        if args.stage in (name, "all"):
            lesson(tf)


if __name__ == "__main__":
    main()
