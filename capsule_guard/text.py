from __future__ import annotations

import re


SYNONYMS = {
    "notebook": "laptop",
    "procurement": "buying",
    "buy": "buying",
    "purchasing": "buying",
    "cellphone": "phone",
    "mobile": "phone",
}


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "for",
    "from",
    "give",
    "i",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "or",
    "should",
    "the",
    "to",
    "user",
    "vendor",
    "recommend",
    "recommendation",
    "purchase",
    "decision",
    "decisions",
    "task",
    "tasks",
    "what",
    "which",
}


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


def topic_terms(text: str) -> frozenset[str]:
    return frozenset(token for token in tokenize(text) if token not in STOPWORDS and len(token) > 2)


def canonical_terms(terms: set[str] | frozenset[str]) -> frozenset[str]:
    return frozenset(SYNONYMS.get(term, term) for term in terms)


def jaccard(left: set[str] | frozenset[str], right: set[str] | frozenset[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)
