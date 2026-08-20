#!/usr/bin/env python3
"""
Static-site generator for the UQMI course (GitHub Pages).

Reads the course notebooks, converts each to HTML, and writes a complete
static site into ./docs — no Streamlit, no server, nothing to run at view time.

    python build.py                    # build into ./docs
    python build.py --serve            # build, then preview on localhost:8000

Notebooks are read from NOTEBOOK_DIR (see below). Images referenced by the
notebooks are copied into docs/assets/img/ and the <img> sources rewritten to
relative paths, so the published site is fully self-contained.
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter
from traitlets.config import Config
from pygments.formatters import HtmlFormatter

HERE = Path(__file__).parent

# The session notebooks live in this repository, in "session 01" … "session 19"
# folders alongside this script. Override with --notebooks if that ever changes.
DEFAULT_NOTEBOOK_DIR = HERE

OUT = HERE / "docs"

SITE_TITLE = "Uncertainty Quantification of Machine Learning Models in Medical Imaging"
SITE_SHORT = "UQMI"

AUTHORS = [
    ("BG", "Benyamin Gheiji", "Course Author"),
    ("DE", "Danial Elyassirad", "Course Author"),
    ("MV", "Mahsa Vatanparast", "Course Author"),
    ("SF", "Shahriar Faghani", "Content Supervisor"),
]

# ── Course structure ────────────────────────────────────────────────────────
# Conformal Prediction (13, 14) and the Part 2 Summary (15) belong to Part 2.
PARTS = [
    {
        "id": 1,
        "icon": "🌱",
        "name": "Foundations",
        "label": "Part 1 — Foundations",
        "range": "Sessions 1–3",
        "sessions": [1, 2, 3],
        "chips": ["Why UQ?", "Aleatoric vs Epistemic", "Clinical Practice"],
        "desc": "Clinical motivation, the two failure modes of AI (overconfidence and "
                "underconfidence), the two kinds of uncertainty, and how clinicians "
                "already reason probabilistically.",
    },
    {
        "id": 2,
        "icon": "⚙️",
        "name": "Core UQ Methods",
        "label": "Part 2 — Core UQ Methods",
        "range": "Sessions 4–15",
        "sessions": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "chips": ["Bayesian DL", "Variational Inference", "MC Dropout",
                  "Deep Ensembles", "Evidential DL", "Conformal Prediction"],
        "desc": "The methods themselves — Bayesian neural networks, variational "
                "inference, MC Dropout, Deep Ensembles, Evidential Deep Learning and "
                "Conformal Prediction. Each concept session is followed by a PyTorch "
                "implementation on real chest X-ray data.",
    },
    {
        "id": 3,
        "icon": "📐",
        "name": "Evaluation & Reliability",
        "label": "Part 3 — Evaluation & Reliability",
        "range": "Sessions 16–18",
        "sessions": [16, 17, 18],
        "chips": ["Calibration", "Risk–Coverage", "OOD Detection"],
        "desc": "Having produced uncertainty estimates, we ask whether they can be "
                "trusted: calibration, risk–coverage trade-offs, and detecting inputs "
                "that fall outside the training distribution.",
    },
    {
        "id": 4,
        "icon": "🧭",
        "name": "Future Directions",
        "label": "Part 4 — Future Directions",
        "range": "Session 19",
        "sessions": [19],
        "chips": ["Practical Guide", "Open Challenges", "What's Next"],
        "desc": "Pulling the pieces together: how to choose a method for a real "
                "clinical problem, what is still unsolved, and where the field is going.",
    },
]

SESSIONS = {
    1:  "Why Uncertainty Matters in Medicine",
    2:  "Aleatoric vs Epistemic Uncertainty",
    3:  "Uncertainty in Clinical Practice",
    4:  "The Bayesian Perspective",
    5:  "Variational Inference",
    6:  "Variational Inference — Implementation",
    7:  "MC Dropout",
    8:  "MC Dropout — Implementation",
    9:  "Deep Ensembles",
    10: "Deep Ensembles — Implementation",
    11: "Evidential Deep Learning",
    12: "Evidential Deep Learning — Implementation",
    13: "Conformal Prediction",
    14: "Conformal Prediction — Implementation",
    15: "Part 2 Summary",
    16: "Calibration",
    17: "Risk–Coverage Analysis",
    18: "Out-of-Distribution Detection",
    19: "Final Summary & Future Directions",
}

KAGGLE = {
    1:  "https://www.kaggle.com/code/benyamingheiji/session-1-why-uncertainty-matters-in-medicine",
    2:  "https://www.kaggle.com/code/benyamingheiji/session-2-aleatoric-vs-epistemic-uncertainty?scriptVersionId=343318282",
    3:  "https://www.kaggle.com/code/benyamingheiji/session-3-uncertainty-in-clinical-practice",
    4:  "https://www.kaggle.com/code/benyamingheiji/session-4-the-bayesian-perspective",
    5:  "https://www.kaggle.com/code/benyamingheiji/session-5-variational-inference/",
    6:  "https://www.kaggle.com/code/benyamingheiji/session-6-variational-inference-implementation/",
    7:  "https://www.kaggle.com/code/benyamingheiji/session-7-mc-dropout/",
    8:  "https://www.kaggle.com/code/benyamingheiji/session-8-mc-dropout-implementation/",
    9:  "https://www.kaggle.com/code/benyamingheiji/session-9-deep-ensembles/",
    10: "https://www.kaggle.com/code/benyamingheiji/session-10-deep-ensembles/",
    11: "https://www.kaggle.com/code/benyamingheiji/session-11-evidential-deep-learning/",
    12: "https://www.kaggle.com/code/benyamingheiji/session-12-edl-implementation/",
    13: "https://www.kaggle.com/code/benyamingheiji/session-13-conformal-prediction",
    14: "https://www.kaggle.com/code/benyamingheiji/session-14-conformal-prediction-implementation/",
    15: "https://www.kaggle.com/code/benyamingheiji/session-15-part-2-summary/",
    16: "https://www.kaggle.com/code/benyamingheiji/session-16-calibration",
    17: "https://www.kaggle.com/code/benyamingheiji/session-17-risk-coverage-analysis/",
    18: "https://www.kaggle.com/code/benyamingheiji/session-18-out-of-distribution-detection/",
    19: "https://www.kaggle.com/code/benyamingheiji/session-19-final-summary-future-directions",
}

# ── Part-page copy: what the part is about, plus a recap of the one before ──
PART_PAGES = {
    1: {
        "lede": "Before any mathematics, the clinical case: why a model that is always "
                "confident is a model you cannot safely deploy.",
        "recap": None,
        "body": [
            "Everything in this course rests on a single observation — accuracy tells you "
            "how often a model is right, but never when it is about to be wrong. In a "
            "clinic, those are completely different questions. A model with 95% accuracy "
            "that fails silently on the 5% is far more dangerous than one that flags its "
            "own uncertain cases for review.",
            "Part 1 builds that intuition before introducing a single equation. You will "
            "see the two ways clinical AI fails, learn to separate uncertainty that more "
            "data can fix from uncertainty that it cannot, and see how radiologists have "
            "always communicated confidence as part of their diagnostic output — the exact "
            "standard we want our models to meet.",
        ],
    },
    2: {
        "lede": "Now the methods themselves — six families of techniques for making a "
                "neural network say how sure it is, each with a hands-on implementation.",
        "recap": (
            "Part 1 — Foundations",
            "You built the case for uncertainty quantification: why accuracy alone is "
            "insufficient in a clinical setting, why confident errors are more dangerous "
            "than cautious ones, and how the softmax layer creates an illusion of "
            "confidence even on inputs the model has never seen anything like. You also "
            "separated aleatoric uncertainty — irreducible noise in the data — from "
            "epistemic uncertainty, which more data can reduce. That distinction decides "
            "the clinical response, and it drives every method that follows.",
        ),
        "body": [
            "This is the longest part of the course, and the heart of it. It opens with the "
            "Bayesian view of a neural network — treating weights as distributions rather "
            "than fixed numbers — and then works through the two practical approximations "
            "that make that idea tractable: variational inference and MC Dropout.",
            "Deep Ensembles arrive next by a completely different route. They make no "
            "Bayesian claims and require no special layers or loss functions: you simply "
            "train the same architecture several times from different random "
            "initializations and look at how much the members disagree. It is the simplest "
            "idea in this part and, on most benchmarks, one of the strongest.",
            "Two further methods take their own paths to the same goal. Evidential Deep "
            "Learning predicts a distribution over probabilities in a single forward pass, "
            "and Conformal Prediction steps outside all of these frames to give prediction "
            "sets with a coverage guarantee that holds without any assumption about your "
            "model.",
            "Every concept session is paired with an implementation session that builds the "
            "method in PyTorch on real chest X-ray data, so you finish with working code, "
            "not just intuition. The part closes with a summary session comparing all five "
            "approaches side by side.",
        ],
    },
    3: {
        "lede": "You can produce an uncertainty number for any input. This part asks the "
                "harder question — is that number telling you the truth?",
        "recap": (
            "Part 2 — Core UQ Methods",
            "You worked through the main families of uncertainty quantification and "
            "implemented each one: the Bayesian perspective on neural networks, "
            "variational inference, MC Dropout, Deep Ensembles, Evidential Deep Learning, "
            "and Conformal Prediction. You saw that Bayesian methods estimate uncertainty "
            "while Conformal Prediction guarantees coverage, and that ensembles remain a "
            "remarkably strong baseline despite making no Bayesian claims at all.",
        ),
        "body": [
            "A method that outputs an uncertainty score is not automatically useful. The "
            "score has to mean something — when a model says it is 80% confident, it should "
            "be right about 80% of the time. That property is calibration, and it has to be "
            "measured rather than assumed.",
            "Part 3 covers the evaluation toolkit: calibration metrics and reliability "
            "diagrams, risk–coverage analysis for deciding when a model should abstain and "
            "hand a case to a clinician, and out-of-distribution detection for recognizing "
            "inputs that lie outside the training distribution entirely. These are the "
            "checks that stand between a promising method and a deployable system.",
        ],
    },
    4: {
        "lede": "What to use, when to use it, and what the field still has not solved.",
        "recap": (
            "Part 3 — Evaluation & Reliability",
            "You learned to interrogate uncertainty estimates rather than trust them: "
            "measuring calibration with ECE and reliability diagrams, using risk–coverage "
            "curves to choose a sensible abstention threshold, and detecting "
            "out-of-distribution inputs. Together these turn an uncertainty number into "
            "evidence about whether a model can be relied upon in practice.",
        ),
        "body": [
            "The final part brings the whole course together. It compares every method you "
            "have implemented across the dimensions that actually matter for deployment — "
            "computational cost, ease of training, quality of the uncertainty estimates, and "
            "the strength of any guarantees — and offers practical guidance on choosing "
            "between them for a given clinical problem.",
            "It also looks forward honestly. Uncertainty quantification in medical imaging "
            "is an active research area with real open problems: scaling to foundation "
            "models, handling distribution shift between hospitals, and the still-unsettled "
            "question of how uncertainty should be communicated to the clinician who has to "
            "act on it.",
        ],
    },
}

HOME_AIM = (
    "This course is about a single, practical problem: how do you build a medical imaging "
    "model that knows when it might be wrong? Most machine learning teaching stops at "
    "accuracy, but a model deployed in a hospital needs to do more than be right most of "
    "the time — it needs to signal the cases where a clinician should look more carefully. "
    "We start from the clinical reasoning behind that idea, then work through the main "
    "techniques for quantifying uncertainty, implementing each one in PyTorch on real chest "
    "X-ray data, and finish by evaluating the uncertainty those methods produce — because an "
    "uncertainty estimate is only useful once you can show it is trustworthy. By the end you "
    "should be able to take an existing model, attach a well-founded uncertainty estimate to "
    "its predictions, check honestly whether that estimate can be trusted, and decide which "
    "method fits the problem in front of you."
)

PREREQS = [
    ("Python",
     "Comfortable writing and reading Python — functions, classes, NumPy arrays, and "
     "working in Jupyter notebooks."),
    ("Machine learning fundamentals",
     "Training and evaluation, over- and underfitting, train/validation/test splits, and "
     "metrics beyond raw accuracy."),
    ("Deep learning & PyTorch",
     "How neural networks are trained, plus enough PyTorch to define a model, write a "
     "training loop, and run inference."),
    ("Medical imaging data",
     "Some experience handling image datasets and an appreciation of the clinical stakes "
     "involved when a model is wrong."),
]

LEARN_ITEMS = [
    ("🩺", "Why accuracy alone is not enough in clinical AI, what uncertainty means for "
           "patient safety, and how clinicians already reason probabilistically"),
    ("🔬", "The difference between aleatoric (data) and epistemic (model) uncertainty — "
           "and why it changes the clinical response"),
    ("📐", "Bayesian deep learning — variational inference and MC Dropout — alongside Deep "
           "Ensembles, Evidential Deep Learning, and Conformal Prediction with guaranteed "
           "coverage"),
    ("🛠️", "Hands-on PyTorch implementations on real chest X-ray data throughout"),
    ("📊", "Calibration, risk–coverage trade-offs, and out-of-distribution detection"),
    ("🧭", "Where the field is heading — open challenges, distribution shift across "
           "hospitals, and how to choose a method for a real deployment"),
]

TOOLKIT = [
    ("🌱", "Foundations",
     "Clinical motivation, the cost of confident errors, aleatoric versus epistemic "
     "uncertainty, and the softmax illusion."),
    ("⚙️", "Core UQ Methods",
     "Bayesian methods (variational inference, MC Dropout), Deep Ensembles, Evidential "
     "Deep Learning, and Conformal Prediction."),
    ("📐", "Evaluation & Reliability",
     "Calibration and reliability diagrams, risk–coverage analysis, and "
     "out-of-distribution detection."),
    ("🧭", "Future Directions",
     "Choosing a method for a real clinical problem, open challenges, and where "
     "uncertainty quantification goes next."),
]


# ── Helpers ─────────────────────────────────────────────────────────────────
def part_of(sid: int) -> dict:
    return next(p for p in PARTS if sid in p["sessions"])


def session_url(sid: int) -> str:
    return f"session-{sid}.html"


def part_url(pid: int) -> str:
    return f"part-{pid}.html"


# Sessions that teach the concept and build it in the same notebook.
COMBINED = {16, 17, 18}


def session_tag(sid: int) -> str:
    t = SESSIONS[sid]
    if sid in COMBINED:
        return "Concept + Implementation"
    if "Implementation" in t:
        return "Implementation"
    if "Summary" in t:
        return "Summary"
    return "Concept"


def build_sequence() -> list[tuple[str, str, str]]:
    """Linear reading order: (url, kind, title)."""
    seq: list[tuple[str, str, str]] = []
    for p in PARTS:
        seq.append((part_url(p["id"]), "part", p["label"]))
        for sid in p["sessions"]:
            seq.append((session_url(sid), "session", f"Session {sid}: {SESSIONS[sid]}"))
    seq.append(("credits.html", "credits", "Congratulations & Credits"))
    return seq


SEQ = build_sequence()
SEQ_INDEX = {url: i for i, (url, _, _) in enumerate(SEQ)}


def neighbours(url: str):
    i = SEQ_INDEX[url]
    prev = SEQ[i - 1] if i > 0 else ("index.html", "home", "Home")
    nxt = SEQ[i + 1] if i < len(SEQ) - 1 else None
    return prev, nxt


# ── Shared chrome ───────────────────────────────────────────────────────────
def sidebar(active: str = "") -> str:
    out = [
        '<aside class="sidebar" id="sidebar">',
        '  <div class="sb-brand">',
        f'    <a class="sb-mark" href="index.html">🏥 {SITE_SHORT}</a>',
        '    <div class="sb-tagline">Uncertainty Quantification<br>in Medical Imaging</div>',
        '  </div>',
        '  <nav class="sb-nav">',
        f'    <a class="sb-home{" active" if active == "index.html" else ""}" '
        f'href="index.html">🏠 &nbsp;Home</a>',
    ]
    for p in PARTS:
        pu = part_url(p["id"])
        out.append('    <div class="sb-part">')
        out.append(f'      <a class="sb-part-label" href="{pu}">{p["icon"]} {p["label"]}</a>')
        for sid in p["sessions"]:
            cls = "sb-item active" if active == session_url(sid) else "sb-item"
            out.append(
                f'      <a class="{cls}" href="{session_url(sid)}">'
                f'<span class="n">{sid}</span><span>{html.escape(SESSIONS[sid])}</span></a>'
            )
        out.append('    </div>')

    cls = "sb-item active" if active == "credits.html" else "sb-item"
    out += [
        '    <div class="sb-part">',
        '      <span class="sb-part-label">🎉 Course Complete</span>',
        f'      <a class="{cls}" href="credits.html">'
        f'<span class="n">✦</span><span>Congratulations &amp; Credits</span></a>',
        '    </div>',
        '  </nav>',
        '  <div class="sb-foot">',
        '    <div class="sb-foot-label">Created by</div>',
        '    <div class="sb-foot-names">' + "<br>".join(n for _, n, _ in AUTHORS) + '</div>',
        '  </div>',
        '</aside>',
    ]
    return "\n".join(out)


def breadcrumb(items: list[tuple[str, str | None]]) -> str:
    """items: list of (label, href or None-for-current)."""
    parts = []
    for i, (label, href) in enumerate(items):
        if i:
            parts.append('<span class="sep">›</span>')
        if href:
            parts.append(f'<a href="{href}">{label}</a>')
        else:
            parts.append(f'<span class="here">{label}</span>')
    return f'<div class="crumb">{"".join(parts)}</div>'


def pagenav(url: str) -> str:
    prev, nxt = neighbours(url)
    cards = []
    if prev:
        cards.append(
            f'<a class="pagenav-card" href="{prev[0]}">'
            f'<div class="pn-label">← Previous</div>'
            f'<div class="pn-title">{html.escape(prev[2])}</div></a>'
        )
    else:
        cards.append('<div class="pagenav-card pagenav-empty"></div>')
    if nxt:
        cards.append(
            f'<a class="pagenav-card pagenav-next" href="{nxt[0]}">'
            f'<div class="pn-label">Next →</div>'
            f'<div class="pn-title">{html.escape(nxt[2])}</div></a>'
        )
    else:
        cards.append('<div class="pagenav-card pagenav-empty"></div>')
    return f'<nav class="pagenav">{"".join(cards)}</nav>'


MATHJAX = """
<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
    processEscapes: true
  },
  options: { skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code'] }
};
</script>
<script id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
"""

NAV_JS = """
<script>
(function () {
  var t = document.getElementById('navToggle');
  var s = document.getElementById('scrim');
  function close() { document.body.classList.remove('nav-open'); }
  if (t) t.addEventListener('click', function () {
    document.body.classList.toggle('nav-open');
  });
  if (s) s.addEventListener('click', close);
})();
</script>
"""


def page(title: str, body: str, active: str = "", extra_head: str = "") -> str:
    pyg = HtmlFormatter(style="monokai").get_style_defs(".nb .highlight")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(SITE_TITLE)} — a free, hands-on course.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@1,400;1,500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/style.css">
<style>
{pyg}
.nb .highlight {{ background: transparent !important; }}
.nb .highlight pre {{ background: transparent; }}
</style>
{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
<button class="sb-toggle" id="navToggle" aria-label="Toggle navigation">☰ Menu</button>
<div class="sb-scrim" id="scrim"></div>
<div class="shell">
{sidebar(active)}
<main class="main" id="main">
{body}
</main>
</div>
{MATHJAX}
{NAV_JS}
</body>
</html>
"""


