# Byte Club Studio

[Open C3 in Colab](https://colab.research.google.com/github/ismailabouzeidx/byte-club-c3-c4/blob/main/C3/business_agent.ipynb) · [Open C4 in Colab](https://colab.research.google.com/github/ismailabouzeidx/byte-club-c3-c4/blob/main/C4/react_agent.ipynb) · [Demo video](demo/byte_club_demo.mp4) · [Validation record](VALIDATION.md)

Ismail Abou Zeid

Byte Club Studio is a fictional coding-help business. C3 implements an information and intake chatbot. C4 extends that exact business into a manually implemented ReAct agent inside LangGraph. Each folder can run independently.

| Version | Notebook | Implementation |
| --- | --- | --- |
| C3 | `C3/business_agent.ipynb` | Three-way router, model-requested tools, short-term memory, Gradio ChatInterface |
| C4 | `C4/react_agent.ipynb` | Explicit LangGraph model/action/observation loop, three persona configurations, controlled experiments |

## Run

Open either notebook in Colab, run its setup cells, and provide `GEMINI_API_KEY` through Colab Secrets or the hidden prompt. A CPU runtime is sufficient. Each notebook writes its own business PDF and summary.

For local execution:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r C4/requirements.txt
cp .env.example .env
# Set GEMINI_API_KEY in .env using an editor.
python C3/app.py
# Or, after stopping C3:
python C4/app.py
```

The default model is `gemini-3.5-flash-lite`, configurable with `GEMINI_MODEL` or the interface. The official Google GenAI SDK supplies the Gemini backend required by C3.

## Business and tools

- Python tutoring: USD 25 per 60 minutes.
- Code Clinic: USD 40 per 60 minutes.
- Starter website: free 20-minute consultation; implementation starts at USD 300, subject to scope and quote.
- PDF-specific policies: free rescheduling with at least 24 hours' notice; at most three learners in group tutoring, with group pricing unpublished.

`record_customer_interest(email, name, message)` writes a local contact-request record. `record_feedback(question)` records explicit feedback or an unanswered business question. Both return a success receipt or a validation/storage error. They do not send email, reserve appointments, process payments, or connect to a CRM.

The persona, instructions, schemas, routing decision, requested actions, and observations are inspectable. Opaque Gemini signatures remain in the in-memory continuation; hidden model reasoning is never displayed.

## Reproducibility and evidence

`authoring/` contains the readable source sections and the builder that produces matching notebook cells and deployment scripts. It is not required to run the submitted notebooks.

```bash
python authoring/build.py
python authoring/verify.py
python authoring/live_check.py --assignment C3
python authoring/live_check.py --assignment C4 --matrix
```

The verification script uses scripted SDK responses to test execution mechanics. Live Gemini result files are separately labeled `source=live_gemini`. Automatic experiment checks cover completion, routing, expected tool use, and selected factual terms; they do not establish overall response quality or statistical significance. Read the saved replies and C4 reflection before interpreting results.

## Submission package

- C3: submit this repository link and the functionality video at `demo/byte_club_demo.mp4`. The required notebook, business PDF, and summary are in `C3/`.
- C4: submit `C4/react_agent.ipynb`. It contains the implementation, persona configurations, prompt comparisons, all 54 recorded experiment trials, and answers to all five reflection questions. Its setup and evidence cells recreate the required files; no separate reflection PDF or experiment-log upload is needed.
- The repository keeps C3 and C4 as distinct runnable folders, with supporting source and result files for reference.
- The filled `.env` and runtime customer logs are excluded. Only synthetic-contact evaluation evidence belongs in the repository.
- Reflection-pass demonstrations and Hugging Face Spaces deployment are optional C3 bonuses. A temporary Gradio link is tied to the running Colab session.

## Sources

- [Gemini function calling](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)
- [Gemini models](https://ai.google.dev/gemini-api/docs/models)
- [Google GenAI Python SDK](https://github.com/googleapis/python-genai)
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)
- [Gradio ChatInterface](https://www.gradio.app/docs/gradio/chatinterface)
