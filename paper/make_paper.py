"""Build the manuscript as a .docx, formatted for the Journal of Imaging
Informatics in Medicine (Springer).

Article type: Technical note / tutorial.
Required order: Abstract, Background, Methods, Results, Discussion, Conclusion,
Acknowledgements  (Introduction and Related Work are merged into Background).
References follow the journal's numbered style.
"""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"
OUT = HERE / "UQMI_paper_JIIM.docx"

CONTENT_W = 6.5
INK = RGBColor(0x11, 0x18, 0x27)
DARK = RGBColor(0x1F, 0x2A, 0x37)
GREY = RGBColor(0x37, 0x41, 0x51)
HEAD_FILL = "1F2A37"
ZEBRA_FILL = "F3F4F6"

doc = Document()

sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
sec.top_margin = sec.bottom_margin = Inches(1)
sec.left_margin = sec.right_margin = Inches(1)

normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(8)
normal.paragraph_format.line_spacing = 1.5      # journals expect 1.5/double

def force_font(style, face="Times New Roman"):
    """Word's Heading styles inherit a *theme* font, which silently overrides
    style.font.name. Pin the real face and strip the theme attributes."""
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("asciiTheme", "hAnsiTheme", "cstheme", "eastAsiaTheme"):
        if rFonts.get(qn("w:" + attr)) is not None:
            del rFonts.attrib[qn("w:" + attr)]
    for attr in ("ascii", "hAnsi", "cs"):
        rFonts.set(qn("w:" + attr), face)


for name, size, color in (("Heading 1", 13, INK), ("Heading 2", 11.5, DARK)):
    st = doc.styles[name]
    st.font.name = "Times New Roman"
    st.font.size = Pt(size)
    st.font.bold = True
    st.font.color.rgb = color
    st.paragraph_format.space_before = Pt(14)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.15
    force_font(st)


# ── helpers ────────────────────────────────────────────────────────────────
def para(text, *, size=None, italic=False, bold=False, align=None,
         color=None, after=None, line=None, font=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if line is not None:
        p.paragraph_format.line_spacing = line
    r = p.add_run(text)
    r.italic, r.bold = italic, bold
    if size:
        r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color
    if font:
        r.font.name = font
    return p


def runs_para(parts, *, align=None, after=None, line=None, size=None):
    """parts: list of (text, {'b':bold,'i':italic,'sup':superscript})"""
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    if line is not None:
        p.paragraph_format.line_spacing = line
    for t, o in parts:
        r = p.add_run(t)
        r.bold = o.get("b", False)
        r.italic = o.get("i", False)
        if o.get("sup"):
            r.font.superscript = True
        if size or o.get("size"):
            r.font.size = Pt(o.get("size", size))
    return p


def h1(t):
    return doc.add_heading(t, level=1)


def h2(t):
    return doc.add_heading(t, level=2)


def bullet(text):
    p = doc.add_paragraph(text, style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.5
    return p


def shade(cell, fill):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:color"), "auto")
    el.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(el)


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def dont_split(row):
    row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))


def table_caption(text):
    """Springer places table captions ABOVE the table."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.line_spacing = 1.15
    label, rest = text.split(" ", 2)[0] + " " + text.split(" ", 2)[1], text.split(" ", 2)[2]
    r = p.add_run(label + " ")
    r.bold = True
    r.font.size = Pt(9.5)
    r2 = p.add_run(rest)
    r2.font.size = Pt(9.5)
    return p


def fig_caption(text):
    """Springer places figure captions BELOW the figure."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.15
    label, rest = text.split(" ", 2)[0] + " " + text.split(" ", 2)[1], text.split(" ", 2)[2]
    r = p.add_run(label + " ")
    r.bold = True
    r.font.size = Pt(9.5)
    r2 = p.add_run(rest)
    r2.font.size = Pt(9.5)
    r2.font.color.rgb = GREY
    return p


def make_table(widths, header, rows, *, size=8.5, center_from=None):
    t = doc.add_table(rows=1, cols=len(widths))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False

    def fill_row(cells, values, *, head=False, zebra=False):
        for i, (c, v) in enumerate(zip(cells, values)):
            c.width = Inches(widths[i])
            if head:
                shade(c, HEAD_FILL)
            elif zebra:
                shade(c, ZEBRA_FILL)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            if center_from is not None and i >= center_from:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(v))
            r.font.size = Pt(size)
            r.font.name = "Times New Roman"
            r.bold = head
            if head:
                r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    fill_row(t.rows[0].cells, header, head=True)
    repeat_header(t.rows[0])
    dont_split(t.rows[0])
    for ri, row in enumerate(rows):
        r = t.add_row()
        fill_row(r.cells, row, zebra=(ri % 2 == 1))
        dont_split(r)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return t


