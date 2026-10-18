"""Keep the submitted notebooks complete without separate evidence attachments."""
import hashlib
import json
from pathlib import Path


REPO = "https://github.com/ismailabouzeidx/byte-club-c3-c4"

PERSONA_DESIGN = """## Persona configuration choices

| Persona and task | Prompt traits | Temperature / top-p / top-k | Intended effect |
| --- | --- | --- | --- |
| Sheriff: welcome customers and collect leads | Plain language, polite frontier humor, hospitality | 0.40 / 0.85 / 32 | Moderate sampling allows varied greetings while keeping intake focused. |
| Patch: scope technical services and explain published terms | Concise, precise vocabulary, explicit limits | 0.15 / 0.75 / 20 | Lower sampling favors consistent wording for factual prices, scope, and contact questions. |
| Professor Pip: advise beginner learners | Encouraging explanations and one simple analogy | 0.70 / 0.95 / 40 | Broader sampling allows more varied teaching examples and explanations. |

I kept a 2,048-token output limit and the same business facts, instructions, and tools for all three personas. I chose these settings to support their different roles. The results below show how they behaved in the test cases; the settings alone do not guarantee accurate answers.

I used the same six customer cases to compare direct answers with brief, checkable explanations, zero-shot with worked examples, and system prompts with instructions in the customer message. The first comparison covers the assignment's with/without Chain-of-Thought-style prompting through visible explanations. It does not expose private reasoning. I also changed temperature, top-p, and top-k one at a time. When comparing personas, I changed both the wording and the associated settings.
"""

RECORDED_EVIDENCE_NOTE = """## Recorded experiment evidence included in this notebook

I included all 54 recorded Gemini trials in the next cell. Each record contains the settings, customer input, reply, tool actions and observations, elapsed time, token count, and checks. I also kept the original prompts, the earlier pilot, and the final regression records so the changes discussed in my reflection can be checked.

The cell restores the saved records if the files are missing. It makes no API request and leaves existing files unchanged. The main comparison came before the final contact-validation changes, so I kept its prompts separate from the later regression results. The complete records are inside the collapsed code cell.
"""

EXPERIMENT_RUNNER = """RUN_EXPERIMENTS = False
if RUN_EXPERIMENTS:
    # New trials go to their own file, preserving the submitted observations.
    rows = run_experiments(load_business(), output="results/new_experiments.jsonl",
                           repeats=1, delay=6)
else:
    print('Showing recorded live experiments; no new Gemini requests were made.')
summary = summarize_experiments()
"""


def source(cell):
    value = cell.get("source", "")
    return value if isinstance(value, str) else "".join(value)


def set_source(cell, text):
    cell["source"] = text if isinstance(cell.get("source"), str) else text.splitlines(keepends=True)


def cell(kind, text):
    item = {
        "cell_type": kind,
        "id": hashlib.sha256(text.encode()).hexdigest()[:12],
        "metadata": {},
        "source": text,
    }
    if kind == "code":
        item.update(execution_count=None, outputs=[])
    return item


def evidence_source(folder):
    payload = {}
    for name in ("experiments.jsonl", "matrix_prompt_v1.json",
                 "final_regression.json", "pilot_gemini38.jsonl"):
        path = Path(folder) / "results" / name
        text = path.read_text(encoding="utf-8")
        payload["results/" + name] = (
            [json.loads(line) for line in text.splitlines() if line.strip()]
            if name.endswith(".jsonl") else json.loads(text)
        )
    literal = json.dumps(payload, ensure_ascii=False, indent=2)
    if "'''" in literal:
        raise ValueError("Evidence contains the notebook literal delimiter")
    return """from pathlib import Path
import json

# Original observations, not generated or simulated results.
RECORDED_EVIDENCE = json.loads(r'''""" + literal + """''')
for filename, content in RECORDED_EVIDENCE.items():
    destination = Path(filename)
    if destination.exists():
        continue
    destination.parent.mkdir(parents=True, exist_ok=True)
    if filename.endswith('.jsonl'):
        text = '\\n'.join(json.dumps(row, ensure_ascii=False) for row in content) + '\\n'
    else:
        text = json.dumps(content, ensure_ascii=False, indent=2) + '\\n'
    destination.write_text(text, encoding='utf-8')
recorded_trials = RECORDED_EVIDENCE['results/experiments.jsonl']
print(f"Embedded evidence: {len(recorded_trials)} recorded live trials across "
      f"{len({row['setup'] for row in recorded_trials})} configurations. No API request made.")
"""


