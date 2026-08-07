def test_add_and_retrieve_chat_turn(temp_chroma_dir):
    from memory.vector_memory import ConversationMemory

    mem = ConversationMemory(user_id=1)
    mem.add_chat_turn("user", "I'm saving up for a new laptop this year.")
    mem.add_chat_turn("assistant", "Got it, I'll factor that into affordability checks.")

    results = mem.retrieve_relevant("What am I saving for?", k=5)
    texts = [r["text"] for r in results]
    assert any("laptop" in t.lower() for t in texts)


def test_add_and_retrieve_preference(temp_chroma_dir):
    from memory.vector_memory import ConversationMemory

    mem = ConversationMemory(user_id=2)
    mem.add_preference("I want to cut down on food delivery spending.")

    results = mem.retrieve_relevant("food delivery habits", k=3, kinds=("preference",))
    assert len(results) == 1
    assert results[0]["kind"] == "preference"


def test_empty_memory_returns_no_results(temp_chroma_dir):
    from memory.vector_memory import ConversationMemory

    mem = ConversationMemory(user_id=3)
    assert mem.retrieve_relevant("anything") == []
    assert mem.get_context_string("anything") == ""


def test_get_context_string_formats_memories(temp_chroma_dir):
    from memory.vector_memory import ConversationMemory

    mem = ConversationMemory(user_id=4)
    mem.add_chat_turn("user", "My rent is 20000 rupees a month.")

    context = mem.get_context_string("rent amount")
    assert "Relevant memory" in context
    assert "20000" in context


def test_memory_is_isolated_per_user(temp_chroma_dir):
    from memory.vector_memory import ConversationMemory

    mem_a = ConversationMemory(user_id=10)
    mem_b = ConversationMemory(user_id=20)

    mem_a.add_chat_turn("user", "I drive a Tesla and love EVs.")

    results_b = mem_b.retrieve_relevant("What car do I drive?")
    assert results_b == []


def test_clear_wipes_memory(temp_chroma_dir):
    from memory.vector_memory import ConversationMemory

    mem = ConversationMemory(user_id=30)
    mem.add_chat_turn("user", "Something to remember.")
    assert mem.retrieve_relevant("Something to remember") != []

    mem.clear()
    assert mem.retrieve_relevant("Something to remember") == []
