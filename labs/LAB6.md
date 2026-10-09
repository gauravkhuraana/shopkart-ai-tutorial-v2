# LAB 6 · Mission: catch the liar (20 min)
**Goal:** plant a known bug in your chatbot, catch it with a cheap rule first, then let the AI judge look.
**You'll learn:** golden datasets, cheap rule checks vs the AI judge, pass marks, regression testing for AI.
Files: `tests/test_chatbot.py` + the answer key `tests/golden_questions.yaml`.

Keep the step 5 bot running (`uvicorn app:app --reload` in `build/step5_agent`). The tests call it over HTTP, exactly like the chat page.
Laptop can't run the bot? Set `SHOPKART_URL` in `.env` to the hosted bot from the slide (FAQ #18).

Read `golden_questions.yaml` first: 10 questions in three groups (in the policy · not in the policy · off-topic / attack).

## What the judge checks (slide 17) · **Is it TRUE?**
| Letter | Question | Failure it catches (slide 16) | DeepEval metric | In the code |
|---|---|---|---|---|
| **T** | Truthful? | Makes things up | `HallucinationMetric` | stretch, TODO 2 |
| **R** | Relevant? | Off-topic | `AnswerRelevancyMetric` | given |
| **U** | Uses the source? | Not from the policy | `FaithfulnessMetric` | stretch, TODO 2 |
| **E** | Even (consistent)? | Contradicts itself | `GEval` "Coherence" | given |
| | Correct vs the answer key? | Wrong answer | `GEval` "Correctness" | given |
| | Talked into it · leaks its rules · invents discounts | | plain rules: `must_not_include` | **core, TODO 1** |

Cheapest first: rules run on every question; the judge only on `judge: true` questions.

---

## CORE (everyone · ~12 min)

### Mission 1 · Catch the liar with a plain rule
```bash
python plant_bug.py liar
```
A bad page has sneaked into ShopKart's knowledge base. Ask the bot **"Do you price-match?"** in the chat page: it now says yes, confidently. ShopKart has no such policy.

1. **TODO 1 · Metal detector.** In `test_metal_detector`, write the two rule checks from the YAML:
   `must_include_any` (at least one must appear) and `must_not_include` (none may appear).
2. Run the cheap checks (free, no AI):
   ```bash
   pytest tests/test_chatbot.py -v -k metal
   ```
   **The price-match test goes red.** You caught the liar with a plain rule.

### Let the AI judge look (one question)
3. **TODO 3 ·** set your pass marks `GROUNDED_PASS` and `HALLUCINATION_MAX` at the top (try 0.7 and 0.5).
4. With the liar still planted, run the judge on that one question and **read the reasons it gives**:
   ```bash
   pytest tests/test_chatbot.py -v -k "ai_judge and price"
   ```
5. `python plant_bug.py off` and run the metal detector again: all green.

**Done when:** you've seen the liar go red with a rule, and read at least one score + reason from the judge.

---

## STRETCH (fast finishers)

### Mission 2 · Complete the TRUE check
**TODO 2 ·** add the two missing metrics to `test_ai_judge`: `FaithfulnessMetric` (**U**ses the source?) and `HallucinationMetric` (**T**ruthful?). Plant the liar again and rerun the price question.
**Faithfulness** may pass, because the bot faithfully repeated the bad page. **Hallucination** fails, because it contradicts the truth.
That's "wrong pages in → confident wrong answer out", caught by a test.

### Mission 3 · Catch the forgetful librarian
```bash
python plant_bug.py no_pages
pytest tests/test_chatbot.py -v -k metal
```
The librarian now brings nothing. Which questions go red? Why do the "not in policy" ones stay green? Finish with `python plant_bug.py off`.

### More
- Add 3 questions from this morning's phone hacking to the YAML (set `judge: true` on one of them).
- Run the whole judge suite: `pytest tests/test_chatbot.py -v -k ai_judge`. It's slower and makes more judge calls (FAQ #14, #15).

---

## Stuck?
`python checkpoint.py lab6` · FAQ #13 "invalid JSON" · #14 "429 rate limit" · #15 "very slow" · #19 "tests red for no reason"

## Boss level
Write your own rubric with `GEval`, e.g. "never promises compensation that isn't in the policy", and add it to the metrics.