def footer() -> str:
    names = " · ".join(n for _, n, _ in AUTHORS)
    return (f'<div class="foot"><span>{html.escape(SITE_SHORT)} — '
            f'{html.escape(SITE_TITLE)}</span><span>{html.escape(names)}</span></div>')


# ── Notebook rendering ──────────────────────────────────────────────────────
IMG_DIR = OUT / "assets" / "img"

# Images are authored at ~1500px but displayed at 700px. Re-encoding them to
# WebP at 2x display width cuts the published site from ~90 MB to a few MB.
OPTIMIZE = True
MAX_IMG_W = 1400
WEBP_Q = 86

try:
    from PIL import Image
except ImportError:                                    # optimisation is optional
    Image = None


def emit_image(src: Path, dest_dir: Path, stem: str) -> str:
    """Copy (and, when possible, shrink) one image. Returns the filename written."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    if OPTIMIZE and Image is not None and src.suffix.lower() in (".png", ".jpg", ".jpeg"):
        try:
            im = Image.open(src)
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                has_alpha = True
            else:
                im = im.convert("RGB")
                has_alpha = False
            if im.width > MAX_IMG_W:
                h = round(im.height * MAX_IMG_W / im.width)
                im = im.resize((MAX_IMG_W, h), Image.LANCZOS)
            name = stem + ".webp"
            im.save(dest_dir / name, "WEBP", quality=WEBP_Q,
                    method=6, lossless=has_alpha and im.width * im.height < 400_000)
            return name
        except Exception as e:                          # fall back to a plain copy
            print(f"      (image optimise failed for {src.name}: {e})")
    name = stem + src.suffix
    shutil.copy2(src, dest_dir / name)
    return name


def find_notebook(nb_root: Path, sid: int) -> Path | None:
    for folder in (nb_root / f"session {sid:02d}", nb_root / f"session{sid}"):
        if folder.is_dir():
            hits = sorted(folder.glob("*.ipynb"))
            if hits:
                return hits[0]
    hits = sorted(nb_root.glob(f"session*{sid}/*.ipynb"))
    return hits[0] if hits else None


def localise_images(html_src: str, sid: int, nb_dir: Path) -> tuple[str, int]:
    """Copy referenced images into docs/assets/img/sNN and rewrite the srcs."""
    dest = IMG_DIR / f"s{sid}"
    copied = 0

    def repl(m: re.Match) -> str:
        nonlocal copied
        pre, src, post = m.group(1), m.group(2), m.group(3)
        if src.startswith("data:"):
            return m.group(0)
        name = src.rsplit("/", 1)[-1].split("?")[0]
        name = re.sub(r"%20", " ", name)
        candidate = nb_dir / name
        if not candidate.exists():
            return m.group(0)
        stem = re.sub(r"[^A-Za-z0-9._-]", "_", Path(name).stem)
        written = emit_image(candidate, dest, stem)
        copied += 1
        return f'{pre}assets/img/s{sid}/{written}{post}'

    out = re.sub(r'(<img[^>]*?\ssrc=")([^"]+)(")', repl, html_src, flags=re.I)
    return out, copied


def render_notebook(nb_path: Path, sid: int) -> str:
    nb = nbformat.read(str(nb_path), as_version=4)

    cfg = Config()
    cfg.HTMLExporter.exclude_input_prompt = True
    cfg.HTMLExporter.exclude_output_prompt = True
    exporter = HTMLExporter(config=cfg, template_name="basic")
    body, _ = exporter.from_notebook_node(nb)

    body, n = localise_images(body, sid, nb_path.parent)
    print(f"      images localised: {n}")
    return body


# ── Pages ───────────────────────────────────────────────────────────────────
def build_home() -> str:
    learn = "".join(
        f'<div class="learn-item"><span class="ico">{ico}</span><span>{txt}</span></div>'
        for ico, txt in LEARN_ITEMS
    )

    prereqs = "".join(
        f'<div class="prereq-card"><span class="pq-num">{i:02d}</span>'
        f'<h3>{html.escape(name)}</h3><p>{html.escape(desc)}</p></div>'
        for i, (name, desc) in enumerate(PREREQS, start=1)
    )

    rows = []
    for p in PARTS:
        chips = "".join(f'<span class="chip">{html.escape(c)}</span>' for c in p["chips"])
        rows.append(f"""
