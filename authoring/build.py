"""Build two self-contained, readable notebooks and matching deployment scripts."""
import base64
import json
from pathlib import Path
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "authoring"
PINS = {"google-genai": "1.75.0", "gradio": "6.30.0", "pypdf": "6.21.1",
        "reportlab": "4.5.1", "python-dotenv": "1.2.1", "langgraph": "1.2.16"}

EXPLANATIONS = {
    "Imports and settings": "We use the official Google GenAI SDK. Five model steps bound a turn; recent completed turns supply short-term memory. Credentials come from the environment, never from a notebook literal.",
    "Business knowledge": "The assistant reads both files. The summary gives the main offer; the PDF adds the 24-hour rescheduling rule and three-learner group limit. A PDF-specific test verifies that the second file matters.",
    "Personas and clear instructions": "Persona controls tone and role. Instructions control facts, actions, and output. Sheriff handles intake, Patch scopes technical services, and Pip advises beginners. Their generation settings match those roles. Production includes worked examples inside the instructions.",
    "Three-way router": "The router is deterministic and easy to inspect. Explicit feedback takes priority, contact/booking signals select lead handling, and other questions select general handling. This heuristic can miss indirect intents; the model still receives both tools and must log unknown business questions on any route.",
    "Tool schemas and real local logging functions": "The model receives JSON-schema declarations. Our Python code validates and executes only these two functions, writes a JSONL record, and returns an observation. The returned receipt is the evidence of success. These are MCP-style descriptions; this project does not implement an MCP server.",
    "Gemini adapter: automatic tool execution is explicitly disabled": "The SDK makes a single model request at a time. We inspect its output ourselves. The full native response is retained when returning tool results so Gemini's opaque signatures are preserved. Visible traces contain actions, observations, and brief answers, never private model reasoning.",
    "Turn state and explicit model/action/observation steps": "State holds messages, pending actions, the visible trace, and a step counter. Tool results return to the model as function-response parts. A successful final answer updates chat history. Failed requests retain their action receipts but do not enter completed conversation memory.",
    "C3: a short, explicit tool-calling loop": "C3 repeatedly asks the model, executes any requested functions, returns their observations, and stops at a visible answer. A step limit prevents an endless loop. The optional reflection pass uses one extra request and shows the original and revised replies.",
    "C4: define the graph state and write the ReAct loop ourselves": "LangGraph supplies state and edge scheduling. We wrote the model node, action/observation node, conditional routing, final parsing, error path, and step limit. We do not use AgentExecutor, create_react_agent, ToolNode, or another prebuilt execution loop.",
    "Controlled C4 experiments and honest result recording": "Each run records its exact settings, synthetic input, visible reply, action trace, timing, token count, and simple checks. Ablations change one factor from Patch's baseline. Persona-package comparisons deliberately change both prompt and settings and cannot isolate either cause. The zero-shot ablation omits worked examples for comparison; production restores the required examples.",
    "A Gradio ChatInterface with persona controls and visible tool receipts": "The interface calls the same runner used by the tests. Every session has separate conversation state and log files. Changing persona or starting a new conversation clears its history. The trace panel explains routing and shows actual tool receipts.",
}


def sections(filename):
    text = (SOURCE / filename).read_text(encoding="utf-8")
    result = []
    for part in text.split("# %% "):
        if not part.strip():
            continue
        heading, code = part.split("\n", 1)
        result.append((heading, code))
    return result


def md(text):
    return nbf.v4.new_markdown_cell(text)


def code(text):
    return nbf.v4.new_code_cell(text.strip() + "\n")


