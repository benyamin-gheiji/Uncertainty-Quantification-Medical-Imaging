# 🩺 Uncertainty Quantification in Medical Imaging Analysis

**A free, hands-on course — 19 sessions on teaching medical imaging models to know what they don't know.**

📖 **Read online:** https://benyamin-gheiji.github.io/Uncertainty-Quantification-Medical-Imaging/

---

## 🎯 What this course is about

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

## 👥 Who it's for

This course is written for researchers and practitioners who already build models for
medical imaging and want their predictions to carry an honest measure of confidence. You
will get the most out of it if you are comfortable with **Python**, understand the
**fundamentals of machine learning**, have some working familiarity with **deep learning
and PyTorch**, and have previously worked with **medical imaging data**. No prior exposure
to UQ methods is assumed — everything in that direction
is built up from the beginning.

## 🚀 Three ways to follow along

1. **Read it on the web** — the [course website](https://benyamin-gheiji.github.io/Uncertainty-Quantification-Medical-Imaging/)
   renders every session with navigation between parts and sessions.
2. **Run it on Kaggle** — every session is published as a Kaggle notebook (linked in the
   table below and from the top of each session page). Free GPUs, no local setup, the chest
   X-ray dataset already attached.
3. **Run it locally** — clone this repository and open any notebook in `session NN/`. The
   implementation sessions expect the
   [chest X-ray pneumonia dataset](https://www.kaggle.com/datasets/paultimothymooney/chest-xray-pneumonia).

## 🗺️ Course outline

### 🌱 Part 1 — Foundations · Sessions 1–3

Clinical motivation, the two failure modes of AI (overconfidence and underconfidence), the
two kinds of uncertainty, and how clinicians already reason probabilistically.

| # | Session | Type | Kaggle |
|---|---|---|---|
| 1 | Why Uncertainty Matters in Medicine | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-1-why-uncertainty-matters-in-medicine) |
| 2 | Aleatoric vs Epistemic Uncertainty | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-2-aleatoric-vs-epistemic-uncertainty) |
| 3 | Uncertainty in Clinical Practice | Concept | [open](https://www.kaggle.com/code/benyamingheiji/session-3-uncertainty-in-clinical-practice) |

### ⚙️ Part 2 — Core UQ Methods · Sessions 4–15

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

### 📐 Part 3 — Evaluation & Reliability · Sessions 16–18

Having produced uncertainty estimates, we ask whether they can be trusted. All three
sessions combine the concept and its implementation in a single notebook.

| # | Session | Type | Kaggle |
|---|---|---|---|
| 16 | Calibration | Concept + Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-16-calibration) |
| 17 | Risk–Coverage Analysis | Concept + Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-17-risk-coverage-analysis/) |
| 18 | Out-of-Distribution Detection | Concept + Implementation | [open](https://www.kaggle.com/code/benyamingheiji/session-18-out-of-distribution-detection/) |

### 🧭 Part 4 — Future Directions · Session 19

How to choose a method for a real clinical problem, what is still unsolved, and where the
field is going.

| # | Session | Type | Kaggle |
|---|---|---|---|
| 19 | Final Summary & Future Directions | Summary | [open](https://www.kaggle.com/code/benyamingheiji/session-19-final-summary-future-directions) |

## 💡 What you'll take away

- Why accuracy alone is not enough in clinical AI, and how clinicians reason probabilistically
- The difference between **aleatoric** (data) and **epistemic** (model) uncertainty, and why
  it changes the clinical response
- Bayesian deep learning — variational inference and MC Dropout — alongside Deep Ensembles,
  Evidential Deep Learning, and Conformal Prediction with guaranteed coverage
- Calibration, risk–coverage trade-offs, and out-of-distribution detection
- Working PyTorch implementations of every method, on real data

## ✍️ Authors

<table>
  <tr>
    <td width="33%"></td>
    <td align="center" width="33%">
      <img src="docs/assets/authors/benyamin-gheiji.webp" width="120" alt="Benyamin Gheiji"><br>
      <b>Benyamin Gheiji</b><br>
      <sub><i>Course Author · Project Lead</i></sub><br>
      <sub>Medical Student, Medical Imaging AI Researcher</sub><br><br>
      <a href="https://benyamin-gheiji.github.io/">Website</a> ·
      <a href="https://scholar.google.com/citations?user=0Fdy24gAAAAJ&hl=en">Scholar</a> ·
      <a href="https://ir.linkedin.com/in/benyamin-gheiji-4a0668260">LinkedIn</a>
    </td>
    <td width="33%"></td>
  </tr>
</table>

<table>
  <tr>
    <td align="center" width="33%">
      <img src="docs/assets/authors/danial-elyassirad.webp" width="120" alt="Danial Elyassirad"><br>
      <b>Danial Elyassirad</b><br>
      <sub><i>Course Author</i></sub><br>
      <sub>Medical Doctor, Medical Imaging AI Researcher</sub><br><br>
      <a href="https://danialelyassirad.github.io/">Website</a> ·
      <a href="https://scholar.google.com/citations?user=RzDOvMwAAAAJ&hl=en">Scholar</a> ·
      <a href="https://ir.linkedin.com/in/danial-elyassirad">LinkedIn</a>
    </td>
    <td align="center" width="33%">
      <img src="docs/assets/authors/mahsa-vatanparast.webp" width="120" alt="Mahsa Vatanparast"><br>
      <b>Mahsa Vatanparast</b><br>
      <sub><i>Course Author</i></sub><br>
      <sub>Medical Doctor, Medical Imaging AI Researcher</sub><br><br>
      <a href="https://scholar.google.com/citations?user=rEmIJDIAAAAJ&hl=en">Scholar</a> ·
      <a href="https://ir.linkedin.com/in/mahsa-vatanparast-24314b2a7">LinkedIn</a>
    </td>
    <td align="center" width="33%">
      <img src="docs/assets/authors/meysam-tavakoli.webp" width="120" alt="Meysam Tavakoli"><br>
      <b>Meysam Tavakoli</b><br>
      <sub><i>Course Author</i></sub><br>
      <sub>PhD, Medical Physicist, Medical Imaging AI Researcher</sub><br><br>
      <a href="https://scholar.google.com/citations?user=2KruThAAAAAJ&hl=en">Scholar</a> ·
      <a href="https://www.linkedin.com/in/meysam-tavakoli-aa853228">LinkedIn</a>
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="33%"></td>
    <td align="center" width="33%">
      <img src="docs/assets/authors/shahriar-faghani.webp" width="120" alt="Shahriar Faghani"><br>
      <b>Shahriar Faghani</b><br>
      <sub><i>Content Supervisor</i></sub><br>
      <sub>Radiology Resident at the University of Pennsylvania<br>
      Adjunct Assistant Professor of Radiology at Mayo Clinic</sub><br><br>
      <a href="https://scholar.google.com/citations?user=6HV5eJAAAAAJ&hl=en">Scholar</a> ·
      <a href="https://www.linkedin.com/in/shahriar-faghani-7b468082">LinkedIn</a>
    </td>
    <td width="33%"></td>
  </tr>
</table>

## 🤝 Feedback and contributing

We would be glad to hear from you if you spot a problem anywhere in the tutorial — an error,
an unclear explanation, or something that simply does not run. You can reach us by opening a
[GitHub issue](https://github.com/benyamin-gheiji/Uncertainty-Quantification-Medical-Imaging/issues),
leaving a comment in the discussion section of the relevant Kaggle notebook, or emailing
**benyamingheiji@gmail.com** directly.

We would also be very happy to collaborate with anyone who would like to help expand this
work — whether that means extending it to segmentation, regression, or registration, adding
new methods, or improving what is already here.

⭐ And if you find the course useful, starring the repository, upvoting the Kaggle notebooks,
and passing it on to others goes a long way in helping it reach the people who need it.
