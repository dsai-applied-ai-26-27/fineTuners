---
title: 'Parameter reference'
summary: 'Every argument that appears in the course code, sorted into three kinds: ritual, structural and dial. Knowing the kind says whether to memorise it, derive it or reason about it.'
---

No parameter in this course is arbitrary, but they are not all the same kind of thing. Each falls into one of three buckets, and the bucket says what to do with it.

## Ritual: memorise once

Always the same. Memorise it once and never think about it again.

| Parameter | Seen in | What it does | How to set it |
|---|---|---|---|
| `random_state=42` | everywhere | Seeds the RNG so the split, the shuffle and the model are reproducible. | Never changes. Also np.random.seed(42) and tf.random.set_seed(42) at the top of a notebook. |
| `solver="lbfgs"` | LogisticRegression | The default optimiser for logistic regression. | Boilerplate — write it and move on. |
| `algorithm="SAMME.R"` | AdaBoost | Probability-based variant of AdaBoost; the default. | Boilerplate. |
| `store_covariance=True` | LDA / QDA | Keeps the estimated covariance matrices so they can be plotted. | Has no effect on predictions. |
| `n_jobs=-1` | forests, grid search | Use all CPU cores. | Speed only, never accuracy. |
| `optimizer="adam"` | model.compile | Adaptive optimiser, the default choice here. | Use keras.optimizers.Adam(learning_rate=0.01) only when the question specifies a learning rate. |

## Structural: derive it from the question

Forced by the data or the task. It is never a choice, so derive it from what the question says.

| Parameter | Seen in | What it does | How to set it |
|---|---|---|---|
| `n_splits` | StratifiedShuffleSplit / KFold | Number of splits or folds produced. | 1 for a single train/test split; k (often 3, 5 or 10) for cross-validation. |
| `include_bias=False` | PolynomialFeatures | Whether to add the column of 1s. | Always False here: LinearRegression fits its own intercept and StandardScaler cannot handle a zero-variance column. |
| `max_iter=1` | SGDRegressor early stopping | One epoch per .fit() call. | Only for the manual early-stopping loop; the ordinary value is 1000. |
| `warm_start=True` | SGDRegressor, GradientBoosting | Continue from the existing parameters instead of resetting. | Mandatory in any incremental training loop; without it every iteration restarts from scratch. |
| `tol=-np.infty` | SGDRegressor early stopping | Disables sklearn's internal stopping rule. | No improvement can ever be smaller than −∞, so it never stops by itself. Your loop is in charge. |
| `penalty=None` | SGDRegressor | No L1/L2 term in the loss. | Used when early stopping is doing the regularising. penalty="l2" makes it Ridge, "l1" makes it Lasso. |
| `probability=True` | SVC | Enables predict_proba via extra calibration. | Required for soft voting. Slows training noticeably. |
| `kernel` | SVC, SVR, KernelPCA | Which implicit feature space to work in. | "linear", "poly" (with degree, coef0), "rbf" (with gamma), "sigmoid". |
| `bootstrap=True` | BaggingClassifier | Sample WITH replacement. | True = bagging. False = pasting. That boolean is the entire difference between the two methods. |
| `oob_score=True` | BaggingClassifier, forests | Evaluate on the ~37% never drawn. | Only meaningful with bootstrap=True. Read the result from .oob_score_. |
| `staged_predict(X_val)` | GradientBoosting | Generator of predictions after each successive tree. | The one-fit way to find the best n_estimators: np.argmin(errors) + 1. |
| `n_components` | PCA, KernelPCA, LLE | Target dimensionality. | INT = that many dimensions. FLOAT < 1 = keep that fraction of the variance and let PCA choose the count. |
| `fit_inverse_transform=True` | KernelPCA | Enables mapping reduced points back to the original space. | Needed to compute reconstruction error. |
| `return_sequences=True` | recurrent layers | Emit an output at every time step. | Required on any recurrent layer feeding another recurrent layer, and on the last one for sequence output. Omit it on the final layer to collapse to one vector. |
| `return_state=True` | LSTM / GRU | Also return the final internal state(s). | LSTM returns 3 values (output, h, c), GRU returns 2. Used to build the encoder–decoder handoff. |
| `initial_state=encoder_state` | decoder LSTM/GRU | Start the decoder from the encoder's final state. | This single argument is what makes a pair of LSTMs an encoder–decoder. |
| `input_shape=[None, 1]` | first layer only | [time steps, features]. None = any length. | Derive it from the data: [None, 1] is a univariate series, [None, max_id] one-hot characters, [None] integer token IDs. |
| `batch_input_shape=[batch_size, None, max_id]` | stateful RNN | Full batch shape including a fixed batch size. | Stateful layers require it, because the state must line up across batches. |
| `stateful=True` | recurrent layers | Carry the hidden state between batches. | Needs sequential (unshuffled) batches and a reset_states() callback at each epoch. |
| `TimeDistributed(Dense(10))` | output layer | Apply the same Dense at every time step. | Only valid when the layer beneath has return_sequences=True. |
| `strides=2` | Conv1D | Step between window positions. | Halves the output length — the targets must be downsampled to match (Y_train[:, 3::2]). |
| `padding="causal"` | Conv1D | Pad only on the left. | Output at t depends only on inputs up to t. Mandatory for forecasting and WaveNet; "valid" shortens, "same" keeps the length but peeks at the future. |
| `dilation_rate=1,2,4,8` | Conv1D | Gap between the kernel's taps. | Doubling per layer grows the receptive field exponentially, so few layers cover a long history. |
| `mask_zero=True` | Embedding | Treat token 0 as padding and ignore it downstream. | Pair it with padded sequences. |
| `loss="mse"` | model.compile | Regression / forecasting loss. | Follows from the task: binary_crossentropy for binary, sparse_categorical_crossentropy for integer multi-class labels, categorical_crossentropy for one-hot. |
| `use_scale=True / causal=True` | Attention | Learned score scaling / masking of future positions. | causal=True belongs to decoder self-attention only. |

