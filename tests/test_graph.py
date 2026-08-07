"""
These tests mock out the LLM and specialist sub-agents entirely (no network,
no API key needed) so we're testing the SUPERVISOR'S GRAPH WIRING —
routing, handoffs, iteration capping, and final-answer synthesis — not the
LLM's judgement.
"""
from langchain_core.messages import AIMessage, HumanMessage

import core.graph as graph_mod
from core.graph import Route, MultiAgentOrchestrator


class FakeRouterLLM:
    """Returned by FakeLLM.with_structured_output(Route); yields a scripted
    sequence of routing decisions, one per call."""
    def __init__(self, routes):
        self._routes = list(routes)

    def invoke(self, messages):
        if not self._routes:
            return Route(next="FINISH", reasoning="fallback")
        return self._routes.pop(0)


class FakeLLM:
    def __init__(self, routes, final_answer="Final synthesized answer."):
        self._routes = routes
        self._final_answer = final_answer

    def with_structured_output(self, schema):
        return FakeRouterLLM(self._routes)

    def invoke(self, messages):
        return AIMessage(content=self._final_answer)


class FakeSubAgent:
    def __init__(self, reply_text):
        self._reply_text = reply_text

    def invoke(self, state):
        new_messages = list(state["messages"]) + [AIMessage(content=self._reply_text)]
        return {"messages": new_messages}


def _patch_graph_dependencies(monkeypatch, routes, budget_reply="budget result", market_reply="market result",
                               final_answer="Final synthesized answer."):
    fake_llm = FakeLLM(routes, final_answer=final_answer)
    monkeypatch.setattr(graph_mod, "_build_llm", lambda api_key, model: fake_llm)
    monkeypatch.setattr(graph_mod, "build_budget_agent", lambda llm, user_id: FakeSubAgent(budget_reply))
    monkeypatch.setattr(graph_mod, "build_market_agent", lambda llm: FakeSubAgent(market_reply))


def test_single_agent_route_then_finish(monkeypatch):
    routes = [Route(next="budget_agent", reasoning="needs budget data"),
              Route(next="FINISH", reasoning="done")]
    _patch_graph_dependencies(monkeypatch, routes)

    compiled = graph_mod.build_graph(user_id=1, api_key="fake", model="fake-model")
    state = compiled.invoke({
        "messages": [HumanMessage(content="Am I overspending on food?")],
        "next": "", "steps": 0, "trace": [],
    })

    assert state["messages"][-1].content == "Final synthesized answer."
    assert any("budget_agent" in t for t in state["trace"])
    assert any("Budget Agent handled" in t for t in state["trace"])


def test_chains_both_agents_in_order(monkeypatch):
    routes = [
        Route(next="market_agent", reasoning="check stock price first"),
        Route(next="budget_agent", reasoning="now check affordability"),
        Route(next="FINISH", reasoning="ready to answer"),
    ]
    _patch_graph_dependencies(monkeypatch, routes)

    compiled = graph_mod.build_graph(user_id=1, api_key="fake", model="fake-model")
    state = compiled.invoke({
        "messages": [HumanMessage(content="Should I buy AAPL or pay off my card?")],
        "next": "", "steps": 0, "trace": [],
    }, config={"recursion_limit": 50})

    trace_text = " ".join(state["trace"])
    assert "market_agent" in trace_text
    assert "budget_agent" in trace_text
    assert trace_text.index("market_agent") < trace_text.index("budget_agent")


def test_max_supervisor_steps_forces_finish(monkeypatch):
    # Router always says to keep routing to budget_agent — should be capped.
    infinite_routes = [Route(next="budget_agent", reasoning="loop") for _ in range(50)]
    _patch_graph_dependencies(monkeypatch, infinite_routes)

    compiled = graph_mod.build_graph(user_id=1, api_key="fake", model="fake-model")
    state = compiled.invoke({
        "messages": [HumanMessage(content="Keep going forever")],
        "next": "", "steps": 0, "trace": [],
    }, config={"recursion_limit": 100})

    assert any("max supervisor steps" in t.lower() for t in state["trace"])
    assert state["messages"][-1].content == "Final synthesized answer."


def test_orchestrator_returns_configured_message_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    orchestrator = MultiAgentOrchestrator(api_key=None)
    assert not orchestrator.is_configured()

    result = orchestrator.run(user_id=1, user_message="hi")
    assert "GROQ_API_KEY" in result["answer"]


def test_orchestrator_run_end_to_end_with_mocks(monkeypatch):
    routes = [Route(next="FINISH", reasoning="simple question")]
    _patch_graph_dependencies(monkeypatch, routes, final_answer="You're doing fine.")

    orchestrator = MultiAgentOrchestrator(api_key="fake-key")
    result = orchestrator.run(user_id=1, user_message="Am I doing okay financially?")

    assert result["answer"] == "You're doing fine."
    assert any("User asked" in t for t in result["trace"])
