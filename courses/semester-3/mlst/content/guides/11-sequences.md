---
title: 'Sequences: RNNs and 1D CNNs'
number: 11
topics: [sequences]
summary: 'Deep RNNs in Keras, normalisation between recurrent layers, LSTM and GRU, Conv1D in front of an RNN, WaveNet, and a metric on the last time step.'
---

Part 11 of 12 of the course notes, from the 2025-26 exam kit (lectures 1 to 7, labs 1 to 10). Each section pairs an exam-ready code pattern with the theory that justifies it. Arguments are tagged **ritual** (always the same), **structural** (forced by the data or the task) or **dial** (a real hyperparameter); the full list is in [](guide:parameter-reference).

## A deep RNN and the Keras skeleton

Keras convention, unchanging: `keras.models.Sequential([layers])` → `model.compile(loss, optimizer, metrics=[])` → `history = model.fit(X, y, epochs=..., validation_data=...)`. Learn that skeleton once and every network question becomes 'which layers, in which order'.

```python
import tensorflow as tf
from tensorflow import keras

model = keras.models.Sequential([
    keras.layers.SimpleRNN(20, return_sequences=True, input_shape=[None, 1]),
    keras.layers.SimpleRNN(20, return_sequences=True),
    keras.layers.TimeDistributed(keras.layers.Dense(10))
])

model.compile(loss="mse", optimizer="adam", metrics=[last_time_step_mse])
history = model.fit(X_train, Y_train, epochs=20,
                    validation_data=(X_valid, Y_valid))
```

| Argument | Kind | What it does |
|---|---|---|
| `20` | dial | Units (neurons) in the recurrent layer — the size of its memory. |
| `return_sequences=True` | structural | Output at EVERY time step instead of only the last. REQUIRED on any recurrent layer that feeds another recurrent layer, and on the last one too if you want a sequence-to-sequence output. Leave it off (default False) on the final layer when you want a single vector for the whole sequence. |
| `input_shape=[None, 1]` | structural | [time steps, features per step]. None = any sequence length. Only the FIRST layer takes it. |
| `TimeDistributed(Dense(10))` | structural | Applies the same Dense layer independently at every time step. 10 units = forecast 10 steps ahead from each position. |

## Batch and layer normalisation in RNNs

**Batch Normalization** normalises across the batch; between recurrent layers it helps only mildly, because it cannot be applied sensibly across time steps. **Layer Normalization** normalises across the features of a single instance, which suits RNNs much better — in the lab it is applied inside a custom `LNSimpleRNNCell` wrapped by `keras.layers.RNN(cell, return_sequences=True)`.

```python
model = keras.models.Sequential([
    keras.layers.SimpleRNN(20, return_sequences=True, input_shape=[None, 1]),
    keras.layers.BatchNormalization(),
    keras.layers.SimpleRNN(20, return_sequences=True),
    keras.layers.BatchNormalization(),
    keras.layers.TimeDistributed(keras.layers.Dense(10))
])
```

## LSTM

**LSTM**: forget / input / output gates and **two states** — the short-term h and the long-term c. It solves the vanishing memory of SimpleRNN over long sequences. Drop-in replacement: same arguments, same position in the Sequential list.

```python
model = keras.models.Sequential([
    keras.layers.LSTM(20, return_sequences=True, input_shape=[None, 1]),
    keras.layers.LSTM(20, return_sequences=True),
    keras.layers.TimeDistributed(keras.layers.Dense(10))
])
model.compile(loss="mse", optimizer="adam", metrics=[last_time_step_mse])
```

## GRU

**GRU** is a simplified LSTM: the forget and input gates are merged into one update gate and the two states are merged into one. Fewer parameters, comparable performance. In code, `SimpleRNN` / `LSTM` / `GRU` are interchangeable names in the same slot.

```python
model = keras.models.Sequential([
    keras.layers.GRU(20, return_sequences=True, input_shape=[None, 1]),
    keras.layers.GRU(20, return_sequences=True),
    keras.layers.TimeDistributed(keras.layers.Dense(10))
])
```

## Conv1D in front of recurrent layers

A **hybrid architecture**: the 1D convolution shortens and summarises the sequence before the recurrent layers see it, which makes training faster and lets the GRUs cover a longer effective history.

```python
model = keras.models.Sequential([
    keras.layers.Conv1D(filters=20, kernel_size=4, strides=2, padding="valid",
                        input_shape=[None, 1]),
    keras.layers.GRU(20, return_sequences=True),
    keras.layers.GRU(20, return_sequences=True),
    keras.layers.TimeDistributed(keras.layers.Dense(10))
])

model.compile(loss="mse", optimizer="adam", metrics=[last_time_step_mse])
history = model.fit(X_train, Y_train[:, 3::2], epochs=20,
                    validation_data=(X_valid, Y_valid[:, 3::2]))
```

| Argument | Kind | What it does |
|---|---|---|
| `filters=20` | dial | Number of feature maps the convolution learns. |
| `kernel_size=4` | dial | Width of the window in time steps. |
| `strides=2` | structural | Jump size. Stride 2 HALVES the output sequence length — which is why the targets must be downsampled. |
| `padding="valid"` | structural | No padding: the output is shorter and the first few steps are dropped. "same" pads to keep the length. |
| `Y_train[:, 3::2]` | structural | Not arbitrary: 'from step 3, every 2nd step'. The 2 matches strides=2; the 3 accounts for the steps lost to valid padding, so targets line up with outputs. |

## WaveNet: causal dilated convolutions

**WaveNet** stacks causal dilated convolutions. The full paper version adds gated activation units and residual + skip connections (`wavenet_residual_block` in the lab); the simplified stack above is what an exam asks for.

```python
model = keras.models.Sequential()
model.add(keras.layers.InputLayer(input_shape=[None, 1]))

for rate in (1, 2, 4, 8) * 2:
    model.add(keras.layers.Conv1D(filters=20, kernel_size=2,
                                  padding="causal", activation="relu",
                                  dilation_rate=rate))

model.add(keras.layers.Conv1D(filters=10, kernel_size=1))
model.compile(loss="mse", optimizer="adam", metrics=[last_time_step_mse])
history = model.fit(X_train, Y_train, epochs=20,
                    validation_data=(X_valid, Y_valid))
```

| Argument | Kind | What it does |
|---|---|---|
| `padding="causal"` | structural | Pads only on the LEFT, so an output at time t depends only on inputs up to t. No peeking at the future — mandatory for forecasting and generation. |
| `dilation_rate=1,2,4,8` | structural | Gaps between the kernel's taps. Doubling each layer makes the receptive field grow EXPONENTIALLY with depth, so a handful of layers covers a long history. |
| `(1,2,4,8) * 2` | structural | Python list repetition: the block of four dilations runs twice, giving eight layers. |
| `kernel_size=1` | structural | The final 1-wide convolution is just a Dense layer applied per time step — it produces the 10 outputs. |

## A metric on the last time step

Training the model to predict at **every** time step gives far more error gradients and stabilises training, but the metric that matters is the error at the final step. `Y[:, -1]` selects the last time step of every sequence in the batch.

```python
def last_time_step_mse(Y_true, Y_pred):
    return keras.metrics.mean_squared_error(Y_true[:, -1], Y_pred[:, -1])

model.compile(loss="mse", optimizer="adam", metrics=[last_time_step_mse])

# a custom optimizer instance when a learning rate is requested
model.compile(loss="mse",
              optimizer=keras.optimizers.Adam(learning_rate=0.01),
              metrics=[last_time_step_mse])
```

## Remember it

The same sections as scenes along a route: [](palace:11-attic). The code is drilled in [the decks](cards).