def complete_submission_notebook(notebook, assignment, folder):
    """Add evidence and clear submission prose; preserve unrelated cells and outputs."""
    cells = notebook["cells"]
    if assignment == "C4":
        cells[:] = [c for c in cells if not source(c).startswith((
            "## Persona configuration choices", "## Recorded experiment evidence included",
            "from pathlib import Path\nimport json\n\n# Original observations,"))]
        persona_index = next(i for i, c in enumerate(cells)
                             if c["cell_type"] == "code" and source(c).startswith("PERSONAS ="))
        cells.insert(persona_index, cell("markdown", PERSONA_DESIGN))
        runner_index = next(i for i, c in enumerate(cells)
                            if c["cell_type"] == "code" and source(c).startswith("RUN_EXPERIMENTS ="))
        runner = cells[runner_index]
        if source(runner) != EXPERIMENT_RUNNER:
            set_source(runner, EXPERIMENT_RUNNER)
            runner["execution_count"], runner["outputs"] = None, []
        evidence = cell("code", evidence_source(folder))
        evidence["metadata"] = {"jupyter": {"source_hidden": True}}
        cells[runner_index:runner_index] = [cell("markdown", RECORDED_EVIDENCE_NOTE), evidence]

    for item in cells:
        if item["cell_type"] != "markdown":
            continue
        text = source(item)
        if text.startswith("## Reflection and interpretation"):
            set_source(item, "## Reflection and interpretation\n\nThe five required reflection questions are answered below using the recorded trials embedded in this notebook. The same reflection is retained in the repository for convenient reading.\n")
        if text.startswith("## Live experiments"):
            set_source(item, "## Live experiments\n\nThe original nine-configuration, six-case comparison is embedded below and can be reviewed without new API calls. Set `RUN_EXPERIMENTS=True` only to run a fresh comparison with your own API access; new trials are saved separately from the submitted evidence.\n\nThe cases cover prices, a PDF-only policy, a complete authorized lead, feedback, unknown facts, and a missing email. Automatic checks cover completion, routing, expected tool use, and selected factual terms. The reflection also reviews usefulness, naturalness, factual limits, and action quality.\n")
        if text.startswith("## Submission and reproducibility"):
            if assignment == "C3":
                body = f"""## Submission and reproducibility

The C3 submission requires the [GitHub repository]({REPO}) and a [functionality video]({REPO}/blob/main/demo/byte_club_demo.mp4). The repository's `C3/` folder includes `business_agent.ipynb`, `me/about_business.pdf`, `me/business_summary.txt` (and the `summary.txt` alias), and installation dependencies.

The notebook contains the business identity, separately labeled persona and instructions, a general/lead/feedback router, both required logging tools and their schemas, document-grounded Gemini interaction with chat history, and a Gradio ChatInterface. The saved live walkthrough records these paths and tool receipts. API keys and the filled `.env` are excluded from the submission.
"""
            else:
                body = """## Submission and reproducibility

Submit this notebook for C4. It includes the use-case summary (goal, audience, tools, and limits), a manual LangGraph ReAct loop, three personas with matching settings and explicit design rationales, a dedicated instructions block with worked examples, the recorded prompt/configuration comparisons, full experiment records, and answers to all five reflection questions. The reflection is included in the notebook as allowed by section 2.5; a separate reflection PDF or experiment-log attachment is unnecessary.

The installation cell supplies dependencies, the business-identity cell creates the PDF and summaries, and the recorded-evidence cell restores the logged results. A fresh evaluation remains optional and writes to a separate file.
"""
            body += "\nKnown limitations: a simple router can miss indirect phrasing; model replies need factual review; logs are local; API access and the temporary demo URL depend on the account/runtime; short conversation memory omits older turns. The recorded tests demonstrate bounded mechanics and specific cases, not a guarantee of every future reply.\n"
            set_source(item, body)
    return student_voice(notebook, assignment)