<a class="part-row" href="{part_url(p['id'])}">
  <div class="part-row-top">
    <span class="part-num">Part {p['id']}</span>
    <span class="part-name">{p['icon']} {html.escape(p['name'])}</span>
    <span class="part-leader"></span>
    <span class="part-range">{html.escape(p['range'])}</span>
  </div>
  <p class="part-desc">{html.escape(p['desc'])}</p>
  <div class="chips">{chips}</div>
</a>""")

    body = f"""
<div class="wrap">
  <section class="hero">
    <div class="hero-eyebrow">🏥 A free, hands-on course in clinical machine learning</div>
    <h1>Uncertainty Quantification of Machine Learning Models in Medical Imaging</h1>
    <div class="hero-rule"></div>
    <p class="hero-sub">Teaching models to know what they don't know — from clinical
      motivation to working PyTorch code.</p>
    <div class="hero-stats">
      <div class="hero-stat"><span class="num">19</span><div class="lbl">Sessions</div></div>
      <div class="hero-stat"><span class="num">4</span><div class="lbl">Parts</div></div>
      <div class="hero-stat"><span class="num">Free</span><div class="lbl">Open Access</div></div>
    </div>
  </section>

  <div class="section-head"><h2>The aim</h2></div>
  <p class="aim">{HOME_AIM}</p>

  <div class="section-head"><h2>Prerequisites</h2></div>
  <div class="prereq-grid">{prereqs}</div>

  <div class="section-head"><h2>What you'll learn</h2></div>
  <div class="learn-grid">{learn}</div>

  <div class="section-head"><h2>Course outline</h2></div>
  <div class="outline">{"".join(rows)}</div>

  <div class="section-head"><h2>Get started</h2></div>
  <p class="prose" style="margin-top:-4px">Begin at the beginning, or jump to any session
     from the sidebar — each one stands on its own.</p>
  <a class="btn" href="{part_url(1)}">Start with Part 1 &nbsp;→</a>

  {footer()}
