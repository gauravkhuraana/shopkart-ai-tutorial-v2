# Optional extra · LangSmith UI: traces and evaluation experiments

> Not part of the tutorial. Steps 6-9 run fully on your laptop and show their results in `evaluate/report.html`. LangSmith is a cloud service: it needs an account (the `langsmith` package itself is already in requirements.txt).

LangGraph builds the Step 5 workflow. LangSmith is the optional cloud UI that shows its traces, datasets and evaluation results. Steps 6-9 (DeepEval + pytest) work without it.

## Before you enable it

LangSmith receives the prompts, model replies, retrieved policy text and agent state for traced runs. Do not use real customer data or secrets. Leave `LANGSMITH_TRACING=false` if you want all runs to stay local.

## 1. Configure LangSmith

1. Create a LangSmith account and API key at <https://smith.langchain.com/settings>.
2. Add these values to the root `.env` file:

```text
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your-real-key
LANGSMITH_PROJECT=shopkart-ai-tutorial
```

If the key belongs to multiple workspaces, also set `LANGSMITH_WORKSPACE_ID`.

Restart `uvicorn` after changing `.env`.

## 2. See a LangGraph trace

Run the Step 5 bot:

```powershell
cd build\step5_agent
uvicorn app:app --reload
```

Use Agent mode in <http://localhost:8000>, or from another terminal run:

```powershell
cd build\step5_agent
python agent.py 1043
```

Open <https://smith.langchain.com>, select the `shopkart-ai-tutorial` project, and open the latest trace. It shows the LangGraph nodes and the OpenAI-compatible model calls beneath them.

## 3. Run a dataset experiment

Keep the bot running, then use a second terminal from the project root:

```powershell
python extras\langsmith\langsmith_eval.py
```

This command:

1. uploads or updates `evaluate/golden_questions.yaml` as the `shopkart-golden-questions` dataset;
2. calls the local `/chat` endpoint for every example;
3. scores the existing `must_include_any` and `must_not_include` rules;
4. uploads the experiment and feedback to the LangSmith UI.

To include a model-based correctness score using `JUDGE_MODEL`:

```powershell
python extras\langsmith\langsmith_eval.py --with-ai-judge
```

That option makes one additional judge-model call per dataset example. Start with the rules-only command to avoid unnecessary cost and rate limits.

To upload the dataset without running the bot:

```powershell
python extras\langsmith\langsmith_eval.py --dataset-only
```

## 4. Plant a bug and compare experiments

```powershell
python plant_bug.py liar
python extras\langsmith\langsmith_eval.py --with-ai-judge
python plant_bug.py off
python extras\langsmith\langsmith_eval.py --with-ai-judge
```

Compare the two experiments in LangSmith. The price-match case should show worse rule and AI-judge feedback while the bug is active.

## Local versus UI evaluation

| Workflow | Best for |
|---|---|
| `pytest evaluate\step6_rules evaluate\step7_judge` | Fast local regression checks and CI |
| `pytest evaluate\step8_agent` | Exact agent journey and safety assertions |
| `python extras\langsmith\langsmith_eval.py` | Browsing datasets, traces, scores and experiment comparisons in a UI |

Keep pytest as the pass/fail gate. Use LangSmith to investigate why a run behaved differently and to compare experiments.
