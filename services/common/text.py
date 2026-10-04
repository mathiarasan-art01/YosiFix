"""Pure-Python text utilities: tokenization, TF-IDF and cosine similarity.

Replaces scikit-learn (≈100 MB on Vercel) with ~100 lines that are fully deterministic
and explainable: every similarity score can be traced back to the shared terms.
"""
import math
import re
from collections import Counter
from typing import Dict, Iterable, List, Sequence, Tuple

STOPWORDS = set(
    """a about above after again against all also am an and any are as at be because been before
    being below between both but by can could did do does doing down during each few for from
    further had has have having he her here hers herself him himself his how i if in into is it its
    itself just me more most my myself no nor not now of off on once only or other our ours
    ourselves out over own same she should so some such than that the their theirs them themselves
    then there these they this those through to too under until up very was we were what when where
    which while who whom why will with would you your yours yourself yourselves using use used
    based system systems platform app application tool tools project solution solutions new make
    help helps provide provides via within without across like get one two many much well able
    want need needs allow allows enable enables etc user users people idea ideas simple smart""".split()
)

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#\-]{1,}")


def _stem(word: str) -> str:
    for suffix in ("ations", "ation", "ments", "ment", "ingly", "ing", "ies", "ers", "er", "ed", "es", "s"):
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            if suffix == "ies":
                return word[: -3] + "y"
            return word[: -len(suffix)]
    return word


def tokenize(text: str, stem: bool = True) -> List[str]:
    if not text:
        return []
    tokens = _TOKEN_RE.findall(text.lower())
    out = []
    for tok in tokens:
        tok = tok.strip("-")
        if len(tok) < 3 or tok in STOPWORDS or tok.isdigit():
            continue
        out.append(_stem(tok) if stem else tok)
    return out


def keywords(text: str, limit: int = 10) -> List[str]:
    """Most frequent meaningful (unstemmed) words, in first-seen order for ties."""
    toks = tokenize(text, stem=False)
    counts = Counter(toks)
    order = {t: i for i, t in reversed(list(enumerate(toks)))}
    ranked = sorted(counts, key=lambda t: (-counts[t], order[t]))
    return ranked[:limit]


class TfidfIndex:
    """Fit on a small corpus, then compare any document vectors with cosine similarity."""

    def __init__(self, documents: Sequence[str]):
        self.docs_tokens = [tokenize(d) for d in documents]
        n = len(self.docs_tokens)
        df: Counter = Counter()
        for toks in self.docs_tokens:
            df.update(set(toks))
        self.idf = {t: math.log((1 + n) / (1 + c)) + 1.0 for t, c in df.items()}
        self.vectors = [self._vec(toks) for toks in self.docs_tokens]

    def _vec(self, toks: Iterable[str]) -> Dict[str, float]:
        tf = Counter(toks)
        if not tf:
            return {}
        vec = {t: (1 + math.log(c)) * self.idf.get(t, 1.0) for t, c in tf.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    def vector_for(self, text: str) -> Dict[str, float]:
        return self._vec(tokenize(text))

    @staticmethod
    def cosine(a: Dict[str, float], b: Dict[str, float]) -> float:
        if not a or not b:
            return 0.0
        if len(a) > len(b):
            a, b = b, a
        return sum(v * b.get(t, 0.0) for t, v in a.items())

    @staticmethod
    def shared_terms(a: Dict[str, float], b: Dict[str, float], limit: int = 6) -> List[str]:
        common = [(t, a[t] * b[t]) for t in a.keys() & b.keys()]
        common.sort(key=lambda x: -x[1])
        return [t for t, _ in common[:limit]]


def similarity(text_a: str, text_b: str, corpus: Sequence[str] = ()) -> Tuple[float, List[str]]:
    """Cosine similarity of two texts (0..1) and the terms driving it."""
    index = TfidfIndex(list(corpus) + [text_a, text_b])
    va, vb = index.vector_for(text_a), index.vector_for(text_b)
    return index.cosine(va, vb), index.shared_terms(va, vb)


def term_coverage(text: str, terms: Iterable[str]) -> bool:
    lowered = (text or "").lower()
    return any(re.search(r"\b" + re.escape(t.lower()), lowered) for t in terms)


def truncate(text: str, limit: int = 280) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"
