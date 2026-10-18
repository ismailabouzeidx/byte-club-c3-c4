"""Offline integration checks. Scripted SDK responses test mechanics, not LLM quality."""
import importlib.util
import json
import os
import tempfile
import asyncio
import inspect
import faulthandler
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
checks = []
faulthandler.dump_traceback_later(30)


def require(condition, label):
    assert condition, label
    checks.append(label)


def response(text="", calls=None, hidden=False, finish="STOP"):
    from google.genai import types
    parts = []
    if hidden:
        parts.append(types.Part(text="PRIVATE_TEST_TRACE", thought=True))
    if text:
        parts.append(types.Part(text=text))
    for index, (name, arguments) in enumerate(calls or []):
        parts.append(types.Part(function_call=types.FunctionCall(name=name, args=arguments, id="call_" + str(index)), thought_signature=b"opaque-test-signature"))
    return types.GenerateContentResponse(candidates=[types.Candidate(content=types.Content(role="model", parts=parts), finish_reason=finish)],
                                         usage_metadata=types.GenerateContentResponseUsageMetadata(total_token_count=25))


class ScriptedClient:
    def __init__(self, replies):
        self.replies, self.requests = list(replies), []
        self.models = self

    def generate_content(self, **request):
        require(request["config"].automatic_function_calling.disable, "Automatic execution is disabled")
        self.requests.append(request)
        if not self.replies:
            raise RuntimeError("Unexpected extra model call")
        result = self.replies.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