def build(assignment):
    folder = ROOT / assignment
    folder.mkdir(exist_ok=True)
    packages = dict(PINS)
    if assignment == "C3":
        packages.pop("langgraph")
    requirements = "\n".join(name + "==" + version for name, version in packages.items()) + "\n"
    (folder / "requirements.txt").write_text(requirements)
    (folder / ".env.example").write_text((ROOT / ".env.example").read_text())
    cells = [md("# Byte Club Studio\n\n**Ismail Abou Zeid | EECE 503P/798S: Agentic Systems**\n\n" +
                ("A business assistant with a three-way router, model-requested tools, business documents, and a Gradio chat interface." if assignment == "C3" else
                 "An extension of C3 with a manual ReAct loop in LangGraph. I compare personas, prompt settings, and tool use, then discuss the results.") +
                "\n\nThis notebook is self-contained: it creates its business documents, defines the code, and can run on a CPU in Colab. The business and all evaluation contacts are fictional. Read each explanation before running the next code cell."),
             md("## 1. Install the pinned dependencies\n\nRun this once in Colab. Restart the runtime only if installation requests it, then continue with the next cell. The Python SDK names in the original brief are older interfaces; this implementation uses the official `google-genai` SDK for the required Gemini backend."),
             code("%pip -q install " + " ".join("'" + name + "==" + version + "'" for name, version in packages.items())),
             md("## 2. Workspace and API key\n\nIn Colab, add a secret named `GEMINI_API_KEY` and enable notebook access. If absent, the next cell offers hidden input. Locally, create `.env` from `.env.example`. Never publish the filled `.env` or paste a key into a code cell. Ordinary chat content is sent to Google when you make a live request."),
             code("""import os
import sys
from pathlib import Path
from dotenv import load_dotenv

IN_COLAB = 'google.colab' in sys.modules
if IN_COLAB:
    project_dir = Path('/content/byte_club_""" + assignment.lower() + """')
    project_dir.mkdir(exist_ok=True)
    os.chdir(project_dir)
load_dotenv()
if IN_COLAB and not os.getenv('GEMINI_API_KEY'):
    try:
        from google.colab import userdata
        os.environ['GEMINI_API_KEY'] = userdata.get('GEMINI_API_KEY')
    except Exception:
        from getpass import getpass
        key = getpass('Gemini API key (hidden; leave blank to skip live calls): ')
        if key:
            os.environ['GEMINI_API_KEY'] = key
print('Gemini key configured:', bool(os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')))
print('Workspace:', Path.cwd())"""),
             md("## 3. Business identity and source files\n\n**Goal:** help beginners and small organizations choose coding assistance, answer factual service questions, record qualified contact requests, and log feedback.\n\n**Audience:** university students, beginner programmers, and small organizations.\n\n**Tools:** `record_customer_interest` and `record_feedback`.\n\n**Limits:** this is a fictional information and intake assistant. It cannot confirm appointments, email customers, process payments, or promise unavailable services. Its knowledge comes only from the two included business files.\n\nThe following cell writes the actual PDF and summary. `summary.txt` is an identical alias because the brief uses both spellings; `business_summary.txt` is the checklist's primary filename."),
             code((SOURCE / "business.py").read_text().split('\nif __name__ == "__main__":')[0] + '\ncreate_business_files("me")\nprint("Business PDF and summary created.")')]
    used = ["common.py"] + (["graph.py", "experiments.py"] if assignment == "C4" else []) + ["interface.py"]
    section_number = 4
    for filename in used:
        for heading, text in sections(filename):
            cells.append(md("## " + str(section_number) + ". " + heading + "\n\n" + EXPLANATIONS.get(heading, "Read and run the implementation below.")))
            cells.append(code(text))
            section_number += 1
    if assignment == "C4":
        cells.extend([md("## ReAct structure\n\n```mermaid\n" + """graph TD
START --> think
think -->|action requested| act_and_observe
act_and_observe -->|observation| think
think -->|final answer or limit| finish
finish --> END
""" + "```\n\nThe `think` node name denotes a model decision step. The application records requested actions and observations, not hidden chain-of-thought. The explained-decision experiment requests only a concise customer-facing rationale. It does not switch off the model's internal computation."),
                      md("## Live experiments\n\nSet `RUN_EXPERIMENTS=True` to make real Gemini calls. The complete matrix has 54 turns and may require multiple model calls per turn. Start with a small subset if quota is limited. Each output row includes exact settings; failures are saved and stop the batch. Do not interpret an unrun matrix as evidence.\n\nThe six shared cases cover prices, PDF-only policy, a complete authorized lead, feedback, unknown facts, and a missing email. For each persona, also review usefulness, naturalness, scope accuracy, and whether actions were appropriate. The automatic word checks are intentionally limited and need human review."),
                      code("""RUN_EXPERIMENTS = False
knowledge = load_business()
if RUN_EXPERIMENTS:
    rows = run_experiments(knowledge, repeats=1, delay=6)
else:
    print('Live experiments are off. Enable the flag after configuring Gemini.')
summary = summarize_experiments()"""),
                      md("## Reflection and interpretation\n\nThe reflection below is based on the saved live runs and is also stored in `REFLECTION.md`. Required questions: which persona was most helpful/natural; which prompt and configuration worked best; how tools were used; what changed when instructions changed; and the largest implementation challenges. No performance claim should be filled in before its supporting experiment exists."),
                      md((folder / "REFLECTION.md").read_text() if (folder / "REFLECTION.md").exists() else "**Current evidence status:** live Gemini comparisons have not yet been recorded.")])
    else:
        cells.extend([md("## Live walkthrough\n\nRun this after configuring Gemini. It demonstrates a general question, a lead collected across turns, feedback, an unknown fact, and PDF-specific knowledge. Every tool action must appear in the returned trace and local log. Use only synthetic details for the recording."),
                      code("""RUN_LIVE_DEMO = os.getenv("BYTECLUB_LIVE_DEMO") == "1"
if RUN_LIVE_DEMO:
    knowledge = load_business()
    history = []
    session_id = uuid.uuid4().hex
    demo_messages = [
        'How much is Python tutoring?',
        'Please register my interest in Python tutoring. My name is Alex Demo and I need help with loops.',
        'My email is alex@example.com. Please record that contact request.',
        'Feedback: the website pricing is unclear.',
        'Do you provide an official Rust certification?',
        'How much notice is needed for free rescheduling?',
    ]
    for index, message in enumerate(demo_messages):
        result = run_c3(message, history, knowledge, settings={"reflection": index == len(demo_messages) - 1}, session_id=session_id)
        history = result['history']
        print('CUSTOMER:', message)
        print('ASSISTANT:', result['answer'])
        print('TRACE:', json.dumps(result['trace'], indent=2))
        if result['error']:
            break
else:
    print('Enable RUN_LIVE_DEMO after configuring Gemini.')""")])
    cells.extend([md("## Launch the chatbot\n\nIn Colab, `share=True` creates a temporary public Gradio URL tied to the runtime. Use synthetic data. Locally, leave `SHARE=False` and open the localhost address. Hugging Face Spaces is an optional separate deployment bonus, not required for the base assignment."),
                  code("SHARE = IN_COLAB\napp = build_app('" + assignment + "')\napp.launch(share=SHARE, **app.byteclub_launch)"),
                  md("## Submission and reproducibility\n\nInclude this notebook, `me/about_business.pdf`, `me/business_summary.txt`, `requirements.txt`, and `README.md`. C3 explicitly requires a GitHub repository with a functionality video. Keep the C3 and C4 folders separately runnable. The filled `.env` and runtime customer logs are excluded.\n\nKnown limitations: a simple router can miss indirect phrasing; model replies need factual review; local logs are not a production CRM; API access and the temporary demo URL depend on the account/runtime; short conversation memory omits older turns."),
                  md("## References\n\n- [Assignment C3](https://lms.aub.edu.lb/mod/assign/view.php?id=2784814)\n- [Assignment C4](https://lms.aub.edu.lb/mod/assign/view.php?id=2784815)\n- [Gemini function calling](https://ai.google.dev/gemini-api/docs/generate-content/function-calling)\n- [Gemini models](https://ai.google.dev/gemini-api/docs/models)\n- [Google GenAI Python SDK](https://github.com/googleapis/python-genai)\n- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)\n- [Gradio ChatInterface](https://www.gradio.app/docs/gradio/chatinterface)\n\nThe project uses ordinary application tool calls with MCP-style schema descriptions, not an MCP server. The LangGraph framework dependency may install prebuilt modules transitively; this project does not import or use them.")])
    nb = nbf.v4.new_notebook(cells=cells)
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                   "language_info": {"name": "python"}, "colab": {"provenance": []}}
    name = "business_agent.ipynb" if assignment == "C3" else "react_agent.ipynb"
    path = folder / name
    # Rebuilding preserves observed outputs when a cell's exact code is unchanged.
    if path.exists():
        previous = nbf.read(path, as_version=4)
        previous_codes = {cell.source: cell for cell in previous.cells if cell.cell_type == "code"}
        for cell in nb.cells:
            if cell.cell_type == "code" and cell.source in previous_codes:
                old = previous_codes[cell.source]
                cell.outputs, cell.execution_count = old.outputs, old.execution_count
    nbf.validate(nb)
    nbf.write(nb, path)
    sources = [(SOURCE / name).read_text() for name in used]
    launcher = "\n\nif __name__ == '__main__':\n    os.chdir(Path(__file__).resolve().parent)\n    app = build_app('" + assignment + "')\n    app.launch(server_name='127.0.0.1', server_port=int(os.getenv('PORT', '7860')), share=False, **app.byteclub_launch)\n"
    (folder / "app.py").write_text("\n\n".join(sources) + launcher, encoding="utf-8")
    print(assignment, len(nb.cells), "cells", path)


if __name__ == "__main__":
    for assignment in ["C3", "C4"]:
        build(assignment)
