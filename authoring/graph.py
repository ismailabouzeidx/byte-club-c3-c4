# %% C4: define the graph state and write the ReAct loop ourselves
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


class ReActState(TypedDict):
    turn: dict


def build_react_graph(client):
    """Only LangGraph's state/edge primitives; no prebuilt executor or ToolNode."""
    def think(state):
        turn = state["turn"]
        try:
            model_step(turn, client)
        except Exception as error:
            safe_failure(turn, error)
        return {"turn": turn}

    def act_and_observe(state):
        turn = state["turn"]
        try:
            action_step(turn)
        except Exception as error:
            safe_failure(turn, error)
        return {"turn": turn}

    def choose_next(state):
        turn = state["turn"]
        if turn["error"] or turn["answer"]:
            return "finish"
        if turn["steps"] >= MAX_MODEL_STEPS:
            turn["error"] = "The agent reached its five-step limit. Completed tool receipts remain valid."
            turn["answer"] = "I reached the action limit before completing an answer. Please simplify the request."
            return "finish"
        if turn["pending"]:
            return "act"
        return "finish"

    def finish(state):
        turn = state["turn"]
        if not turn["error"]:
            try:
                reflection_step(turn, client)
            except Exception as error:
                safe_failure(turn, error)
        turn["trace"].append({"stage": "final", "error": bool(turn["error"])})
        return {"turn": turn}

    graph = StateGraph(ReActState)
    graph.add_node("think", think)
    graph.add_node("act_and_observe", act_and_observe)
    graph.add_node("finish", finish)
    graph.add_edge(START, "think")
    graph.add_conditional_edges("think", choose_next, {"act": "act_and_observe", "finish": "finish"})
    graph.add_edge("act_and_observe", "think")
    graph.add_edge("finish", END)
    return graph.compile()


def run_c4(message, history, knowledge, settings=None, session_id=None, log_root="logs", client=None):
    turn = prepare_turn(message, history, knowledge, settings, session_id, log_root)
    try:
        client = client or make_client()
        graph = build_react_graph(client)
        result = graph.invoke({"turn": turn}, config={"recursion_limit": 20})
        return turn_result(result["turn"])
    except Exception as error:
        return safe_failure(turn, error)


REACT_DIAGRAM = """graph TD
    START --> think
    think -->|model requests action| act_and_observe
    act_and_observe -->|tool result returned to model| think
    think -->|answer, error, or step limit| finish
    finish --> END
"""