def figure(file, caption_text, width=CONTENT_W):
    doc.add_picture(str(FIG / file), width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.paragraphs[-1].paragraph_format.space_before = Pt(10)
    doc.paragraphs[-1].paragraph_format.space_after = Pt(4)
    fig_caption(caption_text)


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ═══════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════════════
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.line_spacing = 1.15
r = p.add_run("Teaching Models to Know What They Do Not Know: An Open, Hands-On "
              "Tutorial on Uncertainty Quantification for Medical Imaging, with a "
              "Language-Model-Based Content Evaluation")
r.bold = True
r.font.size = Pt(15)
p.paragraph_format.space_after = Pt(12)

runs_para(
    [("Benyamin Gheiji", {}), ("1", {"sup": True}), (", Danial Elyassirad", {}),
     ("1", {"sup": True}), (", Mahsa Vatanparast", {}), ("1", {"sup": True}),
     (", Shahriar Faghani", {}), ("2", {"sup": True})],
    align=WD_ALIGN_PARAGRAPH.CENTER, after=8, line=1.15, size=11)

runs_para([("1", {"sup": True}),
           ("[Department, Institution, City, Country]", {"i": True})],
          align=WD_ALIGN_PARAGRAPH.CENTER, after=2, line=1.15, size=9.5)
runs_para([("2", {"sup": True}),
           ("[Department, Institution, City, State, Country]", {"i": True})],
          align=WD_ALIGN_PARAGRAPH.CENTER, after=10, line=1.15, size=9.5)

runs_para([("Corresponding author: ", {"b": True}),
           ("Benyamin Gheiji, [full postal address]. E-mail: [email]", {"i": True})],
          after=4, line=1.15, size=10)
runs_para([("ORCID: ", {"b": True}),
           ("B. Gheiji 0000-0000-0000-0000; D. Elyassirad 0000-0000-0000-0000; "
            "M. Vatanparast 0000-0000-0000-0000; S. Faghani 0000-0000-0000-0000",
            {"i": True})],
          after=16, line=1.15, size=10)

# ── Abstract (unstructured, 150–250 words) ─────────────────────────────────
h1("Abstract")
para("Machine learning models for medical imaging are conventionally judged by how often "
     "they are correct, yet a model that fails silently on the cases it has never "
     "encountered carries a different and larger clinical risk than one that flags those "
     "cases for review. Uncertainty quantification (UQ) supplies the tools to draw that "
     "distinction, but its literature is dispersed across primary methodological papers "
     "written for specialists, and comparatively little of it is executable, clinically "
     "framed, or sequenced for a newcomer. We present an open, hands-on tutorial on UQ for "
     "medical imaging comprising nineteen sessions in four parts, progressing from the "
     "clinical rationale through Bayesian and non-Bayesian methods to the evaluation of the "
     "uncertainty estimates themselves. Every method is implemented in PyTorch on a public "
     "chest radiograph dataset, and every session executes end to end on freely available "
     "hardware. We additionally propose a protocol for evaluating such a resource by "
     "treating it as a knowledge source for a large language model (LLM). One hundred "
     "four-option multiple-choice items were generated from the primary literature rather "
     "than from the tutorial, and twenty instruction-tuned LLMs spanning six families "
     "answered each item twice: unaided, and with passages retrieved from the tutorial. "
     "Access to the tutorial raised mean accuracy from 0.680 to 0.742 and mean area under "
     "the receiver operating characteristic curve for failure prediction from 0.725 to "
     "0.788, with eighteen of twenty models improving on each metric (Wilcoxon signed-rank, "
     "Holm-corrected P = 0.00032). All materials are publicly released.")

runs_para([("Keywords ", {"b": True}),
           ("Uncertainty quantification · Medical imaging · Deep learning · Conformal "
            "prediction · Model calibration · Education", {})],
          after=14, line=1.15)

# ── Statements and Declarations ────────────────────────────────────────────
h1("Statements and Declarations")
runs_para([("Funding ", {"b": True}),
           ("[The authors declare that no funds, grants, or other support were received "
            "during the preparation of this manuscript — amend if applicable.]", {"i": True})],
          after=6, line=1.15)
runs_para([("Competing Interests ", {"b": True}),
           ("The authors have no relevant financial or non-financial interests to "
            "disclose.", {})], after=6, line=1.15)
runs_para([("Author Contributions ", {"b": True}),
           ("[B.G., D.E. and M.V. designed and wrote the tutorial sessions and implemented "
            "the code. B.G. designed and ran the evaluation. S.F. supervised the content "
            "and reviewed the material for clinical accuracy. All authors read and approved "
            "the final manuscript — amend as appropriate.]", {"i": True})],
          after=6, line=1.15)
runs_para([("Ethics Approval ", {"b": True}),
           ("Not applicable. This work uses a publicly available, fully de-identified "
            "imaging dataset and involves no human participants or animal subjects.", {})],
          after=6, line=1.15)
runs_para([("Consent to Participate / Consent to Publish ", {"b": True}),
           ("Not applicable.", {})], after=6, line=1.15)
runs_para([("Data Availability ", {"b": True}),
           ("All tutorial notebooks, figures, evaluation code, and the complete item bank "
            "are publicly available at https://github.com/benyamin-gheiji/"
            "Uncertainty-Quantification-Medical-Imaging.", {})], after=6, line=1.15)

page_break()

# ═══════════════════════════════════════════════════════════════════════════
# BACKGROUND  (Introduction + Related Work merged, per journal structure)
# ═══════════════════════════════════════════════════════════════════════════
h1("Background")
para("Clinical machine learning is generally reported in terms of accuracy, area under the "
     "receiver operating characteristic curve (AUROC), or sensitivity and specificity at a "
     "chosen operating point. These quantities summarise how often a model is right across "
     "a population. They say nothing about the individual case in front of a clinician, and "
     "in particular nothing about whether the model has previously encountered anything "
     "resembling that case.")
para("The distinction matters because the two failure modes are not symmetric. A model that "
     "is uncertain and indicates as much invites a second read, an additional view, or a "
     "confirmatory test, at the cost of clinician time. A model that is confidently wrong "
     "invites none of these, and the error propagates into the decision. This asymmetry has "
     "been identified as a central obstacle to the safe deployment of machine-assisted "
     "decision making [1], and the manner in which model uncertainty is conveyed to the "
     "clinician who must act on it remains an open problem in its own right [2].")
para("The architecture of a standard classifier compounds the difficulty. A softmax output "
     "layer produces a normalised distribution over the training classes for any input "
     "whatsoever, including inputs drawn from a distribution the network has never seen, so "
     "the output continues to resemble a confident probability long after it has ceased to "
     "be a meaningful one. Modern networks are moreover systematically overconfident, a "
     "property that worsens with the capacity increases that otherwise improve accuracy [3].")
para("UQ is the body of work that addresses these problems, and it has developed along "
     "several partly independent lines. A foundational distinction separates aleatoric "
     "uncertainty, which arises from noise and ambiguity inherent in the data and cannot be "
     "reduced by acquiring more of it, from epistemic uncertainty, which reflects what the "
     "model has not learned and can be reduced [4]. Bayesian neural networks place "
     "distributions over weights and approximate the resulting posterior, either by "
     "variational inference (VI), which optimises a factorised approximation to that "
     "posterior [5], or by reinterpreting dropout at inference time as approximate Bayesian "
     "inference, an approach known as Monte Carlo (MC) dropout [6]. Deep Ensembles set the "
     "Bayesian machinery aside entirely and take the disagreement among independently "
     "initialized networks as the uncertainty signal, remaining a strong baseline despite "
     "making no Bayesian claims [7]. Evidential deep learning (EDL) predicts the parameters "
     "of a Dirichlet distribution over class probabilities in a single forward pass, "
     "separating the two components analytically rather than by sampling [8]. Conformal "
     "prediction (CP) takes a different route again, producing prediction sets that contain "
     "the true label with a specified marginal probability, guaranteed in finite samples "
     "under exchangeability alone and without assumptions about the underlying model "
     "[9, 10].")
para("A parallel line of work concerns whether uncertainty estimates deserve to be believed "
     "once produced. Calibration asks whether stated confidence matches observed frequency, "
     "and is measured by reliability diagrams and the expected calibration error (ECE) "
     "[3, 11]. Selective prediction and risk–coverage analysis formalise the decision to "
     "abstain and refer a case for human review [12]. Out-of-distribution (OOD) detection "
     "asks the prior question of whether an input belongs to the training distribution at "
     "all [13], and systematic evaluation under dataset shift has shown that methods "
     "performing comparably in distribution can diverge sharply once that assumption fails "
     "[14].")
para("Several reviews survey this territory, both for deep learning generally [15, 16] and "
     "for medical image analysis specifically [17]. Reviews serve a different purpose from "
     "the present work: they map a field for readers who already intend to enter it, and "
     "they do not generally supply executable implementations or a graded path for a "
     "newcomer. Educational resources that do supply code tend to cover a single method "
     "rather than the range, and are seldom framed around clinical decision-making. The "
     "result is that a practitioner who trains medical imaging models, and who wants their "
     "predictions to carry an honest measure of confidence, has no single path through this "
     "material that begins with the clinical problem and ends with working code.")
para("A second gap concerns how such a resource should be assessed. Tutorials and courses "
     "are conventionally evaluated by expert review or by studies with human learners, both "
     "of which are slow and costly. Retrieval-augmented generation [18] suggests a cheaper "
     "proxy: if a document is a good knowledge source, then supplying it to a language "
     "model should improve that model's answers to questions about its subject matter. We "
     "adopt this as a content-coverage probe rather than as a claim about human learning.")
para("This paper describes such a tutorial and then asks whether it works. Our "
     "contributions are:")
bullet("An open tutorial of nineteen sessions covering the main families of UQ for medical "
       "image classification, in which every method is implemented in PyTorch on a public "
       "chest radiograph dataset and every notebook runs on freely available hardware.")
bullet("A pedagogical structure in which conceptual sessions are paired with implementation "
       "sessions, and in which the final part is devoted not to producing uncertainty "
       "estimates but to establishing whether they can be trusted.")
bullet("A protocol for evaluating an educational resource by treating it as a knowledge "
       "source for a large language model (LLM), measuring both answer accuracy and the "
       "model's ability to predict its own failures, with the item bank generated from the "
       "primary literature rather than from the tutorial.")
bullet("An empirical result across twenty LLMs spanning six families showing that supplying "
       "the tutorial improves both quantities.")

# ═══════════════════════════════════════════════════════════════════════════
# METHODS
# ═══════════════════════════════════════════════════════════════════════════
h1("Methods")

h2("Tutorial Scope and Intended Audience")
para("The tutorial is aimed at researchers and practitioners who already build models for "
     "medical imaging and want their predictions to carry a defensible measure of "
     "confidence. It assumes no prior exposure to Bayesian deep learning or CP, but it does "
     "assume the background summarised in Table 1.")
table_caption("Table 1 Assumed background of the intended reader.")
make_table(
    [1.8, 4.7],
    ["Prerequisite", "What is assumed"],
    [
        ["Python", "Functions, classes, NumPy arrays, and working in Jupyter notebooks."],
        ["Machine learning fundamentals",
         "Training and evaluation, over- and underfitting, data splits, and metrics beyond "
         "raw accuracy."],
        ["Deep learning and PyTorch",
         "How neural networks are trained, plus enough PyTorch to define a model, write a "
         "training loop, and run inference."],
        ["Medical imaging data",
         "Some experience handling image datasets, and an appreciation of the clinical "
         "stakes when a model is wrong."],
    ],
)

h2("Curriculum Structure")
para("The material is arranged as nineteen sessions in four parts (Table 2). The ordering "
     "is deliberate: the clinical argument comes first, and no method is introduced until "
     "the problem it solves has been made concrete; the methods follow; and the final part "
     "is concerned entirely with whether the resulting estimates deserve to be believed.")
table_caption("Table 2 Structure of the tutorial. UQ uncertainty quantification, MC Monte "
              "Carlo.")
make_table(
    [1.35, 0.85, 4.3],
    ["Part", "Sessions", "Focus"],
    [
        ["Part 1 — Foundations", "1–3",
         "Why accuracy alone is insufficient in clinical artificial intelligence; aleatoric "
         "versus epistemic uncertainty; how clinicians already reason probabilistically."],
        ["Part 2 — Core UQ Methods", "4–15",
         "The Bayesian perspective; variational inference; MC dropout; Deep Ensembles; "
         "evidential deep learning; conformal prediction. Each concept session is paired "
         "with a PyTorch implementation, and the part closes with a side-by-side comparison."],
        ["Part 3 — Evaluation and Reliability", "16–18",
         "Calibration and reliability diagrams; risk–coverage analysis and selective "
         "prediction; out-of-distribution detection. All three combine concept and "
         "implementation in one notebook."],
        ["Part 4 — Future Directions", "19",
         "Choosing a method for a clinical problem; open challenges; directions for the "
         "field."],
    ],
)
para("Within Part 2, each conceptual session is followed by an implementation session that "
     "builds the method from scratch on the same dataset and the same backbone, so that "
     "differences between methods are attributable to the methods themselves rather than to "
     "differences in experimental setup. Part 3 combines concept and implementation within "
     "single notebooks, because the evaluation techniques are shorter and are best "
     "understood against outputs from the methods already constructed.")

h2("Implementation and Delivery")
para("All implementation sessions use the same publicly available paediatric chest "
     "radiograph dataset [19] and a DenseNet-121 backbone [20], implemented in PyTorch [21], "
     "with the classification head trained and the backbone frozen where the computational "
     "budget requires it. This is constrained by a deliberate design decision: every "
     "notebook must run to completion on the free graphics processing unit (GPU) tier of a "
     "hosted notebook service, so that no part of the tutorial is inaccessible to a reader "
     "without institutional computing resources.")
para("The material is released in three forms. The Jupyter notebooks and their figures are "
     "held in a public repository. Each session is additionally published as a Kaggle "
     "notebook, executable in the browser with the dataset already attached. A static "
     "website renders every session with navigation between parts and sessions for readers "
     "who prefer to read rather than run.")

h2("Evaluation Design")
para("The evaluation treats the tutorial as a knowledge source and asks whether making it "
     "available to an LLM improves that model's answers to questions about UQ. It is a "
     "content-coverage probe: it tests whether the tutorial contains the relevant "
     "information in a form that can be located and used. It is not a measure of human "
     "learning outcomes.")
para("Two outcomes were measured. Accuracy is whether the model selected the correct "
     "option. AUROC is whether the probability the model assigned to the option it chose "
     "separates its correct from its incorrect answers; this measures failure prediction, "
     "which accuracy does not imply. A model may become more accurate while its confidence "
     "becomes less informative about which of its answers to trust. Measuring both is a "
     "deliberate echo of the argument the tutorial itself makes.")

h2("Question Bank")
para("One hundred four-option multiple-choice items were generated with Claude Opus 5 in "
     "four categories of twenty-five items each: recall items covering definitions, "
     "mechanisms, and the operation of specific methods; conceptual items requiring the "
     "integration of two or more ideas; counterintuitive items in which common intuition "
     "yields the wrong answer, with that intuition present among the distractors; and "
     "applied items concerning clinical deployment, including threshold selection, "
     "abstention policies, external validation, acquisition shift, inference-time compute, "
     "and the communication of uncertainty to clinicians.")
para("Items were generated from the primary methodological literature rather than from the "
     "tutorial, so as to avoid the circularity of testing a text against questions derived "
     "from itself. The generation prompt named the source works explicitly [3–14].")
para("The prompt further imposed construction constraints intended to prevent the answer "
     "being inferable from surface features: exactly one unambiguously correct option; "
     "distractors defensible as incorrect for an identifiable reason, being a documented "
     "misconception, a conflated adjacent concept, or a true statement that does not answer "
     "the question; option lengths within approximately fifteen per cent of one another "
     "within each item, achieved by expanding distractors rather than abbreviating the "
     "correct option; no hedging qualifiers or absolute quantifiers confined to incorrect "
     "options; self-contained stems posing a specific question; no two items assessing the "
     "same fact; and, where the subject matter permitted, a concrete imaging context. The "
     "full prompt is reproduced in the Appendix.")

h2("Retrieval")
para("The tutorial condition supplied context by retrieval rather than as full text, since "
     "nineteen notebooks exceed the context window of the smaller models. The notebooks "
     "were flattened to text, with markdown as written and code fenced, then split on "
     "markdown headings and packed into chunks of approximately four hundred tokens, "
     "splitting oversized units on sentence boundaries so that no chunk begins or ends "
     "mid-sentence. One structural unit of overlap was carried between consecutive chunks.")
para("Chunks were embedded with BAAI/bge-large-en-v1.5 [22] and indexed with FAISS [23] "
     "using inner-product search over L2-normalised vectors. The embedding model is trained "
     "asymmetrically, so its query instruction prefix was applied to queries only and never "
     "to passages. Each query consisted of the item stem concatenated with all four "
     "options, and the top five chunks were retrieved. Retrieval was computed once and "
     "cached, so identical context was supplied to every model; retrieval variation "
     "therefore cannot contribute to any difference between conditions.")

h2("Models and Scoring")
para("Twenty instruction-tuned LLMs across six families were evaluated (Table 3), loaded in "
     "4-bit NF4 quantisation with double quantisation [24].")
table_caption("Table 3 Language models evaluated. All models are instruction-tuned variants.")
make_table(
    [1.25, 5.25],
    ["Family", "Models"],
    [
        ["Qwen2.5", "0.5B, 1.5B, 3B, 7B, 14B"],
        ["Falcon3", "1B, 3B, 7B, 10B"],
        ["Phi", "Phi-3-mini (3.8B), Phi-3.5-mini (3.8B), Phi-4-mini (3.8B), "
                "Phi-3-medium (14B)"],
        ["Mistral", "Mistral-7B-v0.3, Ministral-8B, Mistral-Nemo (12B)"],
        ["Granite 3.1", "2B, 8B"],
        ["Gemma 3", "1B, 4B"],
    ],
)
para("Each model answered all one hundred items twice: once with the question alone, and "
     "once with the retrieved passages prepended. Option order was shuffled once per item "
     "with a fixed seed and held identical across models and conditions.")
para("The answer was read from the model's logits at the first position after the "
     "generation prompt, taking the maximum logit across the plausible token forms of each "
     "letter, since tokenizers differ in whether a leading space is emitted, and applying a "
     "softmax across the four letters. Scoring is therefore deterministic: there is no "
     "sampling, no text parsing, and no model acting as judge. The confidence score used "
     "for AUROC is the probability assigned to the predicted letter; the probability on the "
     "correct letter would be circular, since it is high precisely when the model is right.")

h2("Statistical Analysis")
para("The model is the unit of analysis. Each model contributes one paired observation per "
     "metric, so the tests make no assumption that questions are independent: a question "
     "answered by twenty models yields twenty correlated observations, not twenty "
     "independent ones. Paired differences were tested with the two-sided Wilcoxon "
     "signed-rank test [25], with Holm correction applied across the two metrics [26]. "
     "P values below 0.05 were considered significant.")

# ═══════════════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════════════
h1("Results")

h2("Tutorial Content and Representative Outputs")
para("Part 1 builds the clinical argument before introducing any mathematics. It separates "
     "the two ways a clinical model fails, confident error and indiscriminate caution, and "
     "argues that the first is the more dangerous because it is invisible. It then develops "
     "the aleatoric–epistemic distinction that organises everything afterwards, and closes "
     "by observing that clinicians already reason in these terms, reporting a likelihood, a "
     "confidence, a differential, and a recommended action rather than a bare label.")
para("Part 2 opens with the Bayesian view of a neural network, treating weights as "
     "distributions rather than fixed values, and works through the two approximations that "
     "make this tractable in practice, VI and MC dropout. Deep Ensembles arrive by a "
     "different route, requiring no special layers or loss functions: the same architecture "
     "is trained several times from different random initializations, and the disagreement "
     "among members is the uncertainty signal. EDL and CP follow, each taking its own path "
     "to the same goal. Every method is instrumented identically, so that the resulting "
     "quantities can be compared directly (Fig. 1).")
figure("uncertainty_decomposition_ensembles.png",
       "Fig. 1 Uncertainty decomposition produced by the Deep Ensembles implementation "
       "session. a Distribution of total predictive entropy across the test set. b "
       "Epistemic (mutual information) and aleatoric components per case, sorted by total "
       "uncertainty. c Predictive entropy against mean predicted probability, with "
       "incorrect predictions marked; errors concentrate in the high-entropy region.")
para("Part 3 addresses whether these quantities can be trusted. Calibration asks whether "
     "stated confidence matches observed frequency: among cases assigned 80% confidence, "
     "approximately 80% should be correct. The session measures this with reliability "
     "diagrams and ECE, and applies temperature scaling as a post-hoc correction (Fig. 2).")
figure("calibration_temperature_scaling.png",
       "Fig. 2 Reliability diagrams for four methods before (top row) and after (bottom "
       "row) temperature scaling. Expected calibration error falls for every method; the "
       "fitted temperatures below one indicate that the uncorrected models were "
       "overconfident. VI variational inference, EDL evidential deep learning.")
para("Risk–coverage analysis addresses the operational question of when a model should "
     "decline to predict. Ordering cases by uncertainty and progressively abstaining on the "
     "least certain traces out a curve of error rate against the fraction of cases "
     "retained; the area under that curve summarises the quality of the uncertainty ranking "
     "independently of any particular threshold (Fig. 3). This connects an abstract "
     "quantity to a deployment decision: what accuracy is achievable if a given share of "
     "cases is referred for human review.")
figure("risk_coverage_all_methods.png",
       "Fig. 3 Risk–coverage curves for the four probabilistic methods, with clinically "
       "motivated coverage targets marked. a Risk against coverage. b Area under the "
       "risk–coverage curve by method, where lower is better.")
para("OOD detection asks whether an input belongs to the training distribution at all. The "
     "session constructs corrupted and transformed radiographs as a controlled OOD set and "
     "evaluates how well each method's uncertainty score separates them from held-out "
     "in-distribution cases (Fig. 4). The results are instructive precisely because they "
     "are uneven: methods performing comparably on calibration or selective prediction do "
     "not necessarily separate distribution shift equally well. Figure 5 shows the "
     "qualitative counterpart, which is the form in which such behaviour would be "
     "encountered in practice.")
figure("ood_roc_all_methods.png",
       "Fig. 4 Out-of-distribution (OOD) detection across all five methods. a Receiver "
       "operating characteristic curves for separating in-distribution from OOD inputs "
       "using each method's uncertainty score. b Mean uncertainty assigned to each group, "
       "where a larger gap indicates better separation. CP conformal prediction.")
figure("ood_qualitative.png",
       "Fig. 5 Qualitative out-of-distribution analysis. Top row: in-distribution "
       "radiographs receiving the lowest uncertainty. Bottom row: out-of-distribution "
       "inputs, produced by rotation, noise, and intensity corruption, receiving the "
       "highest.")
para("Part 4 compares the methods across the dimensions that determine which to use in "
     "practice, namely computational cost at training and inference, intrusiveness to an "
     "existing pipeline, quality of the resulting estimates, and the strength of any "
     "guarantee, and sets out the open problems.")

h2("Language-Model Evaluation")
para("Accuracy improved in eighteen of twenty models, and AUROC in eighteen of twenty "
     "(Table 4, Fig. 6).")
table_caption("Table 4 Paired comparison across twenty language models. Chance accuracy is "
              "0.25; an AUROC of 0.5 indicates confidence carrying no information about "
              "correctness. AUROC area under the receiver operating characteristic curve.")
make_table(
    [1.0, 0.5, 0.85, 0.8, 0.85, 0.9, 0.8, 0.8],
    ["Metric", "n", "No context", "Tutorial", "Mean diff.", "Median diff.", "P",
     "P (Holm)"],
    [
        ["Accuracy", "20", "0.680", "0.742", "+0.062", "+0.070", "0.00016", "0.00032"],
        ["AUROC", "20", "0.725", "0.788", "+0.063", "+0.069", "0.00026", "0.00032"],
    ],
    center_from=1,
)
figure("results_paired.png",
       "Fig. 6 Per-model paired differences between the no-context and tutorial conditions, "
       "coloured by model family. Each thin line is one model; the heavy black line is the "
       "mean. a Accuracy. b Area under the receiver operating characteristic curve for "
       "failure prediction.")
para("The two exceptions on accuracy were Qwen2.5-7B and Qwen2.5-14B, which scored 0.88 and "
     "0.93 without context and each lost a single item with it, a pattern consistent with a "
     "ceiling effect rather than with interference. Both nonetheless gained on AUROC, by "
     "0.022 and 0.172 respectively. Across the set, accuracy gains were largest in the "
     "mid-range models and compressed at both ends: the weakest models remained near the "
     "floor in both conditions, while the strongest had little headroom. Per-model results "
     "are given in Table 5.")
table_caption("Table 5 Per-model results. Acc accuracy, ctx context, AUROC area under the "
              "receiver operating characteristic curve.")
make_table(
    [1.4, 0.75, 0.72, 0.72, 0.72, 0.73, 0.73, 0.73],
    ["Model", "Family", "Acc. no ctx", "Acc. tutorial", "Δ Acc.",
     "AUROC no ctx", "AUROC tut.", "Δ AUROC"],
    [
        ["Qwen2.5-0.5B", "Qwen2.5", "0.38", "0.39", "+0.01", "0.593", "0.635", "+0.042"],
        ["Qwen2.5-1.5B", "Qwen2.5", "0.55", "0.63", "+0.08", "0.685", "0.787", "+0.102"],
        ["Qwen2.5-3B", "Qwen2.5", "0.80", "0.84", "+0.04", "0.699", "0.800", "+0.101"],
        ["Qwen2.5-7B", "Qwen2.5", "0.88", "0.87", "−0.01", "0.856", "0.878", "+0.022"],
        ["Qwen2.5-14B", "Qwen2.5", "0.93", "0.92", "−0.01", "0.667", "0.840", "+0.172"],
        ["Falcon3-1B", "Falcon3", "0.35", "0.45", "+0.10", "0.616", "0.710", "+0.094"],
        ["Falcon3-3B", "Falcon3", "0.64", "0.67", "+0.03", "0.742", "0.752", "+0.010"],
        ["Falcon3-7B", "Falcon3", "0.84", "0.89", "+0.05", "0.763", "0.820", "+0.057"],
        ["Falcon3-10B", "Falcon3", "0.86", "0.89", "+0.03", "0.859", "0.848", "−0.011"],
        ["Phi-3-mini", "Phi", "0.69", "0.79", "+0.10", "0.783", "0.866", "+0.083"],
        ["Phi-3.5-mini", "Phi", "0.70", "0.82", "+0.12", "0.752", "0.782", "+0.030"],
        ["Phi-4-mini", "Phi", "0.76", "0.83", "+0.07", "0.828", "0.734", "−0.094"],
        ["Phi-3-medium", "Phi", "0.81", "0.89", "+0.08", "0.832", "0.859", "+0.027"],
        ["Mistral-7B-v0.3", "Mistral", "0.64", "0.75", "+0.11", "0.784", "0.813", "+0.030"],
        ["Ministral-8B", "Mistral", "0.74", "0.84", "+0.10", "0.766", "0.855", "+0.089"],
        ["Mistral-Nemo", "Mistral", "0.76", "0.78", "+0.02", "0.705", "0.854", "+0.150"],
        ["Granite-3.1-2B", "Granite", "0.56", "0.68", "+0.12", "0.724", "0.820", "+0.096"],
        ["Granite-3.1-8B", "Granite", "0.79", "0.86", "+0.07", "0.699", "0.737", "+0.038"],
        ["gemma-3-1b", "Gemma 3", "0.31", "0.34", "+0.03", "0.548", "0.629", "+0.081"],
        ["gemma-3-4b", "Gemma 3", "0.60", "0.70", "+0.10", "0.608", "0.744", "+0.137"],
    ],
    size=8,
    center_from=2,
)

# ═══════════════════════════════════════════════════════════════════════════
# DISCUSSION
# ═══════════════════════════════════════════════════════════════════════════
h1("Discussion")
para("The evaluation supports a narrow claim: the tutorial contains information relevant to "
     "questions drawn from the primary literature, in a form that a retrieval system can "
     "locate and an LLM can use. Because the items were written from the source papers "
     "rather than from the tutorial, this is not a test of whether the tutorial can "
     "reproduce its own contents.")
para("The pattern of gains is informative about where such a resource helps. The models "
     "that improved most were those with sufficient capacity to exploit the retrieved text "
     "but insufficient parametric knowledge of the field to answer without it. Models at the "
     "ceiling gained little on accuracy because there was little to gain; models near the "
     "floor gained little because they could not exploit the context. That the strongest "
     "models nonetheless improved on failure prediction suggests that supplying relevant "
     "material affects the confidence attached to an answer separately from the answer "
     "itself.")
para("The dissociation between the two metrics deserves emphasis. Qwen2.5-14B is the "
     "clearest case: its accuracy did not improve, yet its AUROC rose by 0.172, meaning "
     "that the tutorial changed how informative its confidence was about its own errors "
     "without changing how many errors it made. Since the capacity to flag one's own "
     "failures is precisely what the tutorial argues matters clinically, this is not a "
     "secondary observation. The evaluation is in this sense deliberately reflexive: a "
     "resource arguing that a model should be judged not only on whether it is right but on "
     "whether it knows when it is wrong is assessed here on both counts.")

h2("Limitations")
para("The tutorial is preliminary. It is designed to bring a reader from no background in "
     "UQ to working implementations of the main methods, and that objective trades depth "
     "for coverage. Each method is presented with enough theory to justify the "
     "implementation and enough implementation to make the theory concrete, but none is "
     "treated to the depth of its primary literature; readers intending to work on these "
     "methods rather than with them should treat the tutorial as an entry point and the "
     "cited sources as the substance.")
para("The scope is restricted to classification. Every implementation session addresses a "
     "binary classification task on chest radiographs, and while the concepts transfer, the "
     "implementations do not directly. Segmentation raises the question of what an "
     "uncertainty map means at the pixel and structure level; regression requires "
     "distributional rather than categorical treatment; registration and image "
     "reconstruction raise their own formulations. We intend to extend the tutorial to "
     "these settings.")
para("The evaluation measures recognition rather than generation. A multiple-choice format "
     "establishes whether a model can identify a correct statement, not whether it can "
     "produce the underlying reasoning or apply it to a case.")
para("LLM performance is a proxy for content quality. An improvement in model answers "
     "indicates that the tutorial contains locatable, usable information; it is not "
     "evidence about human learning, for which a study with human participants would be "
     "required.")
para("Retrieval is confounded with content. An item for which the relevant session is never "
     "retrieved cannot benefit from the tutorial however well that session is written, so "
     "the measured gains reflect the combination of content quality and retrievability "
     "rather than content quality alone.")
para("The item bank was generated by a language model. Items were produced by Claude Opus 5 "
     "from the primary literature and are released with the evaluation code so that they "
     "can be independently inspected.")

# ═══════════════════════════════════════════════════════════════════════════
# CONCLUSION
# ═══════════════════════════════════════════════════════════════════════════
h1("Conclusion")
para("We have presented an open tutorial on UQ for medical imaging that proceeds from the "
     "clinical case for uncertainty, through the main methodological families, to the "
     "evaluation of the resulting estimates, with every method implemented on public data "
     "and every notebook runnable on freely available hardware. We have also proposed and "
     "applied a protocol for evaluating such a resource by treating it as a knowledge "
     "source for an LLM and measuring both answer accuracy and the model's ability to "
     "anticipate its own errors. Across twenty models spanning six families, supplying the "
     "tutorial improved both. The protocol is not specific to this subject matter and may "
     "prove useful for evaluating technical educational resources more generally.")

h1("Acknowledgements")
para("[Acknowledgements to be completed by the authors.]", italic=True)

# ═══════════════════════════════════════════════════════════════════════════
# REFERENCES
# ═══════════════════════════════════════════════════════════════════════════
page_break()
h1("References")

REFS = [
    "Begoli E, Bhattacharya T, Kusnezov D: The need for uncertainty quantification in "
    "machine-assisted medical decision making. Nat Mach Intell 1:20-23, 2019",

    "Kompa B, Snoek J, Beam AL: Second opinion needed: communicating uncertainty in medical "
    "machine learning. NPJ Digit Med 4:4, 2021",

    "Guo C, Pleiss G, Sun Y, Weinberger KQ: On calibration of modern neural networks. In: "
    "Proceedings of the 34th International Conference on Machine Learning, PMLR 70:1321-1330, "
    "2017",

    "Kendall A, Gal Y: What uncertainties do we need in Bayesian deep learning for computer "
    "vision? In: Advances in Neural Information Processing Systems 30, 2017",

    "Blundell C, Cornebise J, Kavukcuoglu K, Wierstra D: Weight uncertainty in neural "
    "networks. In: Proceedings of the 32nd International Conference on Machine Learning, "
    "PMLR 37:1613-1622, 2015",

    "Gal Y, Ghahramani Z: Dropout as a Bayesian approximation: representing model "
    "uncertainty in deep learning. In: Proceedings of the 33rd International Conference on "
    "Machine Learning, PMLR 48:1050-1059, 2016",

    "Lakshminarayanan B, Pritzel A, Blundell C: Simple and scalable predictive uncertainty "
    "estimation using deep ensembles. In: Advances in Neural Information Processing Systems "
    "30, 2017",

    "Sensoy M, Kaplan L, Kandemir M: Evidential deep learning to quantify classification "
    "uncertainty. In: Advances in Neural Information Processing Systems 31, 2018",

    "Vovk V, Gammerman A, Shafer G: Algorithmic Learning in a Random World, New York: "
    "Springer, 2005",

    "Angelopoulos AN, Bates S: A gentle introduction to conformal prediction and "
    "distribution-free uncertainty quantification. arXiv:2107.07511, 2021",

    "Naeini MP, Cooper GF, Hauskrecht M: Obtaining well calibrated probabilities using "
    "Bayesian binning. In: Proceedings of the AAAI Conference on Artificial Intelligence "
    "29:2901-2907, 2015",

    "Geifman Y, El-Yaniv R: Selective classification for deep neural networks. In: Advances "
    "in Neural Information Processing Systems 30, 2017",

    "Hendrycks D, Gimpel K: A baseline for detecting misclassified and out-of-distribution "
    "examples in neural networks. In: International Conference on Learning Representations, "
    "2017",

    "Ovadia Y, Fertig E, Ren J, Nado Z, Sculley D, Nowozin S, Dillon JV, Lakshminarayanan B, "
    "Snoek J: Can you trust your model's uncertainty? Evaluating predictive uncertainty "
    "under dataset shift. In: Advances in Neural Information Processing Systems 32, 2019",

    "Abdar M, Pourpanah F, Hussain S, Rezazadegan D, Liu L, Ghavamzadeh M, Fieguth P, Cao X, "
    "Khosravi A, Acharya UR, Makarenkov V, Nahavandi S: A review of uncertainty "
    "quantification in deep learning: techniques, applications and challenges. Inf Fusion "
    "76:243-297, 2021",

    "Gawlikowski J, Tassi CRN, Ali M, Lee J, Humt M, Feng J, Kruspe A, Triebel R, Jung P, "
    "Roscher R, Shahzad M, Yang W, Bamler R, Zhu XX: A survey of uncertainty in deep neural "
    "networks. Artif Intell Rev 56:1513-1589, 2023",

    "Lambert B, Forbes F, Doyle S, Dehaene H, Dojat M: Trustworthy clinical AI solutions: a "
    "unified review of uncertainty quantification in deep learning models for medical image "
    "analysis. Artif Intell Med 150:102830, 2024",

    "Lewis P, Perez E, Piktus A, Petroni F, Karpukhin V, Goyal N, Küttler H, Lewis M, Yih "
    "W, Rocktäschel T, Riedel S, Kiela D: Retrieval-augmented generation for "
    "knowledge-intensive NLP tasks. In: Advances in Neural Information Processing Systems "
    "33, 2020",

    "Kermany DS, Goldbaum M, Cai W, Valentim CCS, Liang H, Baxter SL, McKeown A, Yang G, Wu "
    "X, Yan F, Dong J, Prasadha MK, Pei J, Ting MYL, Zhu J, Li C, Hewett S, Dong J, Ziyar I, "
    "Shi A, Zhang R, Zheng L, Hou R, Shi W, Fu X, Duan Y, Huu VAN, Wen C, Zhang ED, Zhang "
    "CL, Li O, Wang X, Singer MA, Sun X, Xu J, Tafreshi A, Lewis MA, Xia H, Zhang K: "
    "Identifying medical diagnoses and treatable diseases by image-based deep learning. Cell "
    "172:1122-1131, 2018",

    "Huang G, Liu Z, van der Maaten L, Weinberger KQ: Densely connected convolutional "
    "networks. In: Proceedings of the IEEE Conference on Computer Vision and Pattern "
    "Recognition, pp 4700-4708, 2017",

    "Paszke A, Gross S, Massa F, Lerer A, Bradbury J, Chanan G, Killeen T, Lin Z, "
    "Gimelshein N, Antiga L, Desmaison A, Köpf A, Yang E, DeVito Z, Raison M, Tejani A, "
    "Chilamkurthy S, Steiner B, Fang L, Bai J, Chintala S: PyTorch: an imperative style, "
    "high-performance deep learning library. In: Advances in Neural Information Processing "
    "Systems 32, 2019",

    "Xiao S, Liu Z, Zhang P, Muennighoff N, Lian D, Nie J-Y: C-Pack: packed resources for "
    "general Chinese embeddings. In: Proceedings of the 47th International ACM SIGIR "
    "Conference on Research and Development in Information Retrieval, pp 641-649, 2024",

    "Johnson J, Douze M, Jégou H: Billion-scale similarity search with GPUs. IEEE Trans Big "
    "Data 7:535-547, 2021",

    "Dettmers T, Pagnoni A, Holtzman A, Zettlemoyer L: QLoRA: efficient finetuning of "
    "quantized LLMs. In: Advances in Neural Information Processing Systems 36, 2023",

    "Wilcoxon F: Individual comparisons by ranking methods. Biometrics Bull 1:80-83, 1945",

    "Holm S: A simple sequentially rejective multiple test procedure. Scand J Stat 6:65-70, "
    "1979",
]

for i, ref in enumerate(REFS, start=1):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.left_indent = Inches(0.35)
    p.paragraph_format.first_line_indent = Inches(-0.35)
    r = p.add_run(f"{i}. ")
    r.font.size = Pt(10)
    r2 = p.add_run(ref)
    r2.font.size = Pt(10)

# ═══════════════════════════════════════════════════════════════════════════
# APPENDIX
# ═══════════════════════════════════════════════════════════════════════════
page_break()
h1("Appendix: Item Generation Prompt")
para("The prompt used with Claude Opus 5 to generate the hundred-item bank is reproduced "
     "here in full. [Insert the verbatim prompt text.]", italic=True)

doc.save(str(OUT))
print(f"wrote {OUT}  ({OUT.stat().st_size/1024:.1f} KB)")
print(f"references: {len(REFS)}")
