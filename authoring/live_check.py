"""Run a small live check without ever printing credentials or raw API errors."""
import argparse
import importlib.util
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--assignment", default="C3", choices=["C3", "C4"])
parser.add_argument("--matrix", action="store_true")
parser.add_argument("--resume", action="store_true")
parser.add_argument("--delay", type=float, default=10)
parser.add_argument("--diagnose", action="store_true")
parser.add_argument("--model")
parser.add_argument("--final-regression", action="store_true")
args = parser.parse_args()
if args.model:
    os.environ['GEMINI_MODEL'] = args.model
folder = ROOT / args.assignment
os.chdir(folder)
spec = importlib.util.spec_from_file_location("byteclub_live", folder / "app.py")
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)
knowledge = app.load_business()
if args.final_regression:
    runner = app.run_c3 if args.assignment == 'C3' else app.run_c4
    history, rows = [], []
    session_id = app.uuid.uuid4().hex
    questions = ['Please register my interest in Code Clinic. My name is Alex Demo and I need help debugging a Python loop.',
                 'My email is alex@example.com. Please record my contact request.']
    for index, message in enumerate(questions):
        result = runner(message, history, knowledge, {'persona':'Patch'}, session_id=session_id)
        history = result['history']
        actions = [row for row in result['trace'] if row['stage']=='action_observation' and row['observation'].get('ok')]
        passed = not result['error'] and (not actions if index == 0 else any(row['tool']=='record_customer_interest' for row in actions))
        rows.append({'source':'live_gemini','scenario':'final_contact_provenance_and_memory','input':message,'passed':passed,**result})
        print('Regression',index+1,'passed:',passed,'answer:',result['answer'],flush=True)
        if result['error']:
            break
        app.time.sleep(6)
    (folder/'results'/'final_regression.json').write_text(json.dumps(rows,indent=2))
    if len(rows)!=2 or not all(row['passed'] for row in rows):
        raise SystemExit(1)
elif args.diagnose:
    state = app.prepare_turn('Please register my interest. I am Sam Demo and need Python tutoring, but have not provided an email.', [], knowledge, {'persona':'Patch','explain':True})
    try:
        app.model_step(state, app.make_client())
        print('Diagnostic request completed. Visible answer:',state['answer'])
    except Exception as error:
        message = str(getattr(error,'message',''))
        key = os.getenv('GEMINI_API_KEY','')
        if key:
            message = message.replace(key,'[REDACTED]')
        print('Provider error type:',type(error).__name__,'code:',getattr(error,'code',None),'message:',message[:500])
elif args.matrix:
    app.run_experiments(knowledge, repeats=1, delay=args.delay, resume=args.resume)
else:
    runner = app.run_c3 if args.assignment == "C3" else app.run_c4
    questions = ["How much is Python tutoring?",
                 "Please record my interest in Code Clinic. My name is Alex Demo and my email is alex@example.com. I need help debugging a loop; please have the team contact me."]
    rows = []
    for message in questions:
        result = runner(message, [], knowledge)
        rows.append({"source": "live_gemini", "input": message, **result})
        print(json.dumps({"answer": result["answer"], "error": result["error"], "trace": result["trace"]}, ensure_ascii=False), flush=True)
        if result["error"]:
            break
    (folder / "results").mkdir(exist_ok=True)
    (folder / "results" / "live_smoke.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
