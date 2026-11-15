---
title: Introduction to pattern recognition
number: 1
topics: [intro]
summary: What a pattern, a feature and a classifier are, the processing chain every recognition system follows, and the fish example that introduces overfitting.
takeaways:
  - A pattern recognition system is two boxes in a row, a **feature extractor** and a **classifier**, and most of the difficulty is in the first.
  - Good features make the variability *within* a class small compared with the variability *between* classes.
  - A boundary that separates the training samples perfectly can still fail on new data. That is overfitting.
  - More features do not always help. The rule of thumb is $n \ge N(N-1)/2$ training examples for $N$ features.
  - Correlated or badly scaled features break Euclidean distance. Rescale them, or use Mahalanobis distance.
sources:
  - lectures/L1_intro_to_ML_PatternRecognition.pdf
---

## Where this fits

Lecture 1 sets up the vocabulary for the whole course. It contains no derivations. What it
does contain is the picture every later lecture fills in: raw data goes through a feature
extractor, then a classifier, and a category comes out. Lectures on representation and
feature extraction are about the first box; the lectures on distance-based and
statistics-based classification are about the second.

:::note Not in these notes
Slides 2 to 11 cover organisation. The part worth keeping: grading is project 40%
(lab 10%, project 25%, quiz 5%), midterm 20% (after week 5, one attempt, threshold 50%) and
a mandatory final 40% (threshold 50%). The main textbook is Fieguth, *An Introduction to
Pattern Recognition and Machine Learning* (slides 8 and 10).
:::

## Why learn from examples

Some problems, such as recognising a face, are very hard to solve by writing a program by
hand. We do not know how our own brain does it, and a hand-written program would be
"horrendously complicated" even if we did (slide 12).

Machine learning turns the problem around. Instead of writing the program, we collect many
examples that give the correct output for a given input. A learning algorithm takes those
examples and produces the program. That program may look nothing like hand-written code (it
can be millions of numbers), and if it is done right it works on **new** cases as well as on
the ones it was trained on.

:::recall What is the test of whether learning worked?
That the produced program works on new cases, not only on the examples it was trained on
(slide 12). Performance on the training examples alone proves nothing.
:::

## Patterns and recognition

:::definition Pattern
A repeated or regular arrangement of elements, events or objects that follows a specific rule
or structure. In practice it is an abstraction: a set of **measurements** describing a
physical object (slide 13). Slide 29 gives the working version: an object, process or event
that can be given a name.
:::

*Recognition* is "re-cognition": knowing again, the feeling that the present object has been
met before (slide 14). Pattern recognition as a field studies how machines can (slide 25)

1. observe the environment,
2. learn to distinguish patterns of interest,
3. make sound and reasonable decisions about the categories of the patterns.

The vocabulary used from here on (slide 29):

:::definition Pattern class
A set of patterns sharing common attributes, usually originating from the same source. Also
called a category.
:::

:::definition Classifier
A machine that performs classification: it assigns given objects to prescribed classes.
:::

Slide 29 quotes the one-sentence version of the whole subject: classification is "the
assignment of a physical object or event to one of several prespecified categories".

Patterns of the same class do not look identical. A face changes with expression, lighting
and occlusion (slide 23). Handling that variation is the actual problem.

## Two phases

Every recognition system works in two phases (slide 30).

- **Training (learning).** The system is shown several examples of each class and builds a
  model for identifying each class. Learned adequately, the model becomes general.
- **Detecting (classifying).** The model is applied to new patterns.

## Three kinds of learning

The kinds differ in what the "teacher" provides (slides 37 to 39).

| Kind | What the training set contains | Typical task |
|---|---|---|
| **Supervised** | A category label (or cost) for each pattern | Classification |
| **Unsupervised** | No labels. The system forms clusters, natural groupings by some similarity criterion | Clustering |
| **Reinforcement** | No desired category, only feedback on whether a decision was right or wrong | Learning from outcomes |

The same unlabelled objects can be grouped in more than one valid way. On slide 38 one
classifier is trained on shape (triangles and circles) and another on colour (yellow and
blue), from the same objects. In unsupervised learning (slide 39) the grouping depends
entirely on the similarity measure you choose.

## The processing chain

A real system has five stages (slide 40, after Fieguth).

1. **Data acquisition and sensing.** Measuring physical variables. Bandwidth and resolution
   matter here.
2. **Pre-processing.** Removing noise and isolating the pattern of interest from its
   background.
3. **Feature extraction.** Finding a new representation in terms of features.
4. **Classification.** Using the features and the learned model to assign a category.
5. **Post-processing.** Evaluating the confidence of the decision.

The **classical model** (slide 47) keeps only stages 3 and 4:

$$\text{raw data} \;\longrightarrow\; \text{feature extractor} \;\xrightarrow{\;x = (x_1, \dots, x_d)\;}\; \text{classifier} \;\longrightarrow\; \text{category } 1, 2, \dots, c$$

:::paper
A pattern recognition system has two parts. The **feature extractor** turns raw data into a
feature vector $x$. The **classifier** receives $x$ and assigns it to one of $c$ categories.
:::

## Features

A feature is a property of an object. A good one is (slide 41)