for assignment in ["C3", "C4"]:
    print("Checking", assignment, flush=True)
    folder = ROOT / assignment
    os.chdir(folder)
    spec = importlib.util.spec_from_file_location("check_" + assignment, folder / "app.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    runner = module.run_c3 if assignment == "C3" else module.run_c4
    knowledge = module.load_business()
    require("24 hours" in knowledge and "three learners" in knowledge, assignment + " loads PDF-specific facts")
    require(module.route_message("Feedback: confusing prices; contact a@example.com") == "feedback", assignment + " feedback route priority")
    require(module.route_message("Please contact me") == "lead", assignment + " lead route")
    require(module.route_message("How much is tutoring?") == "general", assignment + " general route")
    with tempfile.TemporaryDirectory() as logs:
        client = ScriptedClient([response(calls=[("record_customer_interest", {"email": "alex@example.com", "name": "Alex Demo", "message": "Python loops"})], hidden=True), response("Your request was recorded.")])
        result = runner("Please record my interest. I am Alex Demo, alex@example.com; help with Python loops.", [], knowledge, client=client, log_root=logs)
        require(not result["error"] and result["model_steps"] == 2, assignment + " completes model/action/observation/final cycle")
        recorded = list(Path(logs).glob("*/customer_interest.jsonl"))
        require(len(recorded) == 1 and "alex@example.com" in recorded[0].read_text(), assignment + " actually writes tool record")
        sent = client.requests[1]["contents"]
        require(sent[1].parts[-1].thought_signature == b"opaque-test-signature", assignment + " preserves opaque signature")
        require(sent[2].parts[0].function_response.id == "call_0", assignment + " returns matching function-call ID")
        require("PRIVATE_TEST_TRACE" not in json.dumps(result), assignment + " does not expose hidden thought text")
        require(result["history"][-1]["assistant"] == result["answer"], assignment + " stores completed turns")

        client = ScriptedClient([response("Please provide your email.")])
        next_result = runner("What else do you need?", result["history"], knowledge, client=client, log_root=logs)
        require(client.requests[0]["contents"][0].parts[0].text.startswith("Please record"), assignment + " reuses recent history")

        tools = module.make_tools(Path(logs) / "validation")
        bad = module.execute_tool("record_customer_interest", {"email": "bad", "name": "Alex", "message": "tutoring"}, tools, {})
        require(not bad["ok"], assignment + " rejects invalid email")
        require(not module.execute_tool("run_shell", {}, tools, {})["ok"], assignment + " rejects undeclared tools")
        require(not module.execute_tool("record_feedback", {"question": 5}, tools, {})["ok"], assignment + " validates argument types")
        seen = {}
        first = module.execute_tool("record_feedback", {"question": "Test feedback"}, tools, seen)
        second = module.execute_tool("record_feedback", {"question": "Test feedback"}, tools, seen)
        require(first["id"] == second["id"] and second["duplicate"], assignment + " deduplicates repeat writes within a turn")
        require(len((Path(logs) / "validation" / "feedback.jsonl").read_text().splitlines()) == 1, assignment + " no duplicate disk record")

        client = ScriptedClient([response(calls=[("record_customer_interest", {"email": "alex@example.com", "name": "Alex Demo", "message": "Code Clinic"})]), response("Please provide your email address.")])
        guarded = runner("Please register my interest in Code Clinic. My name is Alex Demo.", [], knowledge, client=client, log_root=logs)
        observations = [row['observation'] for row in guarded['trace'] if row['stage'] == 'action_observation']
        require(observations and not observations[0]['ok'], assignment + " rejects an email copied from worked examples")
        require(not list((Path(logs) / guarded['session_id']).glob('customer_interest.jsonl')), assignment + " no record written for invented contact details")

        client = ScriptedClient([response(calls=[("record_feedback", {"question": "Unknown policy"})]) for _ in range(5)])
        limited = runner("Unknown policy?", [], knowledge, client=client, log_root=logs)
        require(bool(limited["error"]) and len(client.requests) == 5, assignment + " bounds the action loop")
        require(not limited["history"], assignment + " incomplete request excluded from completed history")

        client = ScriptedClient([response("Partial", finish="MAX_TOKENS")])
        incomplete = runner("A question", [], knowledge, client=client, log_root=logs)
        require("output limit" in incomplete["error"], assignment + " does not label truncated answer complete")

        client = ScriptedClient([response("Original draft"), response("Revised reply")])
        reflected = runner("A question", [], knowledge, {"reflection": True}, client=client, log_root=logs)
        require(reflected["reflection"] == {"draft": "Original draft", "revised": "Revised reply"}, assignment + " reflection logs actual draft and revision")
        require(client.requests[-1]["config"].tools is None, assignment + " reflection cannot perform new tools")

        state = module.prepare_turn("new", [{"user": str(i), "assistant": "ok"} for i in range(10)], knowledge)
        require(state["history_omitted"] == 4, assignment + " trims whole old turns")

    app = module.build_app(assignment, client=ScriptedClient([response("Hello from the demo")]))
    require(any(type(block).__name__ == "ChatInterface" for block in app.blocks.values()) or bool(app.fns), assignment + " builds Gradio interface")
    reply_fn = inspect.unwrap(next(item.fn for item in app.fns.values() if getattr(item.fn, "__name__", "") == "chat_reply"))
    result = reply_fn("Hello", [], "Sheriff", False, True, "system", False, 0.4, 0.85, 32, 2048, module.MODEL, module.new_session())
    if inspect.isawaitable(result):
        result = asyncio.run(result)
    require(result[0] == "Hello from the demo" and len(result[1]["history"]) == 1, assignment + " interface invokes actual runner")
    reset_fn = next(item.fn for item in app.fns.values() if getattr(item.fn, "__name__", "") == "switch_persona")
    reset = reset_fn("Patch")
    if inspect.isawaitable(reset):
        reset = asyncio.run(reset)
    require(reset[6]["history"] == [] and reset[7] == [], assignment + " persona change resets both visible and model history")
    require(reset[10] == [] and reset[11] == [], assignment + " reset clears Gradio internal conversation states")
    require(module.history_to_turns([{'role':'user','content':[{'type':'text','text':'Earlier'}]}, {'role':'assistant','content':[{'type':'text','text':'Reply'}]}]) == [{'user':'Earlier','assistant':'Reply'}], assignment + " reads Gradio 6 structured text history")

summary = {"source": "offline_integration_tests", "passed": len(checks), "checks": checks,
           "limitation": "Scripted SDK responses verify application mechanics, not Gemini answer quality."}
(ROOT / "verification.json").write_text(json.dumps(summary, indent=2))
print("PASS", len(checks), "checks")
