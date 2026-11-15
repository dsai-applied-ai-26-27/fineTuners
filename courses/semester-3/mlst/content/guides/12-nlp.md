---
title: 'NLP: embeddings, seq2seq and attention'
number: 12
topics: [nlp]
summary: 'Character-level datasets, embeddings for sentiment analysis, stateful RNNs, the encoder-decoder handoff, bidirectional layers and attention.'
---

Part 12 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## Character tokenising and windowed datasets

```python
tokenizer = keras.preprocessing.text.Tokenizer(char_level=True)
tokenizer.fit_on_texts(shakespeare_text)
max_id = len(tokenizer.word_index)          # number of distinct characters

dataset = tf.data.Dataset.from_tensor_slices(encoded)
dataset = dataset.window(n_steps + 1, shift=1, drop_remainder=True)
dataset = dataset.flat_map(lambda w: w.batch(n_steps + 1))
dataset = dataset.shuffle(10000).batch(batch_size)
dataset = dataset.map(lambda X, Y: (tf.one_hot(X, depth=max_id), Y))
dataset = dataset.prefetch(1)
```

| Argument | Kind | What it does |
|---|---|---|
| `char_level=True` | structural | Character-level tokenising. Leave it out for word-level. |
| `shift=1, drop_remainder=True` | structural | Windows overlap by all but one step; incomplete final windows are discarded so every batch has the same shape. |

## Embeddings and sentiment analysis

```python
embed_size = 128
model = keras.models.Sequential([
    keras.layers.Embedding(vocab_size, embed_size,
                           mask_zero=True, input_shape=[None]),
    keras.layers.GRU(128, return_sequences=True),
    keras.layers.GRU(128),
    keras.layers.Dense(1, activation="sigmoid")
])
model.compile(loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"])
history = model.fit(train_set, epochs=5)
```

| Argument | Kind | What it does |
|---|---|---|
| `Embedding(vocab_size, embed_size)` | structural | Rows = vocabulary size, columns = dimensions of the learned vector. Replaces one-hot with something dense and trainable. |
| `mask_zero=True` | structural | Token 0 is padding; tell the downstream layers to ignore it. |
| `second GRU has NO return_sequences` | structural | Deliberate: the last recurrent layer collapses the sequence into ONE vector, which the Dense(1, sigmoid) turns into a single sentiment probability. |
| `Dense(1, activation="sigmoid")` | structural | Binary output ⇒ 1 unit + sigmoid + binary_crossentropy. Multi-class ⇒ n units + softmax + (sparse_)categorical_crossentropy. |

## Stateful RNNs

```python
model = keras.models.Sequential([
    keras.layers.GRU(128, return_sequences=True, stateful=True, dropout=0.2,
                     batch_input_shape=[batch_size, None, max_id]),
    keras.layers.GRU(128, return_sequences=True, stateful=True, dropout=0.2),
    keras.layers.TimeDistributed(keras.layers.Dense(max_id, activation="softmax"))
])

class ResetStatesCallback(keras.callbacks.Callback):
    def on_epoch_begin(self, epoch, logs):
        self.model.reset_states()

model.compile(loss="sparse_categorical_crossentropy", optimizer="adam")
history = model.fit(dataset, epochs=50, callbacks=[ResetStatesCallback()])
```

| Argument | Kind | What it does |
|---|---|---|
| `stateful=True` | structural | Carry the hidden state from one batch to the next, so the model can learn patterns longer than one window. |
| `batch_input_shape=[batch_size, None, max_id]` | structural | Stateful layers need a FIXED batch size, so input_shape is not enough — the full batch shape must be declared. |
| `callbacks=[ResetStatesCallback()]` | structural | Without a reset at each epoch the state leaks across epochs and the model sees a false continuation. |
| `loss="sparse_categorical_crossentropy"` | structural | Multi-class targets given as integer IDs. Use "categorical_crossentropy" if the targets are one-hot. |

## Encoder-decoder