- representative of a specific class of objects,
- compact (cheap in memory),
- computationally simple,
- perceptually relevant, if the classifier is meant to imitate a human.

Above all, features "should pave the way to a good discrimination of different classes".

Several features together form a **feature vector** $x = (x_1, x_2, \dots, x_d)$, for example
shape (number of sides), size and colour. Each object is then one point in a $d$-dimensional
**feature space** (slides 45 and 46).

:::theorem What a feature extractor should do (slide 56)
The ideal feature extractor would produce the *same* feature vector for all patterns of the
same class and *different* feature vectors for patterns of different classes. In practice
different inputs always give different vectors, so the aim is that

$$\text{within-class variability} \;\ll\; \text{between-class variability}.$$
:::

That one inequality is what the later lecture on Fisher's discriminant turns into a formula.
The slide adds that designing good features "is sometimes more of an art than a science",
and that the design is specific to the problem.

## Case study: sorting fish

The running example (slides 49 to 55): sort fish on a conveyor belt into **sea bass** and
**salmon** from a camera image. The steps are capture the image, isolate the fish
(pre-processing), take measurements (feature extraction), make the decision
(classification).

**One feature: length.** A fisherman says sea bass are generally longer. Plot the histograms
of length for the two species in the training samples and pick a threshold. It does not
work well: although sea bass are longer *on average*, there are many fish for which that
does not hold. The histograms overlap (slide 51).

**A better feature.** Try another measurement (slide 52; the slide labels it weight, the
textbook version uses lightness). The histograms overlap less, so a threshold is easier to
choose, but a perfect decision is still impossible.

**Two features.** Use two measurements at once (slide 53). Each fish becomes a point in a 2-D
feature space, and a **decision boundary**, here a line, divides the space into two
regions. Combining features separates the classes better than either feature alone.

**A more complex boundary.** A wiggly curve can separate the training samples perfectly
(slide 54).

:::pitfall Overfitting
A boundary that classifies every training sample correctly is not the goal. It has adapted
to the particular samples, including their noise, and will fail to generalise to new fish.
The question to ask of any classifier is how it performs on samples it has not seen.
:::

Slide 55 states the design problem that follows: manage the trade-off between the complexity
of the decision rule and its performance on unknown samples. Different criteria lead to
different boundaries.

:::recall Why not simply keep adding features until the training samples separate?
Because of the curse of dimensionality (next section) and overfitting. Separation of the
training set is not evidence of performance on new data.
:::

## When features go wrong

**Too many features.** Adding features does not always improve results (slide 57). The slide
gives a rule of thumb for how much data a feature set needs:

$$n \;\ge\; \frac{N(N-1)}{2}$$

where $n$ is the number of examples in the training set and $N$ the number of features. This
is the **curse of dimensionality**. The advice: avoid unreliable features, watch for
correlation with features you already have, and be careful about measurement and noise.

**Inadequate features.** If the features do not contain the information that separates the
classes, no classifier can recover it. Go back and design better features (slide 58).

**Correlated or badly scaled features.** Two features meant to measure different things often
vary together because of a common cause. The perimeter and the maximum width of a figure both
grow with its scale (slide 59). A classifier based on Euclidean distance to a template then
degrades: a pattern at the extreme of one class can be closer to the template of another
class than to its own. Measuring one feature in microns and another in kilometres causes the
same failure.

:::tip
The fixes named on slide 59: use a metric that accounts for spread and correlation, such as
**Mahalanobis distance**, and extract features that are insensitive to scale.
:::

## Designing a classifier

Choosing a model means weighing domain knowledge and prior information, the design
criterion, parametric against non-parametric models, and computational cost (slide 60).

Three problems the slides name, each with its remedy:

| Problem | Example | Remedy |
|---|---|---|
| **Curved boundaries** (slide 62) | $x_1$ is a perimeter, $x_2$ an area. One grows linearly with scale, the other quadratically, which warps the feature space, and a linear boundary performs badly | Redesign the feature (use $\sqrt{\text{area}}$), use Mahalanobis distance (it can give quadratic boundaries), or use a nonlinear model |
| **Subclasses** (slide 63) | The classes the user defined are not the natural groups in the data | Clustering |
| **Complex feature space** (slide 67) | No simple boundary exists | A different type of classifier, or nonlinear features |

## Simple classifiers

**Minimum-distance classifier** (slide 64). Assign $x$ to the class whose template $m$ is
nearest under a chosen metric, for example $\lVert x - m \rVert$. Which metric is part of
the definition: Euclidean and Manhattan (taxicab) are named on slide 66, and finding others
is set as homework.

**Template matching** (slide 65). To classify a noisy example, compare it with a template of
each class. Two equivalent ways to score the comparison:

1. count the **agreements** and pick the class with the most (maximum correlation), or
2. count the **disagreements** and pick the class with the fewest (minimum error).

It works when the variation inside a class is additive noise only. It fails under
translation, rotation, shearing, warping, scaling or occlusion.

Slides 68 and 69 show neural networks and Gaussian modelling as pictures only; both return
in later lectures.

## Where next

Drill the vocabulary with [](deck:ch1-introduction). The inequality from slide 56 becomes a
formula in [](guide:fisher-and-pca), and the minimum-distance classifier is worked out in
[](guide:distance-and-boundaries).