def student_voice(notebook, assignment):
    """Use the author's voice for design choices without altering code or results."""
    import re

    notes = {
        "Install the pinned dependencies": "I pinned the package versions so the setup can be reproduced. The installation cell supports a CPU runtime in Colab. If installation requests a runtime restart, the remaining cells can be run after restarting. I use the official `google-genai` SDK for Gemini; the assignment brief names an older SDK interface.",
        "Workspace and API key": "I load `GEMINI_API_KEY` from Colab Secrets or the local environment. If the Colab secret is unavailable, the setup cell offers hidden input. The notebook contains no API key. Live requests send the chat content to Gemini and use the configured account's quota.",
        "Imports and settings": "I use the official Google GenAI SDK for model calls. I limit each turn to five model steps and keep the six most recent completed turns as short-term memory. Credentials come from the environment.",
        "Business knowledge": "I load both business files before building the prompt. The summary contains the main services and prices. The PDF also contains the 24-hour rescheduling rule and the three-learner group limit. I included a question about these policies to check that answers use the PDF as well as the summary.",
        "Personas and clear instructions": "I separated the persona from the instructions. The persona sets the role and voice; the instructions define the facts, actions, and response format. Sheriff handles intake, Patch explains technical scope, and Professor Pip advises beginners. I included worked examples in the default instructions.",
        "Three-way router": "I use a simple router for general questions, lead collection, and feedback. Explicit feedback takes priority, while contact or booking signals select lead handling. Other messages use the general route. This keeps the routing easy to inspect, although indirect phrasing can be missed. Both tools remain available to the model, including when an unknown question starts on the general route.",
        "Tool schemas and real local logging functions": "I defined the two tools with names, parameter descriptions, required fields, and expected success or failure outputs. When the model requests a tool, my code validates its arguments, writes a JSONL record, and returns a receipt. The schemas follow the MCP-style descriptions discussed in class; I did not build an MCP server.",
        "Gemini adapter: automatic tool execution is explicitly disabled": "I disabled the SDK's automatic tool execution so each action is handled explicitly in my code. After a model request, I inspect the function calls and return the tool observations in the next request. I preserve Gemini's native response for continuation, while the visible trace shows the actions, observations, and final reply.",
        "Turn state and explicit model/action/observation steps": "I store the messages, pending actions, trace, and step counter in the turn state. Tool observations return to Gemini as function-response parts. I add a question and answer to memory only after the turn completes successfully. A failed request can still have a valid tool receipt, but its incomplete conversation is left out of memory.",
        "C3: a short, explicit tool-calling loop": "I handle the C3 interaction with a short loop: call Gemini, execute any requested tools, return their observations, and continue until there is a final answer. The step limit bounds the number of requests. I also included the optional reflection pass, which records the original draft and the reviewed reply.",
        "C4: define the graph state and write the ReAct loop ourselves": "I used LangGraph for the state and edge scheduling. I wrote the model node, action/observation node, conditional routing, final parsing, error handling, and step limit. I did not use AgentExecutor, create_react_agent, ToolNode, or a prebuilt agent executor.",
        "C4: manual ReAct loop in LangGraph": "I used LangGraph for the state and edge scheduling. I wrote the model node, action/observation node, conditional routing, final parsing, error handling, and step limit. I did not use AgentExecutor, create_react_agent, ToolNode, or a prebuilt agent executor.",
        "Controlled C4 experiments and honest result recording": "I recorded the exact settings, input, reply, tool trace, timing, token count, and checks for each trial. I changed one factor at a time from Patch's baseline for the prompt and sampling comparisons. The persona comparisons change both the wording and settings, so they do not isolate either factor. I removed the worked examples only for the zero-shot comparison and kept them in the default chatbot.",
        "Controlled C4 experiments": "I recorded the exact settings, input, reply, tool trace, timing, token count, and checks for each trial. I changed one factor at a time from Patch's baseline for the prompt and sampling comparisons. The persona comparisons change both the wording and settings, so they do not isolate either factor. I removed the worked examples only for the zero-shot comparison and kept them in the default chatbot.",
        "A Gradio ChatInterface with persona controls and visible tool receipts": "I connected Gradio's ChatInterface to the same runner used in the tests. Each session has its own conversation state and log directory. Changing persona or starting a new conversation clears the history. The trace panel shows the routing decision, requested tools, and receipts.",
    }
    for item in notebook["cells"]:
        if item["cell_type"] != "markdown":
            continue
        text = source(item)
        heading = text.split("\n", 1)[0]
        numbered = re.fullmatch(r"## (\d+)\. (.+)", heading)
        if text.startswith("# Byte Club Studio\n"):
            description = (
                "I built Byte Club Studio as a business assistant that answers service questions, collects leads, and records feedback. I use a three-way router, model-requested tools, and a Gradio chat interface."
                if assignment == "C3" else
                "I extended my C3 business chatbot with a manual ReAct loop in LangGraph. I compared three personas, prompt settings, and tool use, then used the recorded results to evaluate the choices."
            )
            text = "# Byte Club Studio\n\n**Ismail Abou Zeid**\n\n" + description + "\n\nI kept the implementation and business-file generation in this notebook so it can run on a CPU in Colab. The business and test contacts are fictional.\n"
        elif numbered and numbered.group(2) in notes:
            title = numbered.group(2)
            if title == "C4: define the graph state and write the ReAct loop ourselves":
                title = "C4: manual ReAct loop in LangGraph"
            elif title == "Controlled C4 experiments and honest result recording":
                title = "Controlled C4 experiments"
            text = f"## {numbered.group(1)}. {title}\n\n{notes[numbered.group(2)]}\n"
        elif numbered and numbered.group(2) == "Business identity and source files":
            text = """## 3. Business identity and source files

I created Byte Club Studio as a fictional business offering coding lessons, code reviews, and small websites. I included its mission, services, team, prices, and distinctive offer in a PDF and a short summary.

**Goal:** help beginners and small organizations choose coding assistance, answer factual service questions, record contact requests, and log feedback.

**Audience:** students, beginner programmers, and small organizations.

**Tools:** `record_customer_interest` and `record_feedback`.

**Limits:** the assistant cannot confirm appointments, email customers, process payments, or promise unpublished services. It answers from the two business files.

The next cell creates `about_business.pdf` and `business_summary.txt`. I also included the identical `summary.txt` alias because the brief uses both filenames.
"""
        elif heading == "## Live walkthrough":
            text = "## Live walkthrough\n\nI tested a general question, a lead collected across turns, feedback, an unknown business fact, and a question about the PDF-only policy. The saved output shows the replies, tool actions, and local receipts. The walkthrough can be rerun after configuring Gemini. I used fictional contact details for these demonstrations.\n"
        elif heading == "## ReAct structure":
            text = text.replace("The `think` node name denotes a model decision step.", "I use the `think` node for one model decision step.").replace("The explained-decision experiment requests only a concise customer-facing rationale.", "For the explained-decision comparison, I requested a short customer-facing rationale.")
        elif heading == "## Persona configuration choices":
            text = PERSONA_DESIGN
        elif heading == "## Live experiments":
            text = "## Live experiments\n\nI compared nine configurations on the same six cases. The original results are embedded below, so they can be reviewed without new API calls. `RUN_EXPERIMENTS` stays off by default. Enabling it runs a fresh comparison and saves the new results separately.\n\nThe cases cover prices, a PDF-only policy, a complete lead, feedback, unknown facts, and a missing email. I checked completion, routing, expected tools, and selected factual terms automatically. My reflection also considers usefulness, naturalness, factual limits, and whether the actions were appropriate.\n"
        elif heading == "## Recorded experiment evidence included in this notebook":
            text = RECORDED_EVIDENCE_NOTE
        elif heading == "## Reflection and interpretation":
            text = "## Reflection and interpretation\n\nI used the recorded trials to answer the five reflection questions below. The full trial records and the reflection are both included in this notebook.\n"
        elif text.startswith("# C4 reflection -"):
            text = text.replace("our action node", "my action node").replace("our own functions", "my own functions").replace("our code", "my code")
        elif heading == "## Launch the chatbot":
            text = "## Launch the chatbot\n\nThe final code cell opens the Gradio app. In Colab, `share=True` provides a temporary public link that needs an active runtime. Local Jupyter uses `SHARE=False` and the localhost address. The demonstration uses fictional contacts. I did not deploy a permanent Hugging Face Space.\n"
        elif heading in ("## Submission and reproducibility", "## Reproducibility and limitations"):
            if assignment == "C3":
                text = f"""## Reproducibility and limitations

My [GitHub repository]({REPO}) contains the C3 notebook, business PDF, summary, and dependencies in `C3/`. The [functionality video]({REPO}/blob/main/demo/byte_club_demo.mp4) shows the chatbot and tool receipts. I kept the API key and runtime customer logs out of the submission.

I used a simple router and short conversation memory. Indirect requests can be misclassified, older turns eventually leave the context, and generated replies still need factual review. The tools write local records; they do not send email or book appointments. Live requests depend on API access, and the temporary Gradio link depends on the runtime.
"""
            else:
                text = """## Reproducibility and limitations

I included the use-case summary, manual LangGraph ReAct loop, persona configurations, instructions, worked examples, experiment records, comparisons, and reflection in this notebook. The setup cell installs the dependencies, and the business and evidence cells recreate the files used by the implementation.

I kept the saved trials separate from new evaluations because the main comparison preceded the final contact-validation changes. The earlier prompts and final regression results are labeled separately. The tests cover specific cases and bounded execution; they do not guarantee the quality of every future reply.

The assistant still has a simple router, short memory, generated replies, and local logging. It depends on API access for new conversations and on an active runtime for the temporary Gradio link.
"""
        elif heading == "## References":
            text = text.replace("The project uses ordinary application tool calls with MCP-style schema descriptions, not an MCP server.", "I used ordinary application tool calls with MCP-style schema descriptions.").replace("this project does not import or use them", "I did not import or use them")
        set_source(item, text)
    return notebook