</div>
"""
    return page(SITE_TITLE, body, active="index.html")


def build_part(p: dict) -> str:
    meta = PART_PAGES[p["id"]]
    url = part_url(p["id"])

    crumb = breadcrumb([("🏠 Home", "index.html"), (html.escape(p["label"]), None)])

    recap_html = ""
    if meta["recap"]:
        rtitle, rtext = meta["recap"]
        recap_html = f"""
<div class="recap">
  <div class="recap-label">Where you've just been</div>
  <h3>{html.escape(rtitle)}</h3>
  <p>{html.escape(rtext)}</p>
</div>"""

    body_paras = "".join(f"<p>{html.escape(t)}</p>" for t in meta["body"])

    rows = []
    for sid in p["sessions"]:
        rows.append(f"""
<a class="sess-row" href="{session_url(sid)}">
  <span class="s-num">{sid:02d}</span>
  <span class="s-title">{html.escape(SESSIONS[sid])}</span>
  <span class="s-leader"></span>
  <span class="s-tag">{session_tag(sid)}</span>
</a>""")

    body = f"""
<div class="wrap">
  {crumb}
  <section class="part-hero">
    <div class="part-kicker">Part {p['id']} · {html.escape(p['range'])}</div>
    <h1>{p['icon']} {html.escape(p['name'])}</h1>
    <p class="lede">{html.escape(meta['lede'])}</p>
  </section>

  {recap_html}

  <div class="section-head"><h2>About this part</h2></div>
  <div class="prose">{body_paras}</div>

  <div class="section-head"><h2>Sessions in this part</h2></div>
  <div class="sess-index">{"".join(rows)}</div>

  {pagenav(url)}
  {footer()}
