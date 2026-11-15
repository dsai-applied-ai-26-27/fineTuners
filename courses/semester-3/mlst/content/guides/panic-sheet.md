---
title: 'Panic sheet'
summary: 'For the ten minutes before you walk in. The six code skeletons, the layers in the slot they go, the arguments that cost marks, and Section A in one line each.'
---

Skeletons first. If you can write these six, you can start every Section B answer.

## The six skeletons

**Any model**

```python
model = SomeModel(hyperparameters)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```

**Any transformer**

```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)
```

**End-to-end task**

```python
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)
model = SomeModel(random_state=42)
model.fit(X_train_scaled, y_train)
print(mean_squared_error(y_test, model.predict(X_test_scaled)))
```

**Pipeline (2-tuples) and ColumnTransformer (3-tuples)**

```python
num_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("std_scaler", StandardScaler()),
])
full_pipeline = ColumnTransformer([
    ("num", num_pipeline, num_attribs),
    ("cat", OneHotEncoder(), cat_attribs),
])
X_prepared = full_pipeline.fit_transform(X)
```

**Keras Sequential**

```python
model = keras.models.Sequential([ ...layers... ])
model.compile(loss="mse", optimizer="adam", metrics=["accuracy"])
history = model.fit(X_train, y_train, epochs=20,
                    validation_data=(X_valid, y_valid))
```

**Keras Functional (two inputs, or a state handoff)**

```python
inputs  = keras.layers.Input(shape=[None, 1])
z       = keras.layers.SomeLayer(...)(inputs)
outputs = keras.layers.Dense(n, activation="softmax")(z)
model = keras.models.Model(inputs=[inputs], outputs=[outputs])
```

## Layers, in the slot they go

**Recurrent: interchangeable names**

```python
keras.layers.SimpleRNN(20, return_sequences=True, input_shape=[None, 1]),
keras.layers.LSTM(20, return_sequences=True),      # 3 gates, 2 states
keras.layers.GRU(20, return_sequences=True),       # 2 gates, 1 state
keras.layers.BatchNormalization(),                 # between recurrent layers
keras.layers.TimeDistributed(keras.layers.Dense(10))
```

**Convolutional over sequences**

```python
keras.layers.Conv1D(filters=20, kernel_size=4, strides=2, padding="valid")
keras.layers.Conv1D(filters=20, kernel_size=2, padding="causal",
                    activation="relu", dilation_rate=rate)   # WaveNet
keras.layers.Conv1D(filters=10, kernel_size=1)     # = per-step Dense
```

**Encoder to decoder**

```python
encoder = keras.layers.LSTM(128, return_state=True)
encoder_outputs, state_h, state_c = encoder(encoder_embeddings)
decoder_outputs = keras.layers.LSTM(128, return_sequences=True)(
    decoder_embeddings, initial_state=[state_h, state_c])
```

## Arguments that cost marks

| Write | Because |
|---|---|
| `SVC(probability=True)` | Required for soft voting: SVC has no `predict_proba` otherwise |
| `PolynomialFeatures(include_bias=False)` | LinearRegression adds its own intercept |
| `max_iter=1` + `warm_start=True` + `tol=-np.infty` | The three that make a manual epoch loop work |
| `deepcopy(model)` | Snapshot of a trained model. `clone(model)` is an untrained copy for CV folds |
| `return_sequences=True` | On every recurrent layer feeding another one; drop it on the last for one output |
| `TimeDistributed(Dense(n))` | Only valid when the layer below returns sequences |
| `padding="causal"` | Forecasting and WaveNet: never see the future |
| `strides=2` with `Y_train[:, 3::2]` | The stride halves the sequence, so downsample the targets |
| `n_components=0.95` | A float is a share of variance; an int is a number of dimensions |
| `bootstrap=True` | Bagging. `False` is pasting. `oob_score=True` only with `True` |
| `return_state=True` | LSTM returns 3 values, GRU returns 2. Pair with `initial_state=` |
| `loss="sparse_categorical_crossentropy"` | Multi-class with integer labels. `binary_crossentropy` for one sigmoid unit |
| `fit_transform` / `transform` | Train / test. Fitting on test is leakage |
| `cross_val_predict` | Predictions, for a confusion matrix. `cross_val_score` gives fold scores |

## Section A, in one line each

| Topic | The line |
|---|---|
| One-hot against dummy | $k$ columns against $k - 1$. One-hot plus the intercept is perfectly collinear, so $X^\top X$ is singular and the coefficients are not identifiable |
| $\mathbb{I}(\cdot)$ | The indicator function: 1 if the condition holds, 0 otherwise. It builds each encoded column |
| ERM | Minimise the average training loss as a stand-in for the expected loss. Analytic $\theta = (X^\top X)^{-1} X^\top y$, or numeric $\theta \leftarrow \theta - \alpha \nabla$ |
| Gower distance | Per-feature dissimilarity in $[0, 1]$, averaged. Numeric: absolute difference over range. Categorical: match or no match. Handles mixed types without scaling |
| SVM primal | $\min \tfrac12 \lVert w \rVert^2$ subject to $y_i (w^\top x_i + b) \ge 1$ |
| SVM dual | $\max \sum_i \alpha_i - \tfrac12 \sum_i \sum_j \alpha_i \alpha_j y_i y_j\, x_i^\top x_j$ with $\alpha_i \ge 0$ and $\sum_i \alpha_i y_i = 0$. Data appears only as inner products, hence kernels |
| Support vectors | The points with $\alpha_i > 0$. Only those on the margin determine the solution |
| Score against probabilistic | A score is thresholded at 0, a probability at 0.5. Move the threshold when costs are asymmetric |
| Precision and recall | Precision $= TP/(TP+FP)$, recall $= TP/(TP+FN)$, F1 the harmonic mean. Raising the threshold raises precision and lowers recall |
| ROC against PR | ROC is TPR against FPR, AUC 1.0 perfect and 0.5 random. PR is better for rare positives because it ignores TN |
| Bias against variance | Bias: high error on both train and test. Variance: low train, high test. Test error is U-shaped in complexity |
| Bootstrap | Sample with replacement: about 63.2% in-bag, about 37% out-of-bag, which is free validation |
| LOOO-CV | Keep all observations of one object on one side of the split, or the model memorises the object |
| Bagging against boosting | Parallel, cuts variance. Sequential, cuts bias. AdaBoost reweights instances; gradient boosting fits residuals |
| Random forest | Bagging plus a random feature subset per split, which decorrelates the trees |
| CART | Recursive greedy exhaustive search. Gini pairs with Brier, entropy with log loss. Control with `max_depth`, `min_samples_*`, `ccp_alpha` |
| LDA against QDA | Shared covariance gives a linear boundary; per-class covariance gives a quadratic one |
| Naive Bayes | Generative; assumes conditional independence of the features given the class |
| Kernel trick | A kernel gives the inner product in a high-dimensional space without computing the mapping |
| C and gamma | Large C: narrow margin, less regularisation. Large gamma: wiggly boundary. If overfitting, lower both |
| k-NN | Majority vote or average of the $k$ neighbours. Scaling is mandatory. Small $k$: high variance. Large $k$: high bias |
| L1 against L2 | L1: robust to outliers, not differentiable at 0, drives coefficients to zero. L2: convex, closed form, sensitive to outliers |

The full answers are in [](deck:section-a), the formulas on [the sheet](formulas), and the
plan this page closes is on [](exam:final).
