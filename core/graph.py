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
from providers.resilience import retry_call

from core.agents import build_budget_agent, build_market_agent, build_analytics_agent, build_document_agent

MAX_SUPERVISOR_STEPS = int(os.environ.get("MAX_SUPERVISOR_STEPS", "6"))

# First entry is what's actually used unless GROQ_MODEL overrides it; the
# rest are automatic fallbacks tried in order if a model call fails (e.g.
# because Groq has deprecated/removed it). Keep this list to models that
# support tool calling + structured output on Groq.
_configured_fallbacks = [x.strip() for x in os.environ.get("GROQ_FALLBACK_MODELS", "").split(",") if x.strip()]
MODEL_FALLBACK_CHAIN = [os.environ.get("GROQ_MODEL", "openai/gpt-oss-120b"), *_configured_fallbacks, "openai/gpt-oss-20b", "llama-3.3-70b-versatile"]
MODEL_FALLBACK_CHAIN = list(dict.fromkeys(MODEL_FALLBACK_CHAIN))

DEFAULT_MODEL = MODEL_FALLBACK_CHAIN[0]

SUPERVISOR_SYSTEM_TEMPLATE = """You are the Supervisor of a multi-agent personal financial assistant.

You have four specialist agents you can delegate to:
- budget_agent: everything about THIS USER's own transactions, spending,
  budgets, month-end forecasts, affordability of purchases, spending
  anomalies, and recurring payments/subscriptions.
- market_agent: live stock prices, analyst recommendations, and financial
  news search.
- analytics_agent: deterministic financial overview, forecast comparison,
  anomaly explanations, and scenario analysis.
- document_agent: retrieval over this user's uploaded documents with citations.

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
    next: Literal["budget_agent", "market_agent", "analytics_agent", "document_agent", "FINISH"] = Field(description="Which specialist to call next, or FINISH if ready to answer.")
    reasoning: str = Field(default="", description="One short sentence on why.")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    tool_plan: list[str] = Field(default_factory=list)


class FinalAnswerMetadata(BaseModel):
    answer_type: Literal["grounded_finance", "market_research", "document_rag", "mixed", "unavailable"]
    sources: list[str] = Field(default_factory=list)
    uncertainty: str = ""
    deterministic_data_used: bool = False


class GraphState(TypedDict):
    messages: Annotated[list, add_messages]
    next: str
    steps: int
    trace: list
    final_metadata: dict


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
    analytics_agent = None
    document_agent = None

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
            route = retry_call(
                lambda: router_llm.invoke([SystemMessage(content=system_prompt)] + state["messages"]),
                attempts=int(os.environ.get("LLM_RETRY_ATTEMPTS", "2")),
                base_delay=float(os.environ.get("LLM_RETRY_BASE_DELAY", "0.5")),
            )
        except Exception as e:
            # A single malformed/failed routing call shouldn't kill the
            # whole conversation — fall back to answering directly with
            # whatever's in the conversation so far.
            trace.append("Routing failed; finishing with available evidence")
            return {"next": "FINISH", "steps": steps, "trace": trace}

        trace.append(f"Supervisor -> {route.next} ({route.reasoning})")
        if route.tool_plan:
            trace.append("Tool plan: " + ", ".join(route.tool_plan[:8]))
        return {"next": route.next, "steps": steps, "trace": trace}

    def budget_node(state: GraphState) -> dict:
        trace = list(state.get("trace", []))
        try:
            result = budget_agent.invoke({"messages": state["messages"]})
            new_messages = result["messages"][len(state["messages"]):]
            trace.append("Budget Agent handled its part")
            return {"messages": new_messages, "trace": trace}
        except Exception as e:
            trace.append("Budget Agent failed; no unsupported numbers were added")
            return {
                "messages": [AIMessage(content="(Budget Agent could not complete its analysis right now.)")],
                "trace": trace,
            }

    def analytics_node(state: GraphState) -> dict:
        nonlocal analytics_agent
        trace = list(state.get("trace", []))
        try:
            if analytics_agent is None:
                analytics_agent = build_analytics_agent(llm, user_id)
            result = analytics_agent.invoke({"messages": state["messages"]})
            new_messages = result["messages"][len(state["messages"]):]
            trace.append("Analytics Agent handled its part")
            return {"messages": new_messages, "trace": trace}
        except Exception:
            trace.append("Analytics Agent unavailable; continuing without fabricated analytics")
            return {"messages": [AIMessage(content="Analytics data is unavailable right now.")], "trace": trace}

    def document_node(state: GraphState) -> dict:
        nonlocal document_agent
        trace = list(state.get("trace", []))
        try:
            if document_agent is None:
                document_agent = build_document_agent(llm, user_id)
            result = document_agent.invoke({"messages": state["messages"]})
            new_messages = result["messages"][len(state["messages"]):]
            trace.append("Document/RAG Agent handled its part")
            return {"messages": new_messages, "trace": trace}
        except Exception:
            trace.append("Document/RAG Agent unavailable; no unsupported document claims returned")
            return {"messages": [AIMessage(content="Document retrieval is unavailable right now.")], "trace": trace}

    def market_node(state: GraphState) -> dict:
        trace = list(state.get("trace", []))
        try:
            result = market_agent.invoke({"messages": state["messages"]})
            new_messages = result["messages"][len(state["messages"]):]
            trace.append("Market Agent handled its part")
            return {"messages": new_messages, "trace": trace}
        except Exception as e:
            trace.append("Market Agent failed; no unsupported market data was added")
            return {
                "messages": [AIMessage(content="(Market Agent could not complete its analysis right now.)")],
                "trace": trace,
            }

    def synthesize_node(state: GraphState) -> dict:
        synth_prompt = SystemMessage(content=(
            "Using the conversation and specialist results above, return one clear answer. "
            "Treat tool results as the source of truth for financial numbers. "
            "Never invent balances, totals, dates, prices, forecasts, citations, or document facts. "
            "For market information, distinguish live data, historical data, retrieved sources, and interpretation. "
            "For investment questions, provide sourced information and uncertainty rather than unsupported certainty. "
            "If a provider or specialist failed, state the limitation without exposing exception details."
        ))
        response = retry_call(
            lambda: llm.invoke([synth_prompt] + state["messages"]),
            attempts=int(os.environ.get("LLM_RETRY_ATTEMPTS", "2")),
            base_delay=float(os.environ.get("LLM_RETRY_BASE_DELAY", "0.5")),
        )
        trace = list(state.get("trace", [])) + ["Synthesized final answer"]
        content = getattr(response, "content", "") or ""
        lowered = content.lower()
        if "document" in lowered or "filing" in lowered:
            answer_type = "document_rag"
        elif any(word in lowered for word in ("stock", "share price", "market", "ticker")):
            answer_type = "market_research"
        elif any(word in lowered for word in ("spending", "budget", "transaction", "balance", "forecast")):
            answer_type = "grounded_finance"
        else:
            answer_type = "mixed"
        metadata = FinalAnswerMetadata(
            answer_type=answer_type,
            sources=[x for x in trace if "Agent" in x or "Supervisor" in x][-12:],
            uncertainty="External data and model interpretation depend on provider freshness and availability.",
            deterministic_data_used=any(x in " ".join(trace).lower() for x in ("budget", "analytics", "transaction")),
        ).model_dump()
        return {"messages": [response], "trace": trace, "final_metadata": metadata}

    def route_decision(state: GraphState) -> str:
        return state["next"]

    graph = StateGraph(GraphState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("budget_agent", budget_node)
    graph.add_node("market_agent", market_node)
    graph.add_node("analytics_agent", analytics_node)
    graph.add_node("document_agent", document_node)
    graph.add_node("synthesize", synthesize_node)

    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", route_decision, {
        "budget_agent": "budget_agent",
        "market_agent": "market_agent",
        "analytics_agent": "analytics_agent",
        "document_agent": "document_agent",
        "FINISH": "synthesize",
    })
    graph.add_edge("budget_agent", "supervisor")
    graph.add_edge("market_agent", "supervisor")
    graph.add_edge("analytics_agent", "supervisor")
    graph.add_edge("document_agent", "supervisor")
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
                "agent_run_id": None,
            }

        messages = []
        for turn in (conversation_history or []):
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            else:
                messages.append(AIMessage(content=turn["content"]))
        messages.append(HumanMessage(content=user_message))

        from observability.logging import new_correlation_id, get_logger, event, Timer
        logger = get_logger()
        run_id = new_correlation_id()
        errors = []
        for model in self.models_to_try:
            try:
                event(logger, "agent_run_started", agent_run_id=run_id, user_id=user_id, model=model)
                graph = build_graph(user_id, self.api_key, model, memory_context)
                final_state = graph.invoke(
                    {"messages": messages, "next": "", "steps": 0,
                     "trace": [f'User asked: "{user_message}"', f"Using model: {model}"], "final_metadata": {}},
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
            event(logger, "agent_run_completed", agent_run_id=run_id, user_id=user_id, model=model)
            return {"answer": answer, "trace": trace, "agent_run_id": run_id, "final_metadata": final_state.get("final_metadata", {})}

        # Every model in the chain failed.
        return {
            "answer": ("The agent is unavailable right now. No model returned a usable response. "
                       "Check the configured model/API settings and try again."),
            "trace": ["All configured models failed; provider details were withheld from the user"],
            "agent_run_id": run_id,
            "final_metadata": {"answer_type": "unavailable", "sources": [], "uncertainty": "Model provider unavailable.", "deterministic_data_used": False},
        }