</div>
"""
    return page(f"{p['label']} — {SITE_SHORT}", body, active=url)


def build_session(sid: int, nb_html: str) -> str:
    p = part_of(sid)
    url = session_url(sid)
    crumb = breadcrumb([
        ("🏠 Home", "index.html"),
        (html.escape(p["label"]), part_url(p["id"])),
        (f"Session {sid}", None),
    ])
    kag = KAGGLE.get(sid)
    kaggle_box = ""
    if kag:
        kaggle_box = f"""
<a class="kaggle" href="{kag}" target="_blank" rel="noopener">
  <span class="k-ico">📓</span>
  <span class="k-txt">
    <span class="k-title">Open this session on Kaggle</span>
    <span class="k-sub">Run the notebook interactively — no local setup required</span>
  </span>
  <span class="k-arrow">↗</span>
</a>"""

    body = f"""
<div class="wrap">
  {crumb}
  {kaggle_box}
  <article class="nb">{nb_html}</article>
  {pagenav(url)}
  {footer()}
</div>
"""
    return page(f"Session {sid}: {SESSIONS[sid]} — {SITE_SHORT}", body, active=url)


def build_credits() -> str:
    crumb = breadcrumb([("🏠 Home", "index.html"), ("Congratulations & Credits", None)])

    toolkit = "".join(
        f'<div class="toolkit-card"><span class="tk-ico">{ico}</span>'
        f'<h3>{html.escape(name)}</h3><p>{html.escape(desc)}</p></div>'
        for ico, name, desc in TOOLKIT
    )
    team = "".join(
        f'<div class="team-card"><div class="team-avatar">{ini}</div>'
        f'<div class="team-name">{html.escape(name)}</div>'
        f'<div class="team-role">{html.escape(role)}</div></div>'
        for ini, name, role in AUTHORS
    )

    body = f"""