A **sequence-to-sequence** model. The lab's full version uses `tfa.seq2seq.BasicDecoder` with a `TrainingSampler` and an `LSTMCell(512)`, but the examinable idea is the state handoff above.

```python
import numpy as np
from tensorflow import keras

encoder_inputs = keras.layers.Input(shape=[None], dtype=np.int32)
decoder_inputs = keras.layers.Input(shape=[None], dtype=np.int32)

embeddings = keras.layers.Embedding(vocab_size, embed_size)
encoder_embeddings = embeddings(encoder_inputs)
decoder_embeddings = embeddings(decoder_inputs)

# ENCODER: returns its final states
encoder = keras.layers.LSTM(128, return_state=True)
encoder_outputs, state_h, state_c = encoder(encoder_embeddings)
encoder_state = [state_h, state_c]

# DECODER: initialised WITH those states
decoder_lstm = keras.layers.LSTM(128, return_sequences=True)
decoder_outputs = decoder_lstm(decoder_embeddings,
                               initial_state=encoder_state)

Y_proba = keras.layers.Dense(vocab_size, activation="softmax")(decoder_outputs)

model = keras.models.Model(inputs=[encoder_inputs, decoder_inputs],
                           outputs=[Y_proba])
```

| Argument | Kind | What it does |
|---|---|---|
| `return_state=True` | structural | Returns (output, state_h, state_c) for an LSTM — THREE values. A GRU returns two, because it has a single state. Not the same thing as return_sequences. |
| `initial_state=encoder_state` | structural | The handoff. This single argument is what makes it an encoder–decoder rather than two unrelated LSTMs. |
| `keras.models.Model(inputs=[...], outputs=[...])` | structural | The Functional API: needed whenever the graph is not a straight line — multiple inputs, shared layers, skip connections. |
| `Dense(vocab_size, activation="softmax")` | structural | One output unit per possible word; softmax makes it a distribution over the vocabulary. |

## Bidirectional layers

**Bidirectional** runs two copies of the layer, forwards and backwards, and concatenates their outputs — so the output width doubles. Fine for an **encoder**, impossible for a **decoder**, which generates left to right and must not see the future.

```python
model = keras.models.Sequential([
    keras.layers.GRU(10, return_sequences=True, input_shape=[None, 10]),
    keras.layers.Bidirectional(keras.layers.GRU(10, return_sequences=True))
])
```

## Attention and positional encoding

Attention lets every output position look directly at every encoder output, removing the bottleneck of a single fixed-size state. Because attention is **order-blind**, a **PositionalEncoding** layer adds sin/cos signals of different frequencies to the embeddings so position is recoverable. `MultiHeadAttention` runs several attention heads in parallel over projections of the input (implemented in the lab with `Conv1D(kernel_size=1, use_bias=False)` as the linear projections).

```python
# self-attention in the encoder
Z = encoder_in
for N in range(6):
    Z = keras.layers.Attention(use_scale=True)([Z, Z])
encoder_outputs = Z

# decoder: masked self-attention, then cross-attention to the encoder
Z = decoder_in
for N in range(6):
    Z = keras.layers.Attention(use_scale=True, causal=True)([Z, Z])
    Z = keras.layers.Attention(use_scale=True)([Z, encoder_outputs])

outputs = keras.layers.TimeDistributed(
    keras.layers.Dense(vocab_size, activation="softmax"))(Z)
```

| Argument | Kind | What it does |
|---|---|---|
| `Attention()([Q, V])` | structural | Called on a LIST. [Z, Z] is self-attention; [Z, encoder_outputs] is cross-attention from decoder to encoder. |
| `use_scale=True` | dial | Learn a scaling factor for the similarity scores. |
| `causal=True` | structural | Masks future positions. Decoder self-attention only — the same 'no peeking' rule as causal padding in WaveNet. |

## Remember it

The same sections as scenes along a route: [](palace:12-roof-terrace). The code is drilled in [the decks](cards).
