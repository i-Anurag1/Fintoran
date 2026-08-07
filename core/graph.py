"""
Multi-Agent Orchestrator (LangGraph)
=====================================
A supervisor + specialist-agents graph:

                        User question
                              |
                              v
                       Supervisor node  <-------------------+
                    (decides: route to a                    |
                     specialist, or FINISH)                  |
                    /              \\                        |
                   v                v                        |
           Budget Agent       Market Agent                   |
       (finance_tools.py)   (market_tools.py)                |
                   \\              /                          |
                    \\            /                           |
                     +----------+  -- result appended --------+
                              |
                     Supervisor decides FINISH
                              |
                              v
                      Synthesize final answer
                              |
                              v
                            END

The supervisor can call either specialist multiple times in any order
(e.g. "should I buy AAPL or pay off my card" -> Market Agent for the price,
then Budget Agent for affordability, then synthesize) — nobody hardcodes
that sequence; the supervisor LLM decides it per-question via
structured-output routing.

Model choice
------------
Groq periodically retires models (see console.groq.com/docs/deprecations).
`llama-3.3-70b-versatile` — a common default in older tutorials/projects —
is one such model, scheduled for shutdown; requests to it can start
failing or degrading before the shutdown date. The default here is
`openai/gpt-oss-120b`, Groq's current-generation, actively supported
model with full tool-calling support. If GROQ_MODEL is set in the
environment to something else, that's used instead — but if IT starts
failing (deprecated/renamed/rate-limited), `MultiAgentOrchestrator`
automatically retries the same request against the next model in
MODEL_FALLBACK_CHAIN before giving up, so a single model going away
doesn't take the whole agent down.
"""
import os
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from core.agents import build_budget_agent, build_market_agent

MAX_SUPERVISOR_STEPS = 6

# First entry is what's actually used unless GROQ_MODEL overrides it; the
# rest are automatic fallbacks tried in order if a model call fails (e.g.
# because Groq has deprecated/removed it). Keep this list to models that
# support tool calling + structured output on Groq.
MODEL_FALLBACK_CHAIN = [
    os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"),
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
]
# De-duplicate while preserving order (in case GROQ_MODEL matches a fallback).
MODEL_FALLBACK_CHAIN = list(dict.fromkeys(MODEL_FALLBACK_CHAIN))

DEFAULT_MODEL = MODEL_FALLBACK_CHAIN[0]

SUPERVISOR_SYSTEM_TEMPLATE = """You are the Supervisor of a multi-agent personal financial assistant.

You have two specialist agents you can delegate to:
- budget_agent: everything about THIS USER's own transactions, spending,
  budgets, month-end forecasts, affordability of purchases, spending
  anomalies, and recurring payments/subscriptions.
- market_agent: live stock prices, analyst recommendations, and financial
  news search.

For each user question, decide which specialist(s) are needed, in what
order. Some questions need only one; some (e.g. "should I buy this stock or
pay off my card") need BOTH, in sequence, so you can reason across their
results. Route to one specialist at a time; you will be asked again after
each one responds, so you can chain further calls or finish.

Choose FINISH once you have everything needed to give the user a complete,
grounded answer.
{memory_context}
"""


class Route(BaseModel):
    next: Literal["budget_agent", "market_agent", "FINISH"] = Field(
        description="Which specialist to call next, or FINISH if ready to answer."
    )
    reasoning: str = Field(description="One short sentence on why.")


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    next: str
    steps: int
    trace: list


def _build_llm(api_key: str, model: str):
    return ChatGroq(api_key=api_key, model=model, temperature=0.2)