<div class="wrap">
  {crumb}
  <section class="closing-hero">
    <span class="cap">🎓</span>
    <h1>You've reached the end</h1>
    <p>Nineteen sessions ago you started with a simple, uncomfortable observation: a model
       that is always confident is a model you cannot safely put in front of a patient.
       Since then you have worked through the clinical reasoning behind uncertainty, the
       main methods for measuring it, and the tools for checking whether those measurements
       can actually be trusted.</p>
    <p>That is genuinely a lot of ground. Bayesian neural networks, variational inference,
       MC Dropout, Deep Ensembles, Evidential Deep Learning and Conformal Prediction are
       each substantial topics in their own right, and you have not just read about them —
       you have implemented them on real chest X-ray data and seen where each one helps and
       where it falls short.</p>
    <p>Take the habit with you rather than any single method. Ask what your model does not
       know, insist on evidence that its confidence is calibrated, and design for the cases
       it should hand back to a human. That instinct is what makes clinical AI trustworthy,
       and it will outlast whichever technique happens to be state of the art.</p>
  </section>

  <div class="section-head"><h2>What you learned</h2></div>
  <div class="toolkit-grid">{toolkit}</div>

  <div class="section-head"><h2>About the authors</h2></div>
  <div class="team-grid">{team}</div>

  {pagenav("credits.html")}
  {footer()}
