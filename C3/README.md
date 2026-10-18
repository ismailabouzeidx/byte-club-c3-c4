# Byte Club Studio

Ismail Abou Zeid | EECE 503P/798S

Byte Club Studio is a fictional business offering coding lessons, code reviews, and small websites. The C3 notebook uses Gemini, two logging tools, a three-way router, and Gradio ChatInterface.

## Files

- `business_agent.ipynb`: self-contained Colab/Jupyter implementation and explanations.
- `app.py`: the same Python source as a local deployment script.
- `me/about_business.pdf`: business profile, services, fictional team, and policies.
- `me/business_summary.txt`: short source summary.
- `me/summary.txt`: identical alias because task 1 and the checklist use different names.
- `requirements.txt`: pinned dependencies.
- `.env.example`: credential variable names, without values.
- `results/`: only saved synthetic demonstrations, never real customer records.

## Run in Colab

1. Open the notebook and choose a CPU runtime.
2. Add `GEMINI_API_KEY` in Colab Secrets and enable notebook access, or use the hidden prompt.
3. Run the cells in order. Business files are generated automatically.
4. Launch the Gradio interface in the final code cell.
5. Keep the runtime active while demonstrating the temporary share URL.

For local use, install the requirements and create `.env` from `.env.example` in this folder or the repository root. Run `python app.py` and open the printed localhost URL. Never publish the filled `.env`.

## Requirements map

| Required item | Where to inspect |
| --- | --- |
| Business name, mission, services, team, distinctive offer | Business PDF and summary; notebook business section |
| Separate persona and instructions | `PERSONAS`, `CORE_INSTRUCTIONS`, `WORKED_EXAMPLES` |
| General/lead/feedback router | `route_message`; trace's route entry |
| `record_customer_interest(email, name, message)` | `make_tools`, successful receipt, local JSONL record |
| `record_feedback(question)` | `make_tools`; unknown-question and feedback examples |
| MCP-style name, parameter, and output descriptions | `TOOL_SCHEMAS`, `TOOL_OUTPUT_SCHEMA` |
| Ground answers in both PDF and summary | `load_business`; PDF-specific policy demonstration |
| Gemini backend with history and tool responses | `call_gemini`, `prepare_turn`, `run_c3`, `action_step` |
| Gradio ChatInterface | `build_app` |
| Repository and functionality video | Repository root and final demo recording |

## What the app does

Sheriff is an intake concierge, Patch is a precise scoping advisor, and Professor Pip helps beginners choose a service. A persona changes tone and role; common instructions keep the facts and tool rules consistent. Each persona has a temperature, top-p, top-k, and output-token preset.

The router uses simple keyword/email heuristics. It sets the handling context but does not execute the tools. The model requests a declared function; our code checks its arguments, performs local logging, sends the observation back, and asks for the final reply. Requests are limited to five model steps. Repeated identical writes within one turn reuse the first receipt.

Recent completed question/answer pairs provide short-term memory. Only the six most recent pairs are sent. Each browser session has separate state and local log files. Starting a new conversation or changing persona resets both model memory and displayed conversation.

## Demonstration sequence

1. Ask the price of Python tutoring: USD 25 for 60 minutes.
2. Ask about free rescheduling: at least 24 hours' notice, read from the PDF.
3. Register interest without an email: the assistant should ask for missing contact information.
4. Supply `alex@example.com` and request recording: show the actual tool action and success receipt.
5. Give feedback: show `record_feedback` and its observation.
6. Ask about Rust certification: the source does not provide it, so the assistant should acknowledge uncertainty and log the question.
7. Change persona or start a new conversation and verify that old contact details are not remembered.

The optional reflection checkbox adds a model pass and displays both original and revised replies in the trace. The Hugging Face deployment bonus is separate; it has not been claimed by a temporary Colab URL.

## Limits

The business, team, email address, and evaluation contacts are fictional. Logs demonstrate intake and feedback recording; no actual booking or notification occurs. A heuristic router and generated answers can be wrong. Review the trace and source documents. Keys and runtime logs are excluded from the repository.


## Final validation hardening

Lead tools reject names and emails absent from the actual customer messages, even when the model copies a worked example. The interface derives model history from the visible conversation and clears Gradio's internal states on persona changes. Saved comparison data predates this hardening; final regression evidence checks the updated implementation separately.
