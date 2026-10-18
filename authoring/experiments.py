# %% Controlled C4 experiments and honest result recording
EVALUATION_CASES = [
    {"id": "price", "message": "What is the price and duration of individual Python tutoring?",
     "route": "general", "tool": None, "required": ["25", "60|one.hour|1.hour"]},
    {"id": "pdf_policy", "message": "How much notice is needed for free rescheduling, and how many learners can join a group?",
     "route": "general", "tool": None, "required": ["24", "three|3"]},
    {"id": "complete_lead", "message": "Please record my interest in Code Clinic and have the team contact me. My name is Alex Demo, my email is alex@example.com, and I need help debugging a Python loop.",
     "route": "lead", "tool": "record_customer_interest", "required": []},
    {"id": "feedback", "message": "Feedback: I found the starter website pricing unclear.",
     "route": "feedback", "tool": "record_feedback", "required": []},
    {"id": "unknown", "message": "Do you offer an official Rust certification?",
     "route": "general", "tool": "record_feedback", "required": []},
    {"id": "missing_email", "message": "Please register my interest. I'm Sam Demo and need Python tutoring; I have not provided an email yet.",
     "route": "lead", "tool": None, "required": ["email"]},
]


def experiment_setups():
    # Start from Patch's preset. All ablations below change exactly one factor.
    base = resolve_settings({"persona": "Patch"})
    setups = [{"name": "patch_baseline", "settings": base}]
    variations = [
        ("explained_decision", {"explain": True}),
        ("zero_shot_ablation", {"few_shot": False}),
        ("instructions_in_message", {"instruction_location": "message"}),
        ("temperature_080", {"temperature": 0.8}),
        ("top_p_095", {"top_p": 0.95}),
        ("top_k_40", {"top_k": 40}),
    ]
    for name, change in variations:
        setups.append({"name": name, "settings": dict(base, **change)})
    # These comparisons test complete persona packages, so both wording and settings change.
    for persona in ["Sheriff", "Professor Pip"]:
        setups.append({"name": persona.lower().replace(" ", "_") + "_preset",
                       "settings": resolve_settings({"persona": persona})})
    return setups


def score_case(case, result):
    actions = [row for row in result["trace"] if row["stage"] == "action_observation"]
    successful = [row["tool"] for row in actions if row["observation"].get("ok")]
    expected = case["tool"]
    tool_ok = set(successful) == {expected} if expected else not actions
    terms_ok = all(re.search(term, result["answer"], flags=re.IGNORECASE) for term in case["required"])
    # These are narrow automatic checks, not a semantic or style quality score.
    checks = {"completed": not bool(result["error"]), "route_correct": result["route"] == case["route"],
              "tool_check": bool(tool_ok), "fact_terms_present": bool(terms_ok)}
    return checks


def run_experiments(knowledge, output="results/experiments.jsonl", repeats=1, delay=4,
                    setup_names=None, case_ids=None, client=None, resume=False):
    """REAL Gemini calls only. A full default run is 9 setups x 6 cases (54 turns)."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    client = client or make_client()
    rows = []
    existing = []
    if resume and output.exists():
        existing = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines() if line.strip()]
    batch = existing[-1]["batch"] if existing else datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    finished = {(row["setup"], row["case"], row["repeat"]) for row in existing if row["batch"] == batch and not row["error"]}
    for setup in experiment_setups():
        if setup_names and setup["name"] not in setup_names:
            continue
        for case in EVALUATION_CASES:
            if case_ids and case["id"] not in case_ids:
                continue
            for repeat in range(repeats):
                if (setup["name"], case["id"], repeat) in finished:
                    continue
                result = run_c4(case["message"], [], knowledge, setup["settings"],
                                log_root="logs/evaluation/" + batch, client=client)
                row = {"source": "live_gemini", "timestamp": datetime.now(timezone.utc).isoformat(),
                       "batch": batch, "setup": setup["name"], "case": case["id"], "repeat": repeat,
                       "input": case["message"], "checks": score_case(case, result), **result}
                with output.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(row, ensure_ascii=False) + "\n")
                rows.append(row)
                print(setup["name"], case["id"], row["checks"], str(result["seconds"]) + "s")
                if row["error"]:
                    print("Stopped the batch after an API/error result. Resume only after resolving it.")
                    return rows
                time.sleep(delay)
    return rows


def summarize_experiments(path="results/experiments.jsonl"):
    if not Path(path).exists():
        print("No live experiment file exists yet. Run the experiment cell after configuring Gemini.")
        return []
    rows = [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
    groups = {}
    for row in rows:
        group = groups.setdefault((row["batch"], row["setup"]), [])
        group.append(row)
    summary = []
    for (batch, setup), items in groups.items():
        latest = {}
        for item in items:
            latest[(item["case"], item["repeat"])] = item
        effective = list(latest.values())
        passed = sum(all(item["checks"].values()) for item in effective)
        summary.append({"batch": batch, "setup": setup, "turns": len(effective), "attempts": len(items),
                        "recorded_errors": sum(bool(item["error"]) for item in items),
                        "all_checks_passed": passed,
                        "mean_seconds": round(sum(item["seconds"] for item in effective) / len(effective), 2),
                        "total_tokens": sum(item["total_tokens"] for item in items)})
    for row in summary:
        print(row)
    return summary