def build_graph(user_id: int, api_key: str, model: str, memory_context: str = ""):
    """Compiles a fresh supervisor graph for one request. Cheap enough to
    build per-call; avoids storing non-serializable LLM/tool objects in
    persisted graph state."""
    llm = _build_llm(api_key, model)
    router_llm = llm.with_structured_output(Route)

    budget_agent = build_budget_agent(llm, user_id)
    market_agent = build_market_agent(llm)

    system_prompt = SUPERVISOR_SYSTEM_TEMPLATE.format(
        memory_context=f"\n{memory_context}\n" if memory_context else ""
    )

    def supervisor_node(state: GraphState) -> dict:
        steps = state.get("steps", 0) + 1
        trace = list(state.get("trace", []))

        if steps > MAX_SUPERVISOR_STEPS:
            trace.append("Reached max supervisor steps — forcing FINISH")
            return {"next": "FINISH", "steps": steps, "trace": trace}

        try:
            route = router_llm.invoke(
                [SystemMessage(content=system_prompt)] + state["messages"]
            )
        except Exception as e:
            # A single malformed/failed routing call shouldn't kill the
            # whole conversation — fall back to answering directly with
            # whatever's in the conversation so far.
            trace.append(f"Routing failed ({e}) — finishing with what's available")
            return {"next": "FINISH", "steps": steps, "trace": trace}

        trace.append(f"Supervisor -> {route.next} ({route.reasoning})")
        return {"next": route.next, "steps": steps, "trace": trace}

    def budget_node(state: GraphState) -> dict:
        trace = list(state.get("trace", []))
        try:
            result = budget_agent.invoke({"messages": state["messages"]})
            new_messages = result["messages"][len(state["messages"]):]
            trace.append("Budget Agent handled its part")
            return {"messages": new_messages, "trace": trace}
        except Exception as e:
            trace.append(f"Budget Agent failed ({e})")
            return {
                "messages": [AIMessage(content=f"(Budget Agent could not complete its analysis: {e})")],
                "trace": trace,
            }

    def market_node(state: GraphState) -> dict:
        trace = list(state.get("trace", []))
        try:
            result = market_agent.invoke({"messages": state["messages"]})
            new_messages = result["messages"][len(state["messages"]):]
            trace.append("Market Agent handled its part")
            return {"messages": new_messages, "trace": trace}
        except Exception as e:
            trace.append(f"Market Agent failed ({e})")
            return {
                "messages": [AIMessage(content=f"(Market Agent could not complete its analysis: {e})")],
                "trace": trace,
            }

    def synthesize_node(state: GraphState) -> dict:
        synth_prompt = SystemMessage(content=(
            "Using the conversation and any specialist agent results above, "
            "give the user one final, clear, well-reasoned answer now. Be "
            "concise and specific, and give a direct recommendation if asked "
            "for one. If a specialist could not complete its analysis, "
            "acknowledge that plainly rather than inventing numbers."
        ))
        response = llm.invoke([synth_prompt] + state["messages"])
        trace = list(state.get("trace", [])) + ["Synthesized final answer"]
        return {"messages": [response], "trace": trace}

    def route_decision(state: GraphState) -> str:
        return state["next"]

    graph = StateGraph(GraphState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("budget_agent", budget_node)
    graph.add_node("market_agent", market_node)
    graph.add_node("synthesize", synthesize_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", route_decision, {
        "budget_agent": "budget_agent",
        "market_agent": "market_agent",
        "FINISH": "synthesize",
    })
    graph.add_edge("budget_agent", "supervisor")
    graph.add_edge("market_agent", "supervisor")
    graph.add_edge("synthesize", END)

    return graph.compile()


class MultiAgentOrchestrator:
    """Backed by the LangGraph supervisor graph above. run() returns
    {"answer": str, "trace": list}.

    If `model` isn't given, tries MODEL_FALLBACK_CHAIN in order — the first
    one that actually works for this request is used, so a single
    deprecated/renamed/rate-limited model doesn't take the whole agent
    down."""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.models_to_try = [model] if model else list(MODEL_FALLBACK_CHAIN)

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def run(self, user_id: int, user_message: str, conversation_history: list = None,
            memory_context: str = "") -> dict:
        if not self.is_configured():
            return {
                "answer": ("No GROQ_API_KEY configured, so the agent can't reason yet. "
                           "Set GROQ_API_KEY in your .env file — Groq's free tier is enough "
                           "for this whole project. See README for setup."),
                "trace": ["Agent not configured — missing API key"],
            }

        messages = []
        for turn in (conversation_history or []):
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            else:
                messages.append(AIMessage(content=turn["content"]))
        messages.append(HumanMessage(content=user_message))

        errors = []
        for model in self.models_to_try:
            try:
                graph = build_graph(user_id, self.api_key, model, memory_context)
                final_state = graph.invoke(
                    {"messages": messages, "next": "", "steps": 0,
                     "trace": [f'User asked: "{user_message}"', f"Using model: {model}"]},
                    config={"recursion_limit": (MAX_SUPERVISOR_STEPS + 1) * 4},
                )
            except Exception as e:
                errors.append(f"{model}: {e}")
                continue  # try the next model in the fallback chain

            final_message = final_state["messages"][-1]
            answer = getattr(final_message, "content", None) or (
                "I reasoned through several steps but couldn't reach a final "
                "answer in time. Try rephrasing your question."
            )
            trace = final_state.get("trace", [])
            if errors:
                trace = [f"Recovered after model fallback (tried: {', '.join(e.split(':')[0] for e in errors)})"] + trace
            return {"answer": answer, "trace": trace}

        # Every model in the chain failed.
        detail = " | ".join(errors)
        return {
            "answer": ("The agent couldn't reach any configured model right now "
                       f"({detail}). This is usually a Groq-side issue (an invalid/"
                       "expired API key, a deprecated model name, or a temporary "
                       "outage) rather than a bug in this app — check "
                       "console.groq.com and your GROQ_API_KEY, then try again."),
            "trace": [f"All models failed: {detail}"],
        }