## Dial: know which way it turns

A real hyperparameter. The examinable part is which way it turns and what happens.

| Parameter | Seen in | What it does | How to set it |
|---|---|---|---|
| `test_size=0.2` | train_test_split, StratifiedShuffleSplit | Fraction held out for testing. | Smaller test set = noisier estimate. Smaller training set = pessimistically biased model. |
| `cv=3` | cross_val_score, GridSearchCV | Number of cross-validation folds per candidate. | More folds = more reliable and linearly more expensive. k=10 is the common balance. |
| `strategy="median"` | SimpleImputer | Value used to fill missing entries. | median is robust to outliers and skew; mean, most_frequent and constant are the alternatives. |
| `degree` | PolynomialFeatures, poly kernel | Highest power of the generated monomials. | Up = more flexible, more overfitting, more Runge oscillation at the edges. |
| `alpha` | Ridge, Lasso, ElasticNet, ccp_alpha | Regularisation strength. | Up = simpler model, more bias, less variance. alpha=0 recovers plain LinearRegression. |
| `l1_ratio=0.5` | ElasticNet | The MIX between L1 and L2, not the strength. | 0 = pure Ridge, 1 = pure Lasso. |
| `solver="cholesky"` | Ridge | Closed-form matrix factorisation. | "sag" (stochastic average gradient) for large datasets; "auto" to let sklearn choose. |
| `learning_rate="constant"` | SGDRegressor | No decay schedule for eta. | Keeps epochs comparable. "optimal" and "invscaling" decay instead. |
| `eta0=0.0005` | SGDRegressor | The initial (here constant) learning rate. | Too high overshoots and diverges; too low converges uselessly slowly. |
| `t0, t1 = 5, 50` | manual SGD learning_schedule | Numerator and offset of eta = t0/(t+t1). | Larger t1 = slower cooling. Mini-batch GD in the same lab uses 200, 1000. |
| `C` | LogisticRegression, SVC, LinearSVC | INVERSE regularisation strength. | Opposite direction to alpha. Large C = fit hard, narrow margin, overfitting risk. Small C = strong regularisation, wide margin. |
| `gamma` | RBF kernels, KernelPCA | Reach of a single training point's influence. | Large gamma = narrow bell = wiggly, overfitting boundary. Small = smooth. If overfitting, lower gamma AND C. "scale" derives it from the data. |
| `coef0` | poly / sigmoid kernels | Weight of high-degree terms relative to low-degree ones. | Raise it when high-degree terms matter (lab uses 1 for degree 3, 100 for degree 10). |
| `epsilon` | SVR, LinearSVR | Half-width of the tube inside which errors cost nothing. | Only exists in SVM regression. Larger = flatter, simpler model. |
| `n_neighbors=5` | KNeighborsClassifier | How many neighbours vote. | Small k = jagged, low bias, high variance. Large k = smooth, high bias, low variance. |
| `weights="distance"` | `KNeighbors*` | Closer neighbours count more (w = 1/d). | Default "uniform" weights all k equally; distance weighting captures local detail better. |
| `max_depth` | trees, boosting | Longest chain of questions. | Down = simpler and more regularised. Boosting wants shallow trees (2–3). |
| `max_leaf_nodes` | trees, forests | Cap on terminal regions. | Down = more regularised. |
| `min_samples_split / min_samples_leaf` | trees | Minimum samples to split a node / to remain in a leaf. | Up = more regularised. Every `min_*` up and every `max_*` down regularises a tree. |
| `criterion` | trees | Impurity measure for splitting. | Classification: "gini" (= Brier) or "entropy" (= log loss). Regression: squared error / variance. |
| `ccp_alpha` | trees | Cost-complexity pruning penalty. | Up = more branches pruned away. 0 = no pruning. |
| `n_estimators` | all ensembles | How many predictors in the ensemble. | Bagging/forests: more is safe. Boosting: too many overfits — that is why early stopping exists. |
| `max_samples=100` | BaggingClassifier | Size of each bootstrap sample. | int = a count, float = a fraction of the training set. |
| `max_features="sqrt"` | trees inside a forest | Features considered at each split (mtry). | This is what decorrelates the trees; it is built into RandomForest. |
| `learning_rate` | AdaBoost, GradientBoosting, Adam | Shrinkage of each predictor's contribution. | Low learning_rate + many estimators generalises better than the reverse. |
| `svd_solver="randomized"` | PCA | Approximate, much faster SVD. | Worth it when the target dimension is far smaller than the number of features. |
| `units (20, 128, 512)` | SimpleRNN, LSTM, GRU, Dense | Size of the layer's memory / output width. | Bigger = more capacity and more overfitting risk. The lab uses 20 for toy series, 128 for text. |
| `filters` | Conv1D | Number of feature maps learned. | More = more capacity. |
| `kernel_size` | Conv1D | Width of the window in time steps. | kernel_size=1 is a per-time-step Dense layer. |
| `epochs=20` | model.fit | Passes over the training set. | Watch validation loss; stop when it turns upward. |