</div>
"""
    return page(f"Congratulations & Credits — {SITE_SHORT}", body, active="credits.html")


# ── Main ────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notebooks", default=str(DEFAULT_NOTEBOOK_DIR),
                    help="directory containing the session folders")
    ap.add_argument("--skip-notebooks", action="store_true",
                    help="rebuild only home/part/credits pages (fast)")
    ap.add_argument("--serve", action="store_true", help="preview after building")
    ap.add_argument("--no-optimize", action="store_true",
                    help="copy images verbatim instead of re-encoding to WebP")
    args = ap.parse_args()

    global OPTIMIZE
    if args.no_optimize:
        OPTIMIZE = False

    nb_root = Path(args.notebooks)
    if not nb_root.is_dir():
        print(f"ERROR: notebook directory not found: {nb_root}")
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(parents=True, exist_ok=True)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    shutil.copy2(HERE / "site" / "style.css", OUT / "assets" / "style.css")

    print("building pages…")
    (OUT / "index.html").write_text(build_home(), encoding="utf-8")
    print("   index.html")
    for p in PARTS:
        (OUT / part_url(p["id"])).write_text(build_part(p), encoding="utf-8")
        print(f"   {part_url(p['id'])}")
    (OUT / "credits.html").write_text(build_credits(), encoding="utf-8")
    print("   credits.html")

    if not args.skip_notebooks:
        print("rendering notebooks…")
        missing = []
        for sid in sorted(SESSIONS):
            nb_path = find_notebook(nb_root, sid)
            if not nb_path:
                missing.append(sid)
                print(f"   !! session {sid}: notebook not found")
                continue
            print(f"   session {sid:>2}: {nb_path.name}")
            nb_html = render_notebook(nb_path, sid)
            (OUT / session_url(sid)).write_text(build_session(sid, nb_html), encoding="utf-8")
        if missing:
            print(f"\nWARNING: no notebook found for sessions {missing}")

    print(f"\ndone → {OUT}")

    if args.serve:
        import http.server, socketserver, functools, webbrowser
        handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                    directory=str(OUT))
        with socketserver.TCPServer(("", 8000), handler) as httpd:
            print("serving on http://localhost:8000  (ctrl-c to stop)")
            webbrowser.open("http://localhost:8000")
            httpd.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
