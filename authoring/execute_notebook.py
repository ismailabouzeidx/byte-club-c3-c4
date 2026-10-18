"""Execute actual notebook cells in a fresh kernel, retaining their real outputs."""
import argparse
import os
from pathlib import Path
import nbformat
from nbclient import NotebookClient

parser = argparse.ArgumentParser()
parser.add_argument("--assignment", choices=["C3", "C4"], required=True)
parser.add_argument("--live-demo", action="store_true")
parser.add_argument("--model", default="gemini-3.5-flash-lite")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
folder = root / args.assignment
path = folder / ("business_agent.ipynb" if args.assignment == "C3" else "react_agent.ipynb")
os.environ["JUPYTER_PATH"] = "/tmp/byteclub-kernels/share/jupyter"
os.environ["JUPYTER_RUNTIME_DIR"] = "/tmp/byteclub-jupyter-runtime"
os.environ["IPYTHONDIR"] = "/tmp/byteclub-ipython"
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["GEMINI_MODEL"] = args.model
if args.live_demo:
    os.environ["BYTECLUB_LIVE_DEMO"] = "1"
nb = nbformat.read(path, as_version=4)
for cell in nb.cells:
    if cell.cell_type == "code" and (cell.source.startswith("%pip") or "app.launch(" in cell.source):
        cell.metadata["tags"] = ["skip-verify"]
client = NotebookClient(nb, timeout=180, kernel_name="byteclub", skip_cells_with_tag="skip-verify",
                        resources={"metadata": {"path": str(folder)}})
client.execute()
for cell in nb.cells:
    cell.metadata.pop("tags", None)
nbformat.validate(nb)
nbformat.write(nb, path)
print(args.assignment, "notebook executed; installation and public launch excluded.", flush=True)
print("Executed cells:",sum(c.cell_type == "code" and c.execution_count is not None for c in nb.cells))
