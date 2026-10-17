"""
STEP 4 · The librarian (ready-made: nothing to edit)        (slide 11 · the arrow from "Policy pages")

WHAT THIS FILE DOES
    Finds the ShopKart policy pages that best match a question, so app.py can put them
    in front of the model ("open-book exam"). The pages are the 10 files in shared/data/policies/.

HOW
    Plain keyword search: no AI and no vector database, so you can read every line.
    A page scores higher when it shares more (and rarer) words with the question.
    Real systems often search by MEANING (embeddings). Same idea, smarter librarian.

TRY IT (from this folder)
    python retrieval.py "Can I return shoes after 20 days?"
    python retrieval.py "Do you price-match?"          # notice: nothing about price matching exists
"""

import math
import re
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[2] / "shared")
)  # find shared/config.py
import config  # noqa: E402

POLICY_DIR = config.DATA_DIR / "policies"

# Small words that say nothing about the topic. We ignore them.
STOPWORDS = set(
    """a an the and or but if of to in on at for from by with is are was were be been
i you we my your our me it its this that these those can could do does did have has had will would
should what when where which who how why not no yes please want like get got just so than then there
here about into out up down over any all some more most other such own same too very""".split()
)


def _words(text: str) -> list[str]:
    """Lower-case words without stopwords, with tiny 'stemming' (refunds -> refund, returned -> return)."""
    important = []
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        # Cut common endings off longer words, so "returns" and "returned" both become "return".
        if len(word) > 4:
            word = re.sub(r"(ing|ed|es|s)$", "", word)

        if word not in STOPWORDS:
            important.append(word)
    return important


def load_pages() -> list[dict]:
    """Each policy file is one 'page': {"name": "returns.md", "text": "...the page..."}."""
    pages = []
    for file in sorted(POLICY_DIR.glob("*.md")):
        pages.append(
            {
                "name": file.name,
                "text": file.read_text(encoding="utf-8").strip(),
            }
        )
    return pages


PAGES = load_pages()

# How many pages contain each word. Rare words (like "gift") count more than common ones (like "order").
_DOC_FREQ: dict[str, int] = {}
for _page in PAGES:
    unique_words = set(_words(_page["text"]))
    for _word in unique_words:
        _DOC_FREQ[_word] = _DOC_FREQ.get(_word, 0) + 1


def retrieve(question: str, top_k: int = 3) -> list[dict]:
    """Return the top_k pages that share the most (rare) words with the question. [] if nothing matches."""
    if top_k <= 0:
        return []

    question_words = set(_words(question))

    # Score every page: each question word adds (times it appears on the page) x (how rare it is).
    scored = []
    for page in PAGES:
        page_words = _words(page["text"])

        score = 0
        for word in question_words:
            rarity = math.log(1 + len(PAGES) / _DOC_FREQ.get(word, 1))
            score += page_words.count(word) * rarity

        if score > 0:
            scored.append((score, page))

    # Best score first, then keep only the top_k pages.
    scored.sort(
        key=lambda pair: pair[0],
        reverse=True,
    )
    best_pages = []
    for _score, page in scored[:top_k]:
        best_pages.append(page)
    return best_pages


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]) or "Can I return shoes after 20 days?"
    print(f"\nQ: {question}")
    found = retrieve(question)
    for page in found:
        print("  librarian brings ->", page["name"])
    if not found:
        print("  librarian found nothing")
