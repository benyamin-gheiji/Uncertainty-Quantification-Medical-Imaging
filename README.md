# Uncertainty Quantification of Machine Learning Models in Medical Imaging

**A free, hands-on course — 19 sessions on teaching medical imaging models to know what they don't know.**

📖 **Read online:** https://benyamin-gheiji.github.io/Uncertainty-Quantification-Medical-Imaging/

---

## What this course is about

This course is about a single, practical problem: how do you build a medical imaging model
that knows when it might be wrong?

Most machine learning teaching stops at accuracy. But a model deployed in a hospital needs
to do more than be right most of the time — it needs to signal the cases where a clinician
should look more carefully. A model with 95% accuracy that fails silently on the
remaining 5% is far more dangerous than one that flags its own uncertain cases for review.

We start from the clinical reasoning behind that idea, work through the main techniques for
quantifying uncertainty — implementing each one in PyTorch on real chest X-ray data — and
finish by evaluating the uncertainty those methods produce, because an uncertainty estimate
is only useful once you can show it is trustworthy.

By the end you should be able to take an existing model, attach a well-founded uncertainty
estimate to its predictions, check honestly whether that estimate can be trusted, and decide
which method fits the problem in front of you.

## Who it's for

Researchers and practitioners building models for medical imaging, and anyone who needs
their predictions to carry an honest measure of confidence. You will get the most out of it
with:

| | Prerequisite | What's assumed |
|---|---|---|
| 01 | **Python** | Functions, classes, NumPy arrays, working in Jupyter notebooks |
| 02 | **Machine learning fundamentals** | Training and evaluation, over/underfitting, data splits, metrics beyond accuracy |
| 03 | **Deep learning & PyTorch** | How networks are trained; enough PyTorch to define a model, write a training loop, run inference |
| 04 | **Medical imaging data** | Some experience with image datasets, and an appreciation of the clinical stakes when a model is wrong |

## Three ways to follow along

1. **Read it on the web** — the [course website](https://benyamin-gheiji.github.io/Uncertainty-Quantification-Medical-Imaging/)
   renders every session with navigation between parts and sessions. Nothing to install.
2. **Run it on Kaggle** — every session is published as a Kaggle notebook (linked in the
   table below and from the top of each session page). Free GPUs, no local setup, the chest
   X-ray dataset already attached.
3. **Run it locally** — clone this repository and open any notebook in `session NN/`. You'll
   need `jupyter`, `torch`, `numpy`, `matplotlib` and `scikit-learn`; the implementation
   sessions also expect the chest X-ray dataset.

## Course outline

### Part 1 — Foundations · Sessions 1–3

Clinical motivation, the two failure modes of AI (overconfidence and underconfidence), the
two kinds of uncertainty, and how clinicians already reason probabilistically.

| # | Session | Type | Kaggle |
|---|---|---|---|
| 1 | Why Uncertainty Matters in Medicine | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-1-why-uncertainty-matters-in-medicine) |
| 2 | Aleatoric vs Epistemic Uncertainty | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-2-aleatoric-vs-epistemic-uncertainty) |
| 3 | Uncertainty in Clinical Practice | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-3-uncertainty-in-clinical-practice) |

### Part 2 — Core UQ Methods · Sessions 4–15

The methods themselves. Each concept session is followed by a PyTorch implementation on real
chest X-ray data, and the part closes with a side-by-side comparison of all five approaches.

| # | Session | Type | Kaggle |
|---|---|---|---|
| 4 | The Bayesian Perspective | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-4-the-bayesian-perspective) |
| 5 | Variational Inference | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-5-variational-inference/) |
| 6 | Variational Inference — Implementation | Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-6-variational-inference-implementation/) |
| 7 | MC Dropout | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-7-mc-dropout/) |
| 8 | MC Dropout — Implementation | Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-8-mc-dropout-implementation/) |
| 9 | Deep Ensembles | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-9-deep-ensembles/) |
| 10 | Deep Ensembles — Implementation | Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-10-deep-ensembles/) |
| 11 | Evidential Deep Learning | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-11-evidential-deep-learning/) |
| 12 | Evidential Deep Learning — Implementation | Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-12-edl-implementation/) |
| 13 | Conformal Prediction | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-13-conformal-prediction) |
| 14 | Conformal Prediction — Implementation | Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-14-conformal-prediction-implementation/) |
| 15 | Part 2 Summary | Summary | [open](https://www.kaggle.com/code/benyamingheiji/session-15-part-2-summary/) |

### Part 3 — Evaluation & Reliability · Sessions 16–18

Having produced uncertainty estimates, we ask whether they can be trusted. All three
sessions combine the concept and its implementation in a single notebook.

| # | Session | Type | Kaggle |
|---|---|---|---|
| 16 | Calibration | Concept + Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-16-calibration) |
| 17 | Risk–Coverage Analysis | Concept + Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-17-risk-coverage-analysis/) |
| 18 | Out-of-Distribution Detection | Concept + Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-18-out-of-distribution-detection/) |

### Part 4 — Future Directions · Session 19

How to choose a method for a real clinical problem, what is still unsolved, and where the
field is going.

| # | Session | Type | Kaggle |
|---|---|---|---|
| 19 | Final Summary & Future Directions | Summary | [open](https://www.kaggle.com/code/benyamingheiji/session-19-final-summary-future-directions) |

## What you'll take away

- Why accuracy alone is not enough in clinical AI, and how clinicians reason probabilistically
- The difference between **aleatoric** (data) and **epistemic** (model) uncertainty, and why
  it changes the clinical response
- Bayesian deep learning — variational inference and MC Dropout — alongside Deep Ensembles,
  Evidential Deep Learning, and Conformal Prediction with guaranteed coverage
- Calibration, risk–coverage trade-offs, and out-of-distribution detection
- Working PyTorch implementations of every method, on real data

## Authors

| | |
|---|---|
| **Benyamin Gheiji** | Course Author |
| **Danial Elyassirad** | Course Author |
| **Mahsa Vatanparast** | Course Author |
| **Shahriar Faghani** | Content Supervisor |

## Repository layout

```
session 01/ … session 19/   the course notebooks and their figures
docs/                       the generated course website (served by GitHub Pages)
build.py, site/             the site generator — see BUILDING.md
```
